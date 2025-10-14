"""
WebhookConfig model for storing webhook destination configuration.
"""

from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from . import Base


class WebhookConfig(Base):
    """
    Webhook destination configuration (Discord or Slack).

    Attributes:
        id: Primary key
        type: Webhook type ('discord' or 'slack')
        webhook_url: Full webhook URL (contains secret token)
        enabled: Whether webhook is active
        created_at: When webhook was configured
        updated_at: Last modification timestamp
    """
    __tablename__ = 'webhook_config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(20), nullable=False, unique=True)  # 'discord' or 'slack'
    webhook_url = Column(String(500), nullable=False)
    enabled = Column(Integer, nullable=False, default=1)  # SQLite boolean
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        # Redact URL for security
        url_preview = self.webhook_url[:30] + '***' if len(self.webhook_url) > 30 else '***'
        return f"<WebhookConfig(type='{self.type}', url='{url_preview}')>"
