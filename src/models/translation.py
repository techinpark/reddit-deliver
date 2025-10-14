"""
Translation model for caching translated post content.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base


class Translation(Base):
    """
    Stores translated versions of post titles and content.

    Attributes:
        id: Primary key
        post_id: Foreign key to Post
        source_lang: Detected source language (e.g., 'en')
        target_lang: Target language (e.g., 'ko')
        translated_title: Translated post title
        translated_content: Translated post content (NULL if no content)
        created_at: When translation was created
        post: Relationship to Post model
    """
    __tablename__ = 'translations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(String(20), ForeignKey('posts.id'), nullable=False)
    source_lang = Column(String(10), nullable=False)
    target_lang = Column(String(10), nullable=False)
    translated_title = Column(String(500), nullable=False)
    translated_content = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship
    post = relationship('Post', back_populates='translations')

    # Composite unique constraint: one translation per post per language
    __table_args__ = (
        UniqueConstraint('post_id', 'target_lang', name='uq_post_lang'),
    )

    def __repr__(self):
        return f"<Translation(post_id='{self.post_id}', {self.source_lang}→{self.target_lang})>"
