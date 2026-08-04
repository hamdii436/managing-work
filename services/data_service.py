"""Data service for business data management."""

import logging
from typing import List, Optional, Dict, Any

from database.db_manager import get_db_session
from database.business_repository import BusinessRepository
from database.models import BusinessModel
from models.business import Business, Location

logger = logging.getLogger(__name__)


class DataService:
    """Service for managing business data."""

    def __init__(self) -> None:
        """Initialize data service."""
        self.logger = logging.getLogger(__name__)

    def save_business(self, business: Business) -> bool:
        """Save a business to database.
        
        Args:
            business: Business to save
            
        Returns:
            True if successful
        """
        try:
            session = get_db_session()
            try:
                repo = BusinessRepository(session)
                
                # Check if business already exists
                existing = repo.get_by_url(business.url) if business.url else None
                
                if existing:
                    # Update existing
                    existing.name = business.name
                    existing.city = business.city
                    existing.district = business.district
                    existing.category = business.category
                    existing.phone = business.phone
                    existing.website = business.website
                    existing.email = business.email
                    existing.rating = business.rating
                    existing.review_count = business.review_count
                    existing.description = business.description
                    
                    if business.location:
                        existing.latitude = business.location.latitude
                        existing.longitude = business.location.longitude
                        existing.address = business.location.address
                    
                    repo.update(existing)
                else:
                    # Create new
                    model = BusinessModel(
                        url=business.url or "",
                        name=business.name,
                        city=business.city,
                        district=business.district,
                        category=business.category,
                        phone=business.phone,
                        website=business.website,
                        email=business.email,
                        rating=business.rating,
                        review_count=business.review_count,
                        description=business.description,
                        latitude=business.location.latitude if business.location else None,
                        longitude=business.location.longitude if business.location else None,
                        address=business.location.address if business.location else None,
                    )
                    repo.create(model)
                
                logger.info(f"Saved business: {business.name}")
                return True
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Failed to save business: {e}")
            return False

    def save_businesses(self, businesses: List[Business]) -> tuple[int, int]:
        """Save multiple businesses to database.
        
        Args:
            businesses: List of businesses to save
            
        Returns:
            Tuple of (saved_count, failed_count)
        """
        saved = 0
        failed = 0
        
        for business in businesses:
            if self.save_business(business):
                saved += 1
            else:
                failed += 1
        
        logger.info(f"Saved {saved} businesses, {failed} failed")
        return saved, failed

    def get_business(self, business_id: int) -> Optional[Business]:
        """Get business by ID.
        
        Args:
            business_id: Business ID
            
        Returns:
            Business or None
        """
        try:
            session = get_db_session()
            try:
                repo = BusinessRepository(session)
                model = repo.get_by_id(business_id)
                if model:
                    return self._model_to_business(model)
                return None
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Failed to get business: {e}")
            return None

    def get_all_businesses(self, skip: int = 0, limit: int = 100) -> List[Business]:
        """Get all businesses with pagination.
        
        Args:
            skip: Number to skip
            limit: Max results
            
        Returns:
            List of businesses
        """
        try:
            session = get_db_session()
            try:
                repo = BusinessRepository(session)
                models = repo.get_all(skip, limit)
                return [self._model_to_business(m) for m in models]
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Failed to get all businesses: {e}")
            return []

    def search_by_city(self, city: str, skip: int = 0, limit: int = 100) -> List[Business]:
        """Search businesses by city.
        
        Args:
            city: City name
            skip: Number to skip
            limit: Max results
            
        Returns:
            List of businesses
        """
        try:
            session = get_db_session()
            try:
                repo = BusinessRepository(session)
                models = repo.search_by_city(city, skip, limit)
                return [self._model_to_business(m) for m in models]
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Failed to search by city: {e}")
            return []

    def search_by_criteria(self, city: Optional[str] = None, category: Optional[str] = None,
                          min_rating: Optional[float] = None, max_rating: Optional[float] = None,
                          skip: int = 0, limit: int = 100) -> List[Business]:
        """Search businesses by multiple criteria.
        
        Args:
            city: City name (optional)
            category: Category (optional)
            min_rating: Minimum rating (optional)
            max_rating: Maximum rating (optional)
            skip: Number to skip
            limit: Max results
            
        Returns:
            List of businesses
        """
        try:
            session = get_db_session()
            try:
                repo = BusinessRepository(session)
                models = repo.search_by_criteria(city, category, min_rating, max_rating, skip, limit)
                return [self._model_to_business(m) for m in models]
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Failed to search by criteria: {e}")
            return []

    def count_total(self) -> int:
        """Get total count of businesses.
        
        Returns:
            Total count
        """
        try:
            session = get_db_session()
            try:
                repo = BusinessRepository(session)
                return repo.count()
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Failed to count businesses: {e}")
            return 0

    def delete_business(self, business_id: int) -> bool:
        """Delete a business.
        
        Args:
            business_id: Business ID
            
        Returns:
            True if successful
        """
        try:
            session = get_db_session()
            try:
                repo = BusinessRepository(session)
                return repo.delete_by_id(business_id)
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Failed to delete business: {e}")
            return False

    def delete_by_city(self, city: str) -> bool:
        """Delete all businesses in a city.
        
        Args:
            city: City name
            
        Returns:
            True if successful
        """
        try:
            session = get_db_session()
            try:
                repo = BusinessRepository(session)
                return repo.delete_by_city(city)
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Failed to delete businesses by city: {e}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Statistics dictionary
        """
        try:
            session = get_db_session()
            try:
                repo = BusinessRepository(session)
                all_businesses = repo.get_all(0, 100000)
                
                total = len(all_businesses)
                rated = len([b for b in all_businesses if b.rating])
                with_website = len([b for b in all_businesses if b.website])
                with_phone = len([b for b in all_businesses if b.phone])
                avg_rating = sum(b.rating for b in all_businesses if b.rating) / rated if rated > 0 else 0
                
                return {
                    'total_businesses': total,
                    'with_rating': rated,
                    'with_website': with_website,
                    'with_phone': with_phone,
                    'average_rating': avg_rating,
                }
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}

    def _model_to_business(self, model: BusinessModel) -> Business:
        """Convert database model to business object.
        
        Args:
            model: Business model
            
        Returns:
            Business object
        """
        location = None
        if model.latitude and model.longitude:
            location = Location(
                latitude=model.latitude,
                longitude=model.longitude,
                address=model.address,
            )
        
        return Business(
            name=model.name,
            city=model.city,
            district=model.district,
            category=model.category,
            phone=model.phone,
            website=model.website,
            email=model.email,
            rating=model.rating,
            review_count=model.review_count,
            url=model.url,
            description=model.description,
            location=location,
        )
