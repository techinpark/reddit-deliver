"""
Subreddit management CLI commands.

Handles subreddit add, list, remove, enable/disable operations.
"""

import re
from models import Subreddit
from storage.database import get_session
from cli import print_success, print_error, print_info
from lib.logger import get_logger

logger = get_logger("cli.subreddit")


def handle_subreddit_add(args):
    """Add a subreddit to monitor."""
    session = get_session()
    try:
        name = args.name
        url = args.url

        # Validate subreddit name
        if not re.match(r'^[A-Za-z0-9_]{3,21}$', name):
            print_error(
                f"Invalid subreddit name: {name} (must be 3-21 alphanumeric chars)",
                args.json,
                exit_code=1
            )

        # Generate URL if not provided
        if not url:
            url = f"https://www.reddit.com/r/{name}/"

        # Check if already exists
        existing = session.query(Subreddit).filter_by(name=name).first()
        if existing:
            print_error(f"Subreddit r/{name} already exists", args.json, exit_code=2)

        # Create subreddit
        subreddit = Subreddit(name=name, url=url, enabled=1)
        session.add(subreddit)
        session.commit()

        print_success(f"Subreddit added", args.json, data={
            'name': name,
            'url': url,
            'enabled': True
        })
        print_info(f"Name: {name}")
        print_info(f"URL: {url}")
        print_info("Status: Enabled")

    finally:
        session.close()
