"""
Initialize database from environment variables.

This script reads configuration from environment variables and populates
the database with initial settings.
"""

import os
from models import UserConfig, Subreddit, WebhookConfig
from storage.database import get_session
from lib.logger import get_logger

logger = get_logger("cli.init_from_env")


def init_from_env():
    """Initialize database from environment variables."""
    session = get_session()
    try:
        # Initialize user config if not exists
        config = session.query(UserConfig).first()
        if not config:
            logger.info("Creating default user configuration...")
            config = UserConfig(
                language='ko',  # Default to Korean
                translator_service='gemini',  # Default to Gemini
                poll_interval_minutes=int(os.getenv('MONITOR_INTERVAL', 300)) // 60
            )
            session.add(config)
            logger.info(f"Created config: language={config.language}, translator_service={config.translator_service}")

        # Initialize webhook config from environment
        webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        if webhook_url and webhook_url != 'https://discord.com/api/webhooks/your_webhook_url':
            existing_webhook = session.query(WebhookConfig).filter_by(type='discord').first()
            if not existing_webhook:
                logger.info("Creating Discord webhook configuration...")
                webhook = WebhookConfig(
                    type='discord',
                    webhook_url=webhook_url,
                    enabled=1
                )
                session.add(webhook)
                logger.info(f"Created Discord webhook configuration")

        # Initialize subreddits from environment
        subreddits_env = os.getenv('SUBREDDITS', '')
        if subreddits_env:
            subreddit_names = [s.strip() for s in subreddits_env.split(',') if s.strip()]
            for name in subreddit_names:
                existing = session.query(Subreddit).filter_by(name=name).first()
                if not existing:
                    logger.info(f"Adding subreddit: r/{name}")
                    subreddit = Subreddit(
                        name=name,
                        enabled=1,
                        url=f"https://reddit.com/r/{name}"
                    )
                    session.add(subreddit)
                    logger.info(f"Added r/{name}")
                else:
                    logger.info(f"Subreddit r/{name} already exists")

        session.commit()
        logger.info("Initialization from environment variables complete")

    except Exception as e:
        logger.error(f"Failed to initialize from environment: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == '__main__':
    init_from_env()
