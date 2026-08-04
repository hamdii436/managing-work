"""Business data repository."""

import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from database.base_repository import BaseRepository
from database.models import BusinessModel
from models.business import Business

logger = logging.getLogger(__name__)


class BusinessRepository(BaseRepository[BusinessModel]):
    """Repository for business data operations."""

    def __init__(self, db_session: Session) -> None:
        """Initialize business repository."""
        super().__init__(db_session, BusinessModel)

    def get_by_url(self, url: str) -> Optional[BusinessModel]:
        """Get business by Google Maps URL.
        
        Args:
            url: Google Maps URL
            
        Returns:
            Business model or None
        """
        try:
            return self.db_session.query(BusinessModel).filter(
                BusinessModel.url == url
            ).first()
        except Exception as e:
            logger.error(f"Failed to get business by URL: {e}")
            return None

    def get_by_name_and_city(self, name: str, city: str) -> Optional[BusinessModel]:
        """Get business by name and city.
        
        Args:
            name: Business name
            city: City name
            
        Returns:
            Business model or None
        """
        try:
            return self.db_session.query(BusinessModel).filter(
                BusinessModel.name == name,
                BusinessModel.city == city
            ).first()
        except Exception as e:
            logger.error(f"Failed to get business by name and city: {e}")
            return None

    def search_by_city(self, city: str, skip: int = 0, limit: int = 100) -> List[BusinessModel]:
        """Search businesses by city.
        
        Args:
            city: City name
            skip: Number to skip
            limit: Max results
            
        Returns:
            List of businesses
        """
        try:
            return self.db_session.query(BusinessModel).filter(
                BusinessModel.city == city
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to search businesses by city: {e}")
            return []

    def search_by_category(self, category: str, skip: int = 0, limit: int = 100) -> List[BusinessModel]:
        """Search businesses by category.
        
        Args:
            category: Category name
            skip: Number to skip
            limit: Max results
            
        Returns:
            List of businesses
        """
        try:
            return self.db_session.query(BusinessModel).filter(
                BusinessModel.category == category
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to search businesses by category: {e}")
            return []

    def search_by_rating(self, min_rating: float, max_rating: float, skip: int = 0, limit: int = 100) -> List[BusinessModel]:
        """Search businesses by rating range.
        
        Args:
            min_rating: Minimum rating
            max_rating: Maximum rating
            skip: Number to skip
            limit: Max results
            
        Returns:
            List of businesses
        """
        try:
            return self.db_session.query(BusinessModel).filter(
                BusinessModel.rating.between(min_rating, max_rating)
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to search businesses by rating: {e}")
            return []

    def search_by_criteria(self, city: Optional[str] = None, category: Optional[str] = None,
                          min_rating: Optional[float] = None, max_rating: Optional[float] = None,
                          skip: int = 0, limit: int = 100) -> List[BusinessModel]:
        """Search businesses by multiple criteria.
        
        Args:
            city: City name (optional)
            category: Category name (optional)
            min_rating: Minimum rating (optional)
            max_rating: Maximum rating (optional)
            skip: Number to skip
            limit: Max results
            
        Returns:
            List of businesses matching criteria
        """
        try:
            query = self.db_session.query(BusinessModel)
            
            if city:
                query = query.filter(BusinessModel.city == city)
            if category:
                query = query.filter(BusinessModel.category == category)
            if min_rating is not None:
                query = query.filter(BusinessModel.rating >= min_rating)
            if max_rating is not None:
                query = query.filter(BusinessModel.rating <= max_rating)
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to search businesses by criteria: {e}")
            return []

    def get_top_rated(self, limit: int = 10) -> List[BusinessModel]:
        """Get top rated businesses.
        
        Args:
            limit: Number of results
            
        Returns:
            List of top rated businesses
        """
        try:
            return self.db_session.query(BusinessModel).filter(
                BusinessModel.rating.isnot(None)
            ).order_by(BusinessModel.rating.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to get top rated businesses: {e}")
            return []

    def get_most_reviewed(self, limit: int = 10) -> List[BusinessModel]:
        """Get most reviewed businesses.
        
        Args:
            limit: Number of results
            
        Returns:
            List of most reviewed businesses
        """
        try:
            return self.db_session.query(BusinessModel).filter(
                BusinessModel.review_count.isnot(None)
            ).order_by(BusinessModel.review_count.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to get most reviewed businesses: {e}")
            return []

    def count_by_city(self, city: str) -> int:
        """Count businesses in a city.
        
        Args:
            city: City name
            
        Returns:
            Count of businesses
        """
        try:
            return self.db_session.query(BusinessModel).filter(
                BusinessModel.city == city
            ).count()
        except Exception as e:
            logger.error(f"Failed to count businesses by city: {e}")
            return 0

    def count_by_category(self, category: str) -> int:
        """Count businesses in a category.
        
        Args:
            category: Category name
            
        Returns:
            Count of businesses
        """
        try:
            return self.db_session.query(BusinessModel).filter(
                BusinessModel.category == category
            ).count()
        except Exception as e:
            logger.error(f"Failed to count businesses by category: {e}")
            return 0

    def get_duplicate_candidates(self, name: str, city: str, threshold: float = 0.8) -> List[BusinessModel]:
        """Get potential duplicate businesses.
        
        Args:
            name: Business name
            city: City name
            threshold: Similarity threshold (0.0 to 1.0)
            
        Returns:
            List of potential duplicates
        """
        try:
            # Get businesses in same city with similar names
            candidates = self.db_session.query(BusinessModel).filter(
                BusinessModel.city == city
            ).all()
            
            # Filter by name similarity (simple implementation)
            similar = []
            for candidate in candidates:
                name_lower = name.lower()
                candidate_name_lower = candidate.name.lower()
                if name_lower in candidate_name_lower or candidate_name_lower in name_lower:
                    similar.append(candidate)
            
            return similar
        except Exception as e:
            logger.error(f"Failed to get duplicate candidates: {e}")
            return []

    def delete_by_city(self, city: str) -> bool:
        """Delete all businesses in a city.
        
        Args:
            city: City name
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.db_session.query(BusinessModel).filter(
                BusinessModel.city == city
            ).delete()
            self.db_session.commit()
            logger.info(f"Deleted all businesses in {city}")
            return True
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to delete businesses by city: {e}")
            return False
