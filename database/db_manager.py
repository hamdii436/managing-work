"""Database manager and connection pool."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine, event, Engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session

from config.settings import get_settings
from database.models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and lifecycle."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        """Initialize database manager.

        Args:
            db_path: Path to SQLite database file
        """
        settings = get_settings()
        self.db_path = db_path or settings.database_path
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        self._initialized = False

    def initialize(self) -> None:
        """Initialize database connection and create tables."""
        if self._initialized:
            return
            
        try:
            # Create database directory if it doesn't exist
            db_file = Path(self.db_path)
            db_file.parent.mkdir(parents=True, exist_ok=True)

            # Create SQLite engine
            self.engine = create_engine(
                f"sqlite:///{db_file.absolute()}",
                echo=False,
                pool_size=10,
                pool_recycle=3600,
                connect_args={"check_same_thread": False},
            )

            # Enable foreign keys
            @event.listens_for(Engine, "connect")
            def set_sqlite_pragma(dbapi_connection: any, connection_record: any) -> None:
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

            # Create session factory
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            self._initialized = True
            logger.info(f"Database initialized at {self.db_path}")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def get_session(self) -> Session:
        """Get a new database session.

        Returns:
            Database session

        Raises:
            RuntimeError: If database is not initialized
        """
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.SessionLocal()

    def verify_connection(self) -> tuple[bool, str]:
        """Verify database connection is working.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            if self.engine is None:
                return False, "Database engine not initialized"
            
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("Database connection verified")
            return True, "Database connection successful"
        except Exception as e:
            error_msg = f"Database connection failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def get_database_info(self) -> dict:
        """Get database information.
        
        Returns:
            Dictionary with database info
        """
        try:
            if self.engine is None:
                return {'error': 'Database not initialized'}
            
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            return {
                'path': str(self.db_path),
                'tables': tables,
                'table_count': len(tables),
                'is_connected': True,
            }
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {
                'error': str(e),
                'is_connected': False,
            }

    def close(self) -> None:
        """Close database connection."""
        if self.engine:
            self.engine.dispose()
            self._initialized = False
            logger.info("Database connection closed")

    def backup(self, backup_path: Optional[str] = None) -> tuple[bool, str]:
        """Backup database to file.

        Args:
            backup_path: Path to backup directory

        Returns:
            Tuple of (success, message)
        """
        try:
            from shutil import copy2
            settings = get_settings()
            backup_dir = Path(backup_path or settings.database_backup_path)
            backup_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"database_backup_{timestamp}.db"
            copy2(self.db_path, str(backup_file))
            msg = f"Database backed up to {backup_file}"
            logger.info(msg)
            return True, msg
        except Exception as e:
            error_msg = f"Failed to backup database: {e}"
            logger.error(error_msg)
            return False, error_msg

    def reset(self) -> None:
        """Reset database (drop all tables and recreate)."""
        if self.engine is None:
            raise RuntimeError("Database not initialized")
        try:
            Base.metadata.drop_all(bind=self.engine)
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database reset successfully")
        except Exception as e:
            logger.error(f"Failed to reset database: {e}")
            raise


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """Get or create database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
        _db_manager.initialize()
    return _db_manager


def get_session() -> Session:
    """Get a database session."""
    return get_db_manager().get_session()


def verify_database() -> tuple[bool, str]:
    """Verify database connection."""
    return get_db_manager().verify_connection()


def get_db_info() -> dict:
    """Get database information."""
    return get_db_manager().get_database_info()


def backup_database(backup_path: Optional[str] = None) -> tuple[bool, str]:
    """Create database backup."""
    return get_db_manager().backup(backup_path)

