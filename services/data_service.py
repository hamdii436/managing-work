"""Data service for business data management."""

import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from database.db_manager import get_session
from database.models import BusinessModel
from database.repository import BaseRepository
from models.business import Business

logger = logging.getLogger(__name__)


class DataService:
    """Service for managing business data."""

    def __init__(self, db_session: Optional[Session] = None) -> None:
        """Initialize data service.

        Args:
            db_session: Database session (creates new if not provided)
        """
        self.db_session = db_session or get_session()
        self.repository = BaseRepository(self.db_session, BusinessModel)

    def save_business(self, business: Business) -> Business:
        """Save business to database.

        Args:
            business: Business object to save

        Returns:
            Saved business object
        """
        try:
            db_business = self._business_to_model(business)
            return self.repository.add(db_business)
        except Exception as e:
            logger.error(f"Failed to save business: {e}")
            raise

    def save_businesses(self, businesses: List[Business]) -> int:
        """Save multiple businesses to database.

        Args:
            businesses: List of Business objects

        Returns:
            Number of businesses saved
        """
        saved_count = 0
        for business in businesses:
            try:
                self.save_business(business)
                saved_count += 1
            except Exception as e:
                logger.warning(f"Failed to save business {business.name}: {e}")
        return saved_count

    def get_business(self, business_id: str) -> Optional[Business]:
        """Get business by ID.

        Args:
            business_id: Business ID

        Returns:
            Business object or None
        """
        try:
            db_business = self.repository.get_by_id(business_id)
            return self._model_to_business(db_business) if db_business else None
        except Exception as e:
            logger.error(f"Failed to get business: {e}")
            raise

    def get_all_businesses(self, skip: int = 0, limit: int = 100) -> List[Business]:
        """Get all businesses with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            List of Business objects
        """
        try:
            db_businesses = self.repository.get_all(skip, limit)
            return [self._model_to_business(b) for b in db_businesses]
        except Exception as e:
            logger.error(f"Failed to get businesses: {e}")
            raise

    def search_businesses(
        self,
        category: Optional[str] = None,
        min_rating: Optional[float] = None,
        city: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Business]:
        """Search businesses with filters.

        Args:
            category: Filter by category
            min_rating: Filter by minimum rating
            city: Filter by city
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            List of matching Business objects
        """
        try:
            query = self.db_session.query(BusinessModel)
            if category:
                query = query.filter(BusinessModel.category == category)
            if min_rating is not None:
                query = query.filter(BusinessModel.rating >= min_rating)
            if city:
                query = query.filter(BusinessModel.address.ilike(f"%{city}%"))
            
            results = query.offset(skip).limit(limit).all()
            return [self._model_to_business(b) for b in results]
        except Exception as e:
            logger.error(f"Failed to search businesses: {e}")
            raise

    def delete_business(self, business_id: str) -> bool:
        """Delete business by ID.

        Args:
            business_id: Business ID

        Returns:
            True if deleted, False otherwise
        """
        try:
            return self.repository.delete(business_id)
        except Exception as e:
            logger.error(f"Failed to delete business: {e}")
            raise

    def get_total_count(self) -> int:
        """Get total number of businesses.

        Returns:
            Total count
        """
        try:
            return self.repository.count()
        except Exception as e:
            logger.error(f"Failed to get count: {e}")
            raise

    def _business_to_model(self, business: Business) -> BusinessModel:
        """Convert Business object to SQLAlchemy model."""
        return BusinessModel(
            id=business.id,
            name=business.name,
            url=business.url,
            address=business.address,
            phone=business.phone,
            website=business.website,
            rating=business.rating,
            review_count=business.review_count,
            category=business.category,
            latitude=business.location.latitude,
            longitude=business.location.longitude,
            description=business.description,
            source=business.source,
            is_verified=business.is_verified,
            is_duplicate=business.is_duplicate,
            search_query=business.search_query,
            created_at=business.created_at,
            updated_at=business.updated_at,
        )

    def _model_to_business(self, db_business: BusinessModel) -> Business:
        """Convert SQLAlchemy model to Business object."""
        return Business(
            id=db_business.id,
            name=db_business.name,
            url=db_business.url,
            address=db_business.address,
            phone=db_business.phone,
            website=db_business.website,
            rating=db_business.rating,
            review_count=db_business.review_count,
            category=db_business.category,
            description=db_business.description,
            source=db_business.source,
            is_verified=db_business.is_verified,
            is_duplicate=db_business.is_duplicate,
            search_query=db_business.search_query,
            created_at=db_business.created_at,
            updated_at=db_business.updated_at,
        )

    def close(self) -> None:
        """Close database session."""
        if self.db_session:
            self.db_session.close()
