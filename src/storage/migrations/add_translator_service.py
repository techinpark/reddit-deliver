"""
Migration to add translator_service column to user_config table.

This migration adds support for selecting translation service (deepl/gemini).
"""

import os
import sys
import sqlite3

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from lib.logger import setup_logger

logger = setup_logger("migration")


def run_migration(db_path: str = "data/reddit-deliver.db"):
    """
    Add translator_service column to user_config table.

    Args:
        db_path: Path to database file
    """
    logger.info("Starting migration: add translator_service column...")

    if not os.path.exists(db_path):
        logger.error(f"Database not found: {db_path}")
        logger.error("Please run init_schema.py first")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(user_config)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'translator_service' in columns:
            logger.info("Column 'translator_service' already exists, skipping")
            return

        # Add the column
        logger.info("Adding column 'translator_service' to user_config table...")
        cursor.execute("""
            ALTER TABLE user_config
            ADD COLUMN translator_service VARCHAR(20) NOT NULL DEFAULT 'deepl'
        """)

        conn.commit()
        logger.info("✓ Migration completed successfully")

        # Show current config
        cursor.execute("SELECT language, translator_service, poll_interval_minutes FROM user_config")
        row = cursor.fetchone()
        if row:
            logger.info(f"Current config: language={row[0]}, translator_service={row[1]}, poll_interval={row[2]}")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Add translator_service column migration")
    parser.add_argument(
        '--db',
        default='data/reddit-deliver.db',
        help='Path to database file (default: data/reddit-deliver.db)'
    )
    args = parser.parse_args()

    run_migration(args.db)
