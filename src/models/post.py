"""
Post model for tracking Reddit posts and their processing status.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base


class Post(Base):
    """
    Represents a Reddit post that has been detected and processed.

    Attributes:
        id: Reddit post ID (primary key)
        subreddit_id: Foreign key to Subreddit
        title: Post title (original language)
        content: Post text content (may be NULL for link posts)
        author: Reddit username
        url: Permalink to original Reddit post
        created_utc: When post was created on Reddit
        processed: Processing status (0=pending, 1=success, -1=failed)
        processed_at: When processing completed
        retry_count: Number of retry attempts
        error_message: Error details if processing failed
        subreddit: Relationship to Subreddit model
        translations: Relationship to Translation model
    """
    __tablename__ = 'posts'

    id = Column(String(20), primary_key=True)  # Reddit post ID
    subreddit_id = Column(Integer, ForeignKey('subreddits.id'), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(String, nullable=True)
    author = Column(String(100), nullable=False)
    url = Column(String(500), nullable=False)
    created_utc = Column(DateTime, nullable=False)
    processed = Column(Integer, nullable=False, default=0)  # 0=pending, 1=success, -1=failed
    processed_at = Column(DateTime, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    error_message = Column(String(1000), nullable=True)

    # Relationships
    subreddit = relationship('Subreddit', back_populates='posts')
    translations = relationship('Translation', back_populates='post', cascade='all, delete-orphan')

    def __repr__(self):
        status_str = {0: 'pending', 1: 'success', -1: 'failed'}.get(self.processed, 'unknown')
        return f"<Post(id='{self.id}', title='{self.title[:30]}...', status='{status_str}')>"
