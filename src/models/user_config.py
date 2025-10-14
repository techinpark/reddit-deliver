"""
UserConfig model for storing global user configuration settings.
"""

from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from . import Base


class UserConfig(Base):
    """
    Global user configuration settings.

    Stores user preferences for translation language and polling interval.
    Should be a singleton (only one row in the table).
    """
    __tablename__ = 'user_config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    language = Column(String(10), nullable=False, default='en')  # ISO 639-1 code
    poll_interval_minutes = Column(Integer, nullable=False, default=5)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserConfig(language='{self.language}', poll_interval={self.poll_interval_minutes})>"
