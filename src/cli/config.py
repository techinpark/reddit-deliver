"""
Configuration CLI commands for reddit-deliver.

Handles config init, set, and get operations.
"""

import sys
from models import UserConfig
from storage.database import get_session
from cli import print_success, print_error, print_info
from lib.logger import get_logger

logger = get_logger("cli.config")


def handle_config_init(args):
    """Initialize configuration with defaults."""
    session = get_session()
    try:
        # Check if config already exists
        existing = session.query(UserConfig).first()
        if existing:
            print_error("Configuration already exists. Use 'config set' to modify.", args.json, exit_code=1)

        # Create default config
        config = UserConfig(language='en', poll_interval_minutes=5)
        session.add(config)
        session.commit()

        print_success("Configuration initialized with defaults", args.json, data={
            'language': 'en',
            'poll_interval': 5
        })
        print_info("language: en")
        print_info("poll_interval: 5 minutes")

    finally:
        session.close()


def handle_config_set(args):
    """Set a configuration value."""
    session = get_session()
    try:
        config = session.query(UserConfig).first()
        if not config:
            print_error("Configuration not found. Run 'config init' first.", args.json, exit_code=2)

        key = args.key
        value = args.value

        if key == 'language':
            config.language = value
        elif key == 'poll_interval':
            try:
                config.poll_interval_minutes = int(value)
            except ValueError:
                print_error(f"Invalid poll_interval value: {value} (must be integer)", args.json, exit_code=2)
        else:
            print_error(f"Unknown configuration key: {key}", args.json, exit_code=1)

        session.commit()
        print_success(f"Configuration updated", args.json, data={key: value})
        print_info(f"{key}: {value}")

    finally:
        session.close()


def handle_config_get(args):
    """Get configuration value(s)."""
    session = get_session()
    try:
        config = session.query(UserConfig).first()
        if not config:
            print_error("Configuration not found. Run 'config init' first.", args.json, exit_code=2)

        key = args.key

        if key == 'all':
            data = {
                'language': config.language,
                'poll_interval': config.poll_interval_minutes
            }
            if args.json:
                import json
                print(json.dumps(data, indent=2))
            else:
                print(f"language: {config.language}")
                print(f"poll_interval: {config.poll_interval_minutes}")
        elif key == 'language':
            if args.json:
                import json
                print(json.dumps({'language': config.language}))
            else:
                print(config.language)
        elif key == 'poll_interval':
            if args.json:
                import json
                print(json.dumps({'poll_interval': config.poll_interval_minutes}))
            else:
                print(config.poll_interval_minutes)
        else:
            print_error(f"Unknown configuration key: {key}", args.json, exit_code=1)

    finally:
        session.close()
