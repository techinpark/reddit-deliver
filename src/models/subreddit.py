"""
Subreddit model for tracking monitored subreddits.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base


class Subreddit(Base):
    """
    Represents a Reddit subreddit to monitor for new posts.

    Attributes:
        id: Primary key
        name: Subreddit name (e.g., 'ClaudeAI')
        url: Full Reddit URL
        enabled: Whether actively monitoring (1=yes, 0=no)
        last_checked_at: Timestamp of last successful check
        created_at: When subreddit was added
        posts: Relationship to Post model
    """
    __tablename__ = 'subreddits'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    url = Column(String(500), nullable=False)
    enabled = Column(Integer, nullable=False, default=1)  # SQLite boolean
    last_checked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    posts = relationship('Post', back_populates='subreddit', cascade='all, delete-orphan')

    def __repr__(self):
        status = "enabled" if self.enabled else "disabled"
        return f"<Subreddit(name='{self.name}', {status})>"
