"""
Webhook management CLI commands.

Handles webhook set, test, enable/disable operations.
"""

import re
from models import WebhookConfig
from storage.database import get_session
from services.webhook_sender import WebhookSender
from cli import print_success, print_error, print_info
from lib.logger import get_logger

logger = get_logger("cli.webhook")


def handle_webhook_set(args):
    """Set webhook URL."""
    session = get_session()
    try:
        webhook_type = args.type
        webhook_url = args.url

        # Validate URL format
        if webhook_type == 'discord':
            if not re.match(r'^https://discord\.com/api/webhooks/\d+/[\w-]+$', webhook_url):
                print_error("Invalid Discord webhook URL format", args.json, exit_code=2)
        elif webhook_type == 'slack':
            if not re.match(r'^https://hooks\.slack\.com/services/T[\w]+/B[\w]+/[\w]+$', webhook_url):
                print_error("Invalid Slack webhook URL format", args.json, exit_code=2)

        # Check if webhook config exists
        webhook = session.query(WebhookConfig).filter_by(type=webhook_type).first()

        if webhook:
            webhook.webhook_url = webhook_url
            webhook.enabled = 1
        else:
            webhook = WebhookConfig(type=webhook_type, webhook_url=webhook_url, enabled=1)
            session.add(webhook)

        session.commit()

        # Redact URL for display
        url_preview = webhook_url[:30] + '***'

        print_success(f"{webhook_type.capitalize()} webhook configured", args.json, data={
            'type': webhook_type,
            'url_preview': url_preview,
            'enabled': True
        })
        print_info(f"URL: {url_preview}")
        print_info("Status: Enabled")

    finally:
        session.close()


def handle_webhook_test(args):
    """Test webhook delivery."""
    session = get_session()
    try:
        webhook_type = args.type

        # Get webhook config
        webhook = session.query(WebhookConfig).filter_by(type=webhook_type).first()
        if not webhook:
            print_error(f"{webhook_type.capitalize()} webhook not configured", args.json, exit_code=1)

        print_info(f"Testing {webhook_type} webhook...")

        # Send test message
        sender = WebhookSender()
        success = sender.test_webhook(webhook.webhook_url, webhook_type)

        if success:
            print_success("Test message delivered successfully", args.json)
        else:
            print_error("Test message delivery failed", args.json, exit_code=2)

    finally:
        session.close()
