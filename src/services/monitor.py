"""
Monitoring orchestrator service.

Coordinates Reddit polling, translation, and webhook delivery.
"""

import time
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from models import Subreddit, Post, Translation, UserConfig, WebhookConfig
from services.reddit_client import RedditClient
from services.translator_factory import TranslatorFactory
from services.webhook_sender import WebhookSender
from storage.database import get_session
from lib.logger import get_logger

logger = get_logger("monitor")


class Monitor:
    """
    Monitoring orchestrator for Reddit posts.

    Polls subreddits, translates content, and delivers via webhooks.
    """

    def __init__(self, translator_service: Optional[str] = None):
        """
        Initialize monitor with service dependencies.

        Args:
            translator_service: Override translator service (e.g., 'deepl', 'gemini').
                              If None, uses value from UserConfig.
        """
        self.reddit_client = RedditClient()
        self.webhook_sender = WebhookSender()
        self._translator_service = translator_service
        self._translator = None
        logger.info("Monitor initialized")

    def check_subreddit(self, subreddit: Subreddit, session: Session) -> int:
        """
        Check a single subreddit for new posts.

        Args:
            subreddit: Subreddit model instance
            session: Database session

        Returns:
            Number of new posts processed
        """
        logger.info(f"Checking r/{subreddit.name}...")

        try:
            # Fetch new posts since last check
            since = subreddit.last_checked_at
            posts = self.reddit_client.get_new_posts(
                subreddit.name,
                limit=25,
                since=since
            )

            processed_count = 0

            for post_data in posts:
                # Check if post already exists (duplicate detection)
                existing = session.query(Post).filter_by(id=post_data['id']).first()
                if existing:
                    logger.debug(f"Post {post_data['id']} already processed, skipping")
                    continue

                # Process new post
                if self._process_post(post_data, subreddit, session):
                    processed_count += 1

            # Update last checked timestamp
            subreddit.last_checked_at = datetime.utcnow()
            session.commit()

            logger.info(f"✓ r/{subreddit.name}: {processed_count} new posts processed")
            return processed_count

        except Exception as e:
            logger.error(f"Error checking r/{subreddit.name}: {e}")
            session.rollback()
            return 0

    def _get_translator(self, session: Session):
        """
        Get or create translator instance based on configuration.

        Args:
            session: Database session

        Returns:
            Translator instance
        """
        if self._translator is None:
            # Determine which translator service to use
            service = self._translator_service
            if not service:
                config = session.query(UserConfig).first()
                if config:
                    service = config.translator_service
                else:
                    service = 'deepl'  # Default fallback

            logger.info(f"Creating {service} translator")
            self._translator = TranslatorFactory.create_translator(service)

        return self._translator

    def _process_post(self, post_data: dict, subreddit: Subreddit, session: Session) -> bool:
        """
        Process a single post: translate and send webhook.

        Args:
            post_data: Post data from Reddit API
            subreddit: Subreddit model instance
            session: Database session

        Returns:
            True if processed successfully, False otherwise
        """
        try:
            # Create Post record
            post = Post(
                id=post_data['id'],
                subreddit_id=subreddit.id,
                title=post_data['title'],
                content=post_data['content'],
                author=post_data['author'],
                url=post_data['url'],
                created_utc=post_data['created_utc'],
                processed=0  # Mark as pending
            )
            session.add(post)
            session.flush()  # Get post ID without committing

            # Get user config for target language
            config = session.query(UserConfig).first()
            if not config:
                logger.error("No user config found")
                return False

            target_lang = config.language

            # Get translator and translate post
            translator = self._get_translator(session)
            logger.debug(f"Translating post {post.id} to {target_lang}")
            translated_title, translated_content, source_lang = translator.translate_post(
                post.title,
                post.content,
                target_lang
            )

            # Save translation
            translation = Translation(
                post_id=post.id,
                source_lang=source_lang,
                target_lang=target_lang,
                translated_title=translated_title,
                translated_content=translated_content
            )
            session.add(translation)

            # Get webhook config
            webhook = session.query(WebhookConfig).filter_by(enabled=1).first()
            if not webhook:
                logger.warning("No enabled webhook found, skipping delivery")
                post.processed = 1  # Mark as processed anyway
                post.processed_at = datetime.utcnow()
                session.commit()
                return True

            # Send webhook
            logger.debug(f"Sending {webhook.type} webhook for post {post.id}")
            success = False

            if webhook.type == 'discord':
                success = self.webhook_sender.send_discord(
                    webhook.webhook_url,
                    translated_title,
                    translated_content or '',
                    post.url,
                    post.author
                )
            elif webhook.type == 'slack':
                success = self.webhook_sender.send_slack(
                    webhook.webhook_url,
                    translated_title,
                    translated_content or '',
                    post.url,
                    post.author
                )

            # Update post status
            if success:
                post.processed = 1
                post.processed_at = datetime.utcnow()
                logger.info(f"✓ Post {post.id} processed successfully")
            else:
                post.processed = -1
                post.retry_count += 1
                post.error_message = "Webhook delivery failed"
                logger.error(f"✗ Post {post.id} webhook delivery failed")

            session.commit()
            return success

        except Exception as e:
            logger.error(f"Error processing post {post_data['id']}: {e}")
            post.processed = -1
            post.error_message = str(e)
            post.retry_count += 1
            session.commit()
            return False

    def check_all_enabled(self) -> dict:
        """
        Check all enabled subreddits for new posts.

        Returns:
            Dictionary with statistics:
                - total_checked: Number of subreddits checked
                - total_posts: Total new posts processed
                - errors: Number of errors
        """
        session = get_session()
        stats = {
            'total_checked': 0,
            'total_posts': 0,
            'errors': 0
        }

        try:
            # Get all enabled subreddits
            subreddits = session.query(Subreddit).filter_by(enabled=1).all()

            if not subreddits:
                logger.warning("No enabled subreddits found")
                return stats

            logger.info(f"Checking {len(subreddits)} enabled subreddit(s)...")

            for subreddit in subreddits:
                stats['total_checked'] += 1
                try:
                    posts_processed = self.check_subreddit(subreddit, session)
                    stats['total_posts'] += posts_processed
                except Exception as e:
                    logger.error(f"Error checking r/{subreddit.name}: {e}")
                    stats['errors'] += 1

            logger.info(
                f"Check complete: {stats['total_posts']} posts processed, "
                f"{stats['errors']} errors"
            )

        finally:
            session.close()

        return stats

    def run_once(self) -> dict:
        """
        Run a single monitoring cycle.

        Checks all enabled subreddits once and returns.

        Returns:
            Statistics dictionary
        """
        logger.info("Starting single monitoring cycle...")
        stats = self.check_all_enabled()
        logger.info("Monitoring cycle complete")
        return stats

    def run_daemon(self, interval: int = 300):
        """
        Run monitoring in daemon mode (continuous loop).

        Checks subreddits at regular intervals until interrupted.

        Args:
            interval: Check interval in seconds (default: 300 = 5 minutes)
        """
        logger.info(f"Starting daemon mode with {interval}s interval...")

        try:
            while True:
                try:
                    logger.info("Running monitoring cycle...")
                    stats = self.check_all_enabled()
                    logger.info(
                        f"Cycle complete: {stats['total_posts']} posts, "
                        f"{stats['errors']} errors"
                    )
                except Exception as e:
                    logger.error(f"Error in monitoring cycle: {e}")

                logger.info(f"Sleeping for {interval} seconds...")
                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("Daemon stopped by user")
            raise
