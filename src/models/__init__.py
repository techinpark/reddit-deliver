"""
Data models for Reddit Monitoring and Webhook Delivery System.

This module provides SQLAlchemy models for:
- UserConfig: Global user configuration
- Subreddit: Reddit subreddits to monitor
- WebhookConfig: Webhook destinations (Discord/Slack)
- Post: Reddit posts with processing status
- Translation: Cached translations
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLAlchemy base class for all models
Base = declarative_base()

# Export models for easy importing
from .user_config import UserConfig
from .subreddit import Subreddit
from .webhook_config import WebhookConfig
from .post import Post
from .translation import Translation

__all__ = [
    'Base',
    'UserConfig',
    'Subreddit',
    'WebhookConfig',
    'Post',
    'Translation',
]
