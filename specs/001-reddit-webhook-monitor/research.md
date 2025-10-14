# Technical Research: Reddit Monitoring and Webhook Delivery System

**Date**: 2025-10-15
**Feature**: 001-reddit-webhook-monitor

## Overview

This document resolves the "NEEDS CLARIFICATION" items from the Technical Context, specifically around primary dependencies for Reddit API, translation services, and webhook delivery.

## Research Areas

### 1. Reddit API Library

**Decision**: PRAW (Python Reddit API Wrapper)

**Rationale**:
- Official, well-maintained Python wrapper for Reddit API
- Comprehensive documentation and active community
- Built-in rate limiting and authentication handling
- Supports both OAuth and read-only access
- Stable release (v7.7.1 as of 2024)
- Handles subreddit streaming and post fetching efficiently

**Alternatives Considered**:
- **asyncpraw**: Async version of PRAW
  - Rejected: Unnecessary complexity for initial MVP; synchronous polling sufficient for 5-minute intervals
- **Raw Reddit API (requests library)**: Direct HTTP calls
  - Rejected: Requires manual rate limiting, authentication, and pagination handling
- **pushshift.io**: Reddit archive service
  - Rejected: Service deprecated in 2023, unreliable

**Implementation Notes**:
- Use read-only OAuth for better rate limits (60 requests/minute)
- Implement exponential backoff for rate limit errors
- Cache subreddit objects to reduce API calls

**Best Practices**:
```python
import praw

reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="reddit-deliver/0.1.0"
)

# Get new posts from subreddit
subreddit = reddit.subreddit("ClaudeAI")
for post in subreddit.new(limit=25):
    # Process post
    pass
```

### 2. Translation Service

**Decision**: DeepL API (Free tier)

**Rationale**:
- Superior translation quality compared to Google Translate (based on benchmarks)
- Free tier: 500,000 characters/month (sufficient for MVP)
- Supports 31 languages including Korean, Japanese, Chinese
- Simple REST API with official Python client
- Lower cost than OpenAI for translation-only tasks
- Faster than OpenAI for batch translations

**Alternatives Considered**:
- **Google Cloud Translation API**:
  - Pros: More languages (133), better docs
  - Cons: No free tier, more expensive ($20/1M chars vs DeepL $5.49/1M)
  - Rejected: Cost concern for MVP, DeepL quality better for common languages
- **OpenAI GPT-4 Translation**:
  - Pros: Best quality, can handle context/tone
  - Cons: Expensive ($0.03/1K tokens ~= $60/1M chars), slower latency
  - Rejected: Overkill for simple post translation, cost prohibitive
- **LibreTranslate (self-hosted)**:
  - Pros: Free, open-source, self-hosted
  - Cons: Lower quality, requires infrastructure, slower
  - Rejected: Quality concerns, operational overhead

**Implementation Notes**:
- Use official `deepl` Python package
- Implement caching to avoid re-translating same content
- Fall back to original text if translation fails
- Detect source language automatically

**Best Practices**:
```python
import deepl

translator = deepl.Translator("YOUR_AUTH_KEY")
result = translator.translate_text(
    "Hello, world!",
    target_lang="KO"  # Korean
)
print(result.text)
```

**Fallback Strategy**: If DeepL quota exhausted, log error and send original English text with note "[Translation unavailable]"

### 3. Webhook Delivery

**Decision**: `requests` library with custom formatters

**Rationale**:
- Discord and Slack both use simple POST webhooks
- No need for heavy SDK overhead
- Easy to format JSON payloads per platform specs
- Built into Python standard ecosystem
- More control over retry logic and error handling

**Alternatives Considered**:
- **discord.py**: Full Discord bot framework
  - Rejected: Overkill for webhook-only usage, adds unnecessary complexity
- **slack-sdk**: Official Slack SDK
  - Pros: Typed objects, built-in retry
  - Cons: Heavy dependency, unnecessary features
  - Rejected: Simple webhook POST doesn't justify SDK weight
- **webhooks library**: Generic webhook sender
  - Rejected: Minimal benefit over direct `requests` usage

**Implementation Notes**:

**Discord Webhook Format**:
```python
import requests

payload = {
    "content": f"**New post in r/ClaudeAI**",
    "embeds": [{
        "title": translated_title,
        "description": translated_content[:2000],  # Discord 2048 char limit
        "url": post_url,
        "color": 5814783,  # Blue
        "footer": {"text": f"Posted by u/{author}"}
    }]
}

response = requests.post(discord_webhook_url, json=payload)
```

**Slack Webhook Format**:
```python
payload = {
    "text": f"*New post in r/ClaudeAI*",
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*<{post_url}|{translated_title}>*\n{translated_content[:3000]}"
            }
        }
    ]
}

response = requests.post(slack_webhook_url, json=payload)
```

**Best Practices**:
- Implement retry logic with exponential backoff (max 3 retries)
- Validate webhook URL format before sending
- Truncate content to platform limits (Discord: 2048, Slack: 3000)
- Log all webhook attempts and responses
- Handle 429 (rate limit) errors gracefully

### 4. Database Management

**Decision**: SQLAlchemy ORM with SQLite

**Rationale**:
- SQLAlchemy provides ORM abstraction (easier migrations later)
- Type-safe model definitions
- Easy to upgrade to PostgreSQL/MySQL if needed
- Built-in connection pooling
- Migration support via Alembic

**Alternatives Considered**:
- **Raw SQLite with sqlite3 module**:
  - Rejected: Manual SQL error-prone, no migration support
- **Peewee**: Lightweight ORM
  - Rejected: Less mature, smaller community
- **TinyDB**: JSON-based database
  - Rejected: No relational queries, not suitable for tracking relationships

**Best Practices**:
```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Post(Base):
    __tablename__ = 'posts'

    id = Column(String, primary_key=True)
    subreddit = Column(String, nullable=False)
    title = Column(String, nullable=False)
    created_utc = Column(DateTime, nullable=False)
    processed = Column(Integer, default=0)

engine = create_engine('sqlite:///data/reddit-deliver.db')
Base.metadata.create_all(engine)
```

### 5. Background Monitoring

**Decision**: APScheduler (Advanced Python Scheduler)

**Rationale**:
- Robust job scheduling in Python
- Supports interval-based jobs (check every 5 minutes)
- Thread-safe, handles multiple monitors concurrently
- Persistent job store support
- Better than cron for Python-based solution

**Alternatives Considered**:
- **Celery**: Distributed task queue
  - Rejected: Requires Redis/RabbitMQ broker, overkill for single-process MVP
- **cron + shell script**: System-level scheduling
  - Rejected: Less portable, harder to manage from Python
- **while True + time.sleep()**: Manual loop
  - Rejected: Primitive, no graceful shutdown, poor error handling

**Best Practices**:
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def check_subreddit(subreddit_name):
    # Monitoring logic
    pass

# Check every 5 minutes
scheduler.add_job(
    check_subreddit,
    'interval',
    minutes=5,
    args=['ClaudeAI']
)

scheduler.start()
```

### 6. Configuration Management

**Decision**: YAML config file + Pydantic validation

**Rationale**:
- Human-readable YAML format
- Pydantic provides type validation and defaults
- Easy to document config options
- Environment variable override support

**Best Practices**:
```python
from pydantic import BaseModel, HttpUrl
from typing import List
import yaml

class Config(BaseModel):
    target_language: str = "ko"
    poll_interval_minutes: int = 5
    subreddits: List[str] = []
    discord_webhook: HttpUrl = None
    slack_webhook: HttpUrl = None
    deepl_api_key: str = None

# Load and validate
with open("config/config.yaml") as f:
    config_data = yaml.safe_load(f)
    config = Config(**config_data)
```

## Dependency Summary

**Final dependency list for `requirements.txt`**:
```
praw>=7.7.0
deepl>=1.16.0
requests>=2.31.0
sqlalchemy>=2.0.0
apscheduler>=3.10.0
pydantic>=2.5.0
pyyaml>=6.0.0
```

**Development dependencies**:
```
pytest>=7.4.0
pytest-mock>=3.12.0
responses>=0.24.0  # For mocking HTTP requests
freezegun>=1.4.0   # For time-based testing
```

## Risk Mitigation

### Reddit API Rate Limits
- **Risk**: Exceeding 60 requests/minute rate limit
- **Mitigation**:
  - Implement request throttling
  - Cache subreddit data
  - Use conditional requests (If-Modified-Since headers)
  - Monitor rate limit headers in responses

### Translation API Quota
- **Risk**: Exceeding DeepL free tier (500k chars/month)
- **Mitigation**:
  - Cache translations in database
  - Truncate very long posts (keep first 1000 chars)
  - Monitor usage via logs
  - Fallback to untranslated text with notice

### Webhook Failures
- **Risk**: Discord/Slack webhook unavailable or rate-limited
- **Mitigation**:
  - Retry with exponential backoff (3 attempts)
  - Queue failed deliveries for later retry
  - Log all failures for debugging
  - User notification if webhook persistently fails

### Duplicate Post Detection
- **Risk**: Sending same post multiple times
- **Mitigation**:
  - Store post IDs in database with unique constraint
  - Check existence before processing
  - Use Reddit post ID as primary key

## Performance Considerations

**Expected Load** (10 subreddits, 5-min polling):
- Reddit API calls: 12/hour × 10 subreddits = 120 calls/hour (well under 3600/hour limit)
- Translation API: ~10 new posts/day × 500 chars avg = 5k chars/day = 150k/month (well under 500k limit)
- Database growth: ~300 posts/month × 1KB = 300KB/month (negligible)

**Bottlenecks**:
- Translation API latency (~1-2s per request): Process translations concurrently
- Database writes: Use batch inserts where possible

## Security Considerations

**API Keys**:
- Store in environment variables, NOT in config.yaml committed to git
- Use `.env` file (git-ignored) for local development
- Document required env vars in README

**Webhook URLs**:
- Validate URL format before storage
- Redact URLs in logs (show only domain)
- No authentication required (webhook URLs are secrets themselves)

## Next Steps

All "NEEDS CLARIFICATION" items resolved. Ready to proceed to Phase 1:
- Create data-model.md with entity schemas
- Generate API contracts (CLI interface specifications)
- Create quickstart.md with setup instructions
