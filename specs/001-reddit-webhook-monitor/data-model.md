# Data Model: Reddit Monitoring and Webhook Delivery System

**Feature**: 001-reddit-webhook-monitor
**Date**: 2025-10-15

## Overview

This document defines the data entities and their relationships for the Reddit monitoring system. The model uses SQLAlchemy ORM with SQLite backend.

## Entity Relationship Diagram

```
┌─────────────────┐
│  UserConfig     │ 1
│                 │
│ - id (PK)       │
│ - language      │
│ - poll_interval │
│ - created_at    │
└─────────────────┘
         │
         │ 1
         │
         │ *
┌─────────────────┐           ┌──────────────────┐
│  Subreddit      │           │  WebhookConfig   │
│                 │           │                  │
│ - id (PK)       │           │ - id (PK)        │
│ - name          │           │ - type           │
│ - url           │           │ - webhook_url    │
│ - enabled       │           │ - enabled        │
│ - last_check    │           │ - created_at     │
│ - created_at    │           │ - updated_at     │
└─────────────────┘           └──────────────────┘
         │
         │ 1
         │
         │ *
┌─────────────────────────┐
│  Post                   │
│                         │
│ - id (PK, reddit_id)    │
│ - subreddit_id (FK)     │
│ - title                 │
│ - content               │
│ - author                │
│ - url                   │
│ - created_utc           │
│ - processed             │
│ - processed_at          │
│ - retry_count           │
└─────────────────────────┘
         │
         │ 1
         │
         │ *
┌─────────────────────────┐
│  Translation            │
│                         │
│ - id (PK)               │
│ - post_id (FK)          │
│ - source_lang           │
│ - target_lang           │
│ - translated_title      │
│ - translated_content    │
│ - created_at            │
└─────────────────────────┘
```

## Entity Definitions

### 1. UserConfig

Stores global user configuration settings.

**SQLAlchemy Model**:
```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class UserConfig(Base):
    __tablename__ = 'user_config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    language = Column(String(10), nullable=False, default='en')  # ISO 639-1 code
    poll_interval_minutes = Column(Integer, nullable=False, default=5)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Fields**:
- `id`: Primary key
- `language`: Target language for translations (e.g., 'ko', 'ja', 'en')
- `poll_interval_minutes`: How often to check subreddits (default: 5 minutes)
- `created_at`: When config was first created
- `updated_at`: Last modification timestamp

**Validation Rules**:
- Language must be valid ISO 639-1 code supported by DeepL
- Poll interval must be >= 1 minute (avoid rate limit issues)
- Only one config row should exist (singleton pattern)

**Sample Data**:
```json
{
  "id": 1,
  "language": "ko",
  "poll_interval_minutes": 5,
  "created_at": "2025-10-15T10:00:00Z",
  "updated_at": "2025-10-15T10:00:00Z"
}
```

### 2. Subreddit

Represents a subreddit to monitor for new posts.

**SQLAlchemy Model**:
```python
class Subreddit(Base):
    __tablename__ = 'subreddits'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)  # e.g., 'ClaudeAI'
    url = Column(String(500), nullable=False)  # Full Reddit URL
    enabled = Column(Integer, nullable=False, default=1)  # SQLite boolean: 1=True, 0=False
    last_checked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship
    posts = relationship('Post', back_populates='subreddit', cascade='all, delete-orphan')
```

**Fields**:
- `id`: Primary key
- `name`: Subreddit name (e.g., 'ClaudeAI', 'Python')
- `url`: Full Reddit URL (e.g., 'https://www.reddit.com/r/ClaudeAI/')
- `enabled`: Whether to actively monitor (1=yes, 0=no)
- `last_checked_at`: Timestamp of last successful check
- `created_at`: When subreddit was added

**Validation Rules**:
- Name must match pattern: `^[A-Za-z0-9_]{3,21}$` (Reddit subreddit rules)
- URL must match pattern: `^https://www\.reddit\.com/r/[A-Za-z0-9_]+/?$`
- Name must be unique across all subreddits

**Sample Data**:
```json
{
  "id": 1,
  "name": "ClaudeAI",
  "url": "https://www.reddit.com/r/ClaudeAI/",
  "enabled": 1,
  "last_checked_at": "2025-10-15T10:30:00Z",
  "created_at": "2025-10-15T10:00:00Z"
}
```

### 3. WebhookConfig

Stores webhook destination configuration (Discord or Slack).

**SQLAlchemy Model**:
```python
class WebhookConfig(Base):
    __tablename__ = 'webhook_config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(20), nullable=False)  # 'discord' or 'slack'
    webhook_url = Column(String(500), nullable=False)
    enabled = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Fields**:
- `id`: Primary key
- `type`: Webhook type ('discord' or 'slack')
- `webhook_url`: Full webhook URL (contains secret token)
- `enabled`: Whether webhook is active
- `created_at`: When webhook was configured
- `updated_at`: Last modification timestamp

**Validation Rules**:
- Type must be either 'discord' or 'slack'
- Discord URL must match: `^https://discord\.com/api/webhooks/\d+/[\w-]+$`
- Slack URL must match: `^https://hooks\.slack\.com/services/T[\w]+/B[\w]+/[\w]+$`
- Only one webhook config per type (unique constraint on type)

**Sample Data**:
```json
{
  "id": 1,
  "type": "discord",
  "webhook_url": "https://discord.com/api/webhooks/123456789/abcdefg-hijklmnop",
  "enabled": 1,
  "created_at": "2025-10-15T10:00:00Z",
  "updated_at": "2025-10-15T10:00:00Z"
}
```

### 4. Post

Represents a Reddit post that has been detected and processed.

**SQLAlchemy Model**:
```python
class Post(Base):
    __tablename__ = 'posts'

    id = Column(String(20), primary_key=True)  # Reddit post ID (e.g., 't3_abc123')
    subreddit_id = Column(Integer, ForeignKey('subreddits.id'), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(String, nullable=True)  # May be empty for link posts
    author = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)  # Permalink to Reddit post
    created_utc = Column(DateTime, nullable=False)  # When post was created on Reddit
    processed = Column(Integer, nullable=False, default=0)  # 0=pending, 1=success, -1=failed
    processed_at = Column(DateTime, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    error_message = Column(String(1000), nullable=True)

    # Relationship
    subreddit = relationship('Subreddit', back_populates='posts')
    translations = relationship('Translation', back_populates='post', cascade='all, delete-orphan')
```

**Fields**:
- `id`: Reddit post ID (unique identifier from Reddit API)
- `subreddit_id`: Foreign key to Subreddit table
- `title`: Post title (original language)
- `content`: Post text content (selftext) - may be NULL for link posts
- `author`: Reddit username of post author
- `url`: Permalink to original Reddit post
- `created_utc`: When post was created (from Reddit)
- `processed`: Processing status (0=pending, 1=success, -1=failed)
- `processed_at`: When processing completed
- `retry_count`: Number of retry attempts if failed
- `error_message`: Error details if processing failed

**Validation Rules**:
- ID must be unique (Reddit post IDs are globally unique)
- Title max length: 300 characters (Reddit limit)
- Content truncated to 10,000 characters for translation
- Retry count max: 3

**State Transitions**:
```
New Post → processed=0 (pending)
   ├─→ Success → processed=1, processed_at=now
   └─→ Failure → processed=-1, retry_count++, error_message set
       └─→ Retry (if retry_count < 3) → processed=0
       └─→ Give up (if retry_count >= 3) → processed=-1 (permanent)
```

**Sample Data**:
```json
{
  "id": "t3_1a2b3c4",
  "subreddit_id": 1,
  "title": "Claude Code is amazing!",
  "content": "I just tried the new Claude Code CLI and it's incredible...",
  "author": "reddit_user_123",
  "url": "https://www.reddit.com/r/ClaudeAI/comments/1a2b3c4/claude_code_is_amazing/",
  "created_utc": "2025-10-15T09:45:00Z",
  "processed": 1,
  "processed_at": "2025-10-15T09:46:30Z",
  "retry_count": 0,
  "error_message": null
}
```

### 5. Translation

Stores translated versions of post titles and content.

**SQLAlchemy Model**:
```python
class Translation(Base):
    __tablename__ = 'translations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(String(20), ForeignKey('posts.id'), nullable=False)
    source_lang = Column(String(10), nullable=False)  # Detected source language
    target_lang = Column(String(10), nullable=False)  # Target language (from config)
    translated_title = Column(String(500), nullable=False)
    translated_content = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship
    post = relationship('Post', back_populates='translations')

    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('post_id', 'target_lang', name='uq_post_lang'),
    )
```

**Fields**:
- `id`: Primary key
- `post_id`: Foreign key to Post table
- `source_lang`: Detected source language (e.g., 'en')
- `target_lang`: Target language for translation (e.g., 'ko')
- `translated_title`: Translated post title
- `translated_content`: Translated post content (NULL if post had no content)
- `created_at`: When translation was created

**Validation Rules**:
- Unique constraint on (post_id, target_lang) - one translation per post per language
- Source and target languages must be valid ISO 639-1 codes
- If source_lang == target_lang, store original text (no API call)

**Sample Data**:
```json
{
  "id": 1,
  "post_id": "t3_1a2b3c4",
  "source_lang": "en",
  "target_lang": "ko",
  "translated_title": "Claude Code는 놀랍습니다!",
  "translated_content": "저는 방금 새로운 Claude Code CLI를 사용해봤는데 정말 놀라웠습니다...",
  "created_at": "2025-10-15T09:46:15Z"
}
```

## Database Schema SQL

**Initial schema (SQLite)**:
```sql
CREATE TABLE user_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    poll_interval_minutes INTEGER NOT NULL DEFAULT 5,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE subreddits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    url VARCHAR(500) NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1,
    last_checked_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE webhook_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type VARCHAR(20) NOT NULL UNIQUE,
    webhook_url VARCHAR(500) NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE posts (
    id VARCHAR(20) PRIMARY KEY,
    subreddit_id INTEGER NOT NULL,
    title VARCHAR(500) NOT NULL,
    content TEXT,
    author VARCHAR(100) NOT NULL,
    url VARCHAR(500) NOT NULL,
    created_utc TIMESTAMP NOT NULL,
    processed INTEGER NOT NULL DEFAULT 0,
    processed_at TIMESTAMP,
    retry_count INTEGER NOT NULL DEFAULT 0,
    error_message VARCHAR(1000),
    FOREIGN KEY (subreddit_id) REFERENCES subreddits(id) ON DELETE CASCADE
);

CREATE TABLE translations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id VARCHAR(20) NOT NULL,
    source_lang VARCHAR(10) NOT NULL,
    target_lang VARCHAR(10) NOT NULL,
    translated_title VARCHAR(500) NOT NULL,
    translated_content TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    UNIQUE(post_id, target_lang)
);

-- Indexes for performance
CREATE INDEX idx_posts_subreddit ON posts(subreddit_id);
CREATE INDEX idx_posts_processed ON posts(processed);
CREATE INDEX idx_posts_created_utc ON posts(created_utc);
CREATE INDEX idx_translations_post ON translations(post_id);
```

## Data Flow

### 1. Configuration Flow
```
User runs CLI → Updates UserConfig/WebhookConfig → Persisted to DB
```

### 2. Monitoring Flow
```
Scheduler triggers → Check Subreddit.enabled=1 → Fetch new posts from Reddit API
→ Create Post records (processed=0) → Trigger translation → Create Translation
→ Trigger webhook delivery → Update Post.processed=1
```

### 3. Translation Caching Flow
```
Before translating → Check if Translation exists (post_id + target_lang)
→ If exists: reuse → If not: call DeepL API → Store in Translation table
```

## Migration Strategy

Using Alembic for schema migrations:

**Initial migration**:
```bash
alembic init alembic
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

**Future migrations** (e.g., adding PostgreSQL support):
- Keep model definitions database-agnostic
- Use SQLAlchemy types (String, Integer, DateTime) not DB-specific types
- Test migrations on SQLite first, then PostgreSQL
