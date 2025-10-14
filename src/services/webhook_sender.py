"""
Webhook sender service for Discord and Slack.

Handles formatting and delivery of webhook notifications with retry logic.
"""

import requests
import time
from typing import Optional
from lib.logger import get_logger

logger = get_logger("webhook_sender")


class WebhookSender:
    """
    Webhook notification sender for Discord and Slack.

    Formats messages according to platform specifications and handles delivery.
    """

    def __init__(self):
        """Initialize webhook sender."""
        logger.info("Webhook sender initialized")

    def send_discord(
        self,
        webhook_url: str,
        title: str,
        content: str,
        url: str,
        author: str,
        max_retries: int = 3
    ) -> bool:
        """
        Send notification to Discord webhook.

        Args:
            webhook_url: Discord webhook URL
            title: Post title (translated)
            content: Post content (translated, may be empty)
            url: Original Reddit post URL
            author: Post author username
            max_retries: Maximum retry attempts

        Returns:
            True if sent successfully, False otherwise
        """
        # Truncate content to Discord's limit (2048 chars in embed description)
        content_preview = content[:2000] + "..." if len(content) > 2000 else content

        payload = {
            "content": f"**New post in r/{self._extract_subreddit(url)}**",
            "embeds": [{
                "title": title[:256],  # Discord title limit
                "description": content_preview,
                "url": url,
                "color": 5814783,  # Blue color
                "footer": {
                    "text": f"Posted by u/{author}"
                }
            }]
        }

        return self._send_webhook(webhook_url, payload, "Discord", max_retries)

    def send_slack(
        self,
        webhook_url: str,
        title: str,
        content: str,
        url: str,
        author: str,
        max_retries: int = 3
    ) -> bool:
        """
        Send notification to Slack webhook.

        Args:
            webhook_url: Slack webhook URL
            title: Post title (translated)
            content: Post content (translated, may be empty)
            url: Original Reddit post URL
            author: Post author username
            max_retries: Maximum retry attempts

        Returns:
            True if sent successfully, False otherwise
        """
        # Truncate content to reasonable length for Slack
        content_preview = content[:3000] + "..." if len(content) > 3000 else content

        payload = {
            "text": f"*New post in r/{self._extract_subreddit(url)}*",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*<{url}|{title}>*\n{content_preview}\n\n_Posted by u/{author}_"
                    }
                }
            ]
        }

        return self._send_webhook(webhook_url, payload, "Slack", max_retries)

    def _send_webhook(
        self,
        url: str,
        payload: dict,
        platform: str,
        max_retries: int
    ) -> bool:
        """
        Send webhook with retry logic.

        Args:
            url: Webhook URL
            payload: JSON payload
            platform: Platform name (for logging)
            max_retries: Maximum retry attempts

        Returns:
            True if sent successfully, False otherwise
        """
        for attempt in range(max_retries):
            try:
                logger.debug(f"Sending {platform} webhook (attempt {attempt + 1}/{max_retries})")

                response = requests.post(
                    url,
                    json=payload,
                    timeout=10
                )

                if response.status_code in (200, 204):
                    logger.info(f"✓ {platform} webhook delivered successfully")
                    return True
                elif response.status_code == 429:
                    # Rate limited - wait and retry
                    retry_after = int(response.headers.get('Retry-After', 5))
                    logger.warning(f"{platform} webhook rate limited, retrying after {retry_after}s")
                    time.sleep(retry_after)
                else:
                    logger.warning(
                        f"{platform} webhook failed: {response.status_code} - {response.text}"
                    )

                    # Exponential backoff for other errors
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # 1s, 2s, 4s
                        logger.debug(f"Retrying in {wait_time}s...")
                        time.sleep(wait_time)

            except requests.exceptions.Timeout:
                logger.error(f"{platform} webhook timeout (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)

            except Exception as e:
                logger.error(f"{platform} webhook error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)

        logger.error(f"✗ {platform} webhook delivery failed after {max_retries} attempts")
        return False

    def test_webhook(self, webhook_url: str, webhook_type: str) -> bool:
        """
        Test webhook delivery with a test message.

        Args:
            webhook_url: Webhook URL
            webhook_type: 'discord' or 'slack'

        Returns:
            True if test successful, False otherwise
        """
        logger.info(f"Testing {webhook_type} webhook...")

        if webhook_type == 'discord':
            return self.send_discord(
                webhook_url,
                title="Test Notification from reddit-deliver",
                content="This is a test message to verify webhook configuration.",
                url="https://www.reddit.com",
                author="reddit-deliver",
                max_retries=1
            )
        elif webhook_type == 'slack':
            return self.send_slack(
                webhook_url,
                title="Test Notification from reddit-deliver",
                content="This is a test message to verify webhook configuration.",
                url="https://www.reddit.com",
                author="reddit-deliver",
                max_retries=1
            )
        else:
            logger.error(f"Unknown webhook type: {webhook_type}")
            return False

    @staticmethod
    def _extract_subreddit(url: str) -> str:
        """Extract subreddit name from Reddit URL."""
        try:
            parts = url.split('/r/')
            if len(parts) > 1:
                subreddit = parts[1].split('/')[0]
                return subreddit
        except:
            pass
        return "unknown"
