"""
Reddit API client service using PRAW.

Handles authentication, rate limiting, and fetching new posts from subreddits.
"""

import os
import praw
from datetime import datetime, timedelta
from typing import List, Optional
from lib.logger import get_logger
from lib.rate_limiter import RateLimiter

logger = get_logger("reddit_client")


class RedditClient:
    """
    Reddit API client for fetching new posts from subreddits.

    Uses PRAW library with read-only OAuth authentication.
    """

    def __init__(self):
        """Initialize Reddit client with credentials from environment."""
        client_id = os.environ.get('REDDIT_CLIENT_ID')
        client_secret = os.environ.get('REDDIT_CLIENT_SECRET')

        if not client_id or not client_secret:
            raise ValueError(
                "Reddit API credentials not found. "
                "Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables."
            )

        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent='reddit-deliver/0.1.0 (monitoring bot)'
        )

        # Rate limiter: Reddit allows 60 requests per minute with OAuth
        self.rate_limiter = RateLimiter(requests_per_minute=60)

        logger.info("Reddit client initialized")

    def get_new_posts(self, subreddit_name: str, limit: int = 25, since: Optional[datetime] = None) -> List[dict]:
        """
        Fetch new posts from a subreddit.

        Args:
            subreddit_name: Name of subreddit (e.g., 'ClaudeAI')
            limit: Maximum number of posts to fetch (default: 25)
            since: Only return posts newer than this timestamp (optional)

        Returns:
            List of post dictionaries with keys:
                - id: Reddit post ID
                - title: Post title
                - content: Post selftext (may be empty)
                - author: Username
                - url: Permalink URL
                - created_utc: Creation timestamp

        Raises:
            Exception: If subreddit doesn't exist or API error occurs
        """
        self.rate_limiter.wait_if_needed()

        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []

            if since:
                logger.debug(f"Fetching posts from r/{subreddit_name} since {since} (limit={limit})")
            else:
                logger.debug(f"Fetching new posts from r/{subreddit_name} (limit={limit})")

            total_checked = 0
            for submission in subreddit.new(limit=limit):
                total_checked += 1
                # Convert timestamp
                created_utc = datetime.utcfromtimestamp(submission.created_utc)

                # Filter by timestamp if provided
                if since and created_utc <= since:
                    logger.debug(f"Skipping post {submission.id} (created {created_utc}, cutoff {since})")
                    continue

                post_data = {
                    'id': submission.id,
                    'title': submission.title,
                    'content': submission.selftext or '',  # Empty string for link posts
                    'author': str(submission.author) if submission.author else '[deleted]',
                    'url': f"https://www.reddit.com{submission.permalink}",
                    'created_utc': created_utc
                }

                posts.append(post_data)
                logger.debug(f"Found new post: {submission.id} - {submission.title[:50]}")

            logger.info(f"Fetched {len(posts)} new posts from r/{subreddit_name} (checked {total_checked} total)")
            return posts

        except Exception as e:
            logger.error(f"Error fetching posts from r/{subreddit_name}: {e}")
            raise

    def test_connection(self) -> bool:
        """
        Test Reddit API connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try to fetch user info
            user = self.reddit.user.me()
            logger.info(f"Reddit connection test successful (read-only mode)")
            return True
        except Exception as e:
            logger.error(f"Reddit connection test failed: {e}")
            return False
