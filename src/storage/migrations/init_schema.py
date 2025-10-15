"""
Initial schema migration for reddit-deliver database.

This script initializes the database schema with all required tables.
Run this script to set up a new database.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from storage.database import Database
from models import Base, UserConfig
from lib.logger import setup_logger

logger = setup_logger("migration")


def run_migration(db_path: str = "data/reddit-deliver.db"):
    """
    Run the initial schema migration.

    Args:
        db_path: Path to database file
    """
    logger.info("Starting database migration...")

    # Initialize database
    db = Database(db_path)
    db.initialize()

    logger.info("✓ Database schema created successfully")

    # Create default user config if not exists
    session = db.get_session()
    try:
        config_count = session.query(UserConfig).count()
        if config_count == 0:
            default_config = UserConfig(
                language='en',
                translator_service='deepl',
                poll_interval_minutes=5
            )
            session.add(default_config)
            session.commit()
            logger.info("✓ Default configuration created (language=en, translator=deepl, poll_interval=5)")
        else:
            logger.info(f"Configuration already exists ({config_count} row(s))")
    finally:
        session.close()

    db.close()
    logger.info("Migration complete!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Initialize reddit-deliver database schema")
    parser.add_argument(
        '--db',
        default='data/reddit-deliver.db',
        help='Path to database file (default: data/reddit-deliver.db)'
    )
    args = parser.parse_args()

    run_migration(args.db)
