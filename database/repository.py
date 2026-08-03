"""Repository pattern implementation for database operations."""

import logging
from typing import Any, List, Optional, Type, TypeVar

from sqlalchemy.orm import Session

from core.base import Repository

logger = logging.getLogger(__name__)
T = TypeVar("T")


class BaseRepository(Repository[T]):
    """Base repository for common database operations."""

    def __init__(self, db_session: Session, model: Type[T]) -> None:
        """Initialize repository.

        Args:
            db_session: SQLAlchemy session
            model: SQLAlchemy model class
        """
        self.db_session = db_session
        self.model = model

    def add(self, entity: T) -> T:
        """Add entity to database."""
        try:
            self.db_session.add(entity)
            self.db_session.commit()
            self.db_session.refresh(entity)
            return entity
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to add entity: {e}")
            raise

    def update(self, entity: T) -> T:
        """Update existing entity."""
        try:
            self.db_session.merge(entity)
            self.db_session.commit()
            self.db_session.refresh(entity)
            return entity
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to update entity: {e}")
            raise

    def delete(self, entity_id: Any) -> bool:
        """Delete entity by ID."""
        try:
            entity = self.db_session.query(self.model).filter(self.model.id == entity_id).first()
            if entity:
                self.db_session.delete(entity)
                self.db_session.commit()
                return True
            return False
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to delete entity: {e}")
            raise

    def get_by_id(self, entity_id: Any) -> Optional[T]:
        """Get entity by ID."""
        try:
            return self.db_session.query(self.model).filter(self.model.id == entity_id).first()
        except Exception as e:
            logger.error(f"Failed to get entity: {e}")
            raise

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination."""
        try:
            return self.db_session.query(self.model).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to get all entities: {e}")
            raise

    def delete_all(self) -> int:
        """Delete all entities."""
        try:
            count = self.db_session.query(self.model).delete()
            self.db_session.commit()
            return count
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to delete all entities: {e}")
            raise

    def count(self) -> int:
        """Get total count of entities."""
        try:
            return self.db_session.query(self.model).count()
        except Exception as e:
            logger.error(f"Failed to count entities: {e}")
            raise

    def exists(self, entity_id: Any) -> bool:
        """Check if entity exists."""
        try:
            return self.db_session.query(self.model).filter(self.model.id == entity_id).first() is not None
        except Exception as e:
            logger.error(f"Failed to check entity existence: {e}")
            raise
