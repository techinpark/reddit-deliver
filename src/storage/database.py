"""
Database initialization and session management for SQLite.

Provides engine creation, session management, and database initialization.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Optional

from models import Base
from lib.logger import get_logger

logger = get_logger("database")


class Database:
    """
    Database connection and session manager.

    Handles SQLite database initialization and provides session management.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file (default: data/reddit-deliver.db)
        """
        if db_path is None:
            db_path = os.environ.get('REDDIT_DELIVER_DB', 'data/reddit-deliver.db')

        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.db_path = db_path
        self.engine = None
        self.Session = None

    def initialize(self):
        """
        Create database engine and initialize schema.

        Creates all tables if they don't exist.
        """
        logger.info(f"Initializing database at {self.db_path}")

        # Create engine with SQLite
        self.engine = create_engine(
            f'sqlite:///{self.db_path}',
            connect_args={'check_same_thread': False},  # Allow multi-threading
            poolclass=StaticPool,  # Use static pool for SQLite
            echo=False  # Set to True for SQL query logging
        )

        # Create session factory
        self.Session = sessionmaker(bind=self.engine)

        # Create all tables
        Base.metadata.create_all(self.engine)
        logger.info("Database schema initialized")

    def get_session(self) -> Session:
        """
        Get a new database session.

        Returns:
            SQLAlchemy session instance
        """
        if self.Session is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.Session()

    def close(self):
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")


# Global database instance
_db_instance: Optional[Database] = None


def get_database(db_path: Optional[str] = None) -> Database:
    """
    Get or create the global database instance.

    Args:
        db_path: Path to database file

    Returns:
        Database instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path)
        _db_instance.initialize()
    return _db_instance


def get_session() -> Session:
    """
    Get a new database session from the global database instance.

    Returns:
        SQLAlchemy session
    """
    return get_database().get_session()
