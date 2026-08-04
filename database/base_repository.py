"""Base repository with common CRUD operations."""

import logging
from typing import Generic, TypeVar, List, Optional, Type

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Base repository class for common database operations."""

    def __init__(self, db_session: Session, model_class: Type[T]) -> None:
        """Initialize base repository.
        
        Args:
            db_session: SQLAlchemy session
            model_class: Model class for this repository
        """
        self.db_session = db_session
        self.model_class = model_class

    def create(self, obj: T) -> T:
        """Create new object in database.
        
        Args:
            obj: Object to create
            
        Returns:
            Created object
        """
        try:
            self.db_session.add(obj)
            self.db_session.commit()
            self.db_session.refresh(obj)
            logger.debug(f"Created {self.model_class.__name__}")
            return obj
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to create {self.model_class.__name__}: {e}")
            raise

    def create_many(self, objects: List[T]) -> List[T]:
        """Create multiple objects in database.
        
        Args:
            objects: List of objects to create
            
        Returns:
            List of created objects
        """
        try:
            self.db_session.add_all(objects)
            self.db_session.commit()
            logger.debug(f"Created {len(objects)} {self.model_class.__name__} objects")
            return objects
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to create multiple {self.model_class.__name__}: {e}")
            raise

    def get_by_id(self, obj_id: any) -> Optional[T]:
        """Get object by ID.
        
        Args:
            obj_id: Object ID
            
        Returns:
            Object or None if not found
        """
        try:
            return self.db_session.query(self.model_class).filter(
                self.model_class.id == obj_id
            ).first()
        except Exception as e:
            logger.error(f"Failed to get {self.model_class.__name__} by id: {e}")
            return None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all objects with pagination.
        
        Args:
            skip: Number of objects to skip
            limit: Maximum number of objects to return
            
        Returns:
            List of objects
        """
        try:
            return self.db_session.query(self.model_class).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to get all {self.model_class.__name__}: {e}")
            return []

    def count(self) -> int:
        """Get total count of objects.
        
        Returns:
            Total count
        """
        try:
            return self.db_session.query(self.model_class).count()
        except Exception as e:
            logger.error(f"Failed to count {self.model_class.__name__}: {e}")
            return 0

    def update(self, obj: T) -> T:
        """Update object in database.
        
        Args:
            obj: Object to update
            
        Returns:
            Updated object
        """
        try:
            self.db_session.merge(obj)
            self.db_session.commit()
            logger.debug(f"Updated {self.model_class.__name__}")
            return obj
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to update {self.model_class.__name__}: {e}")
            raise

    def delete(self, obj: T) -> bool:
        """Delete object from database.
        
        Args:
            obj: Object to delete
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            self.db_session.delete(obj)
            self.db_session.commit()
            logger.debug(f"Deleted {self.model_class.__name__}")
            return True
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to delete {self.model_class.__name__}: {e}")
            return False

    def delete_by_id(self, obj_id: any) -> bool:
        """Delete object by ID.
        
        Args:
            obj_id: Object ID
            
        Returns:
            True if deleted, False otherwise
        """
        obj = self.get_by_id(obj_id)
        if obj:
            return self.delete(obj)
        return False

    def delete_all(self) -> bool:
        """Delete all objects.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.db_session.query(self.model_class).delete()
            self.db_session.commit()
            logger.debug(f"Deleted all {self.model_class.__name__} objects")
            return True
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to delete all {self.model_class.__name__}: {e}")
            return False

    def exists(self, obj_id: any) -> bool:
        """Check if object exists.
        
        Args:
            obj_id: Object ID
            
        Returns:
            True if exists, False otherwise
        """
        try:
            return self.db_session.query(
                self.db_session.query(self.model_class).filter(
                    self.model_class.id == obj_id
                ).exists()
            ).scalar()
        except Exception as e:
            logger.error(f"Failed to check existence of {self.model_class.__name__}: {e}")
            return False

    def bulk_update(self, objects: List[T]) -> bool:
        """Update multiple objects in transaction.
        
        Args:
            objects: List of objects to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            for obj in objects:
                self.db_session.merge(obj)
            self.db_session.commit()
            logger.debug(f"Updated {len(objects)} {self.model_class.__name__} objects")
            return True
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to bulk update {self.model_class.__name__}: {e}")
            return False
