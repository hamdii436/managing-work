"""Search service for orchestrating business searches."""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional

from models.business import Business
from models.search import SearchCriteria, SearchJob, SearchResult
from core.enums import SearchStatus
from services.data_service import DataService
from services.deduplication_service import DeduplicationService
from services.scraper_service import ScraperService

logger = logging.getLogger(__name__)


class SearchService:
    """Service for orchestrating business searches."""

    def __init__(self) -> None:
        """Initialize search service."""
        self.data_service = DataService()
        self.deduplication_service = DeduplicationService()
        self.scraper_service = ScraperService()

    async def execute_search(self, search_job: SearchJob) -> SearchResult:
        """Execute a search job.

        Args:
            search_job: Search job to execute

        Returns:
            Search result

        Raises:
            Exception: If search fails
        """
        try:
            search_job.status = SearchStatus.RUNNING
            search_job.started_at = datetime.now()
            search_job.progress = 0.0

            # Build search query
            query = self._build_query(search_job.criteria)
            logger.info(f"Starting search: {query}")

            # Execute scraper
            results = await self.scraper_service.search_businesses(query)
            logger.info(f"Found {len(results)} raw results")

            # Convert to Business objects
            businesses = self._convert_to_businesses(results, search_job.criteria)
            search_job.progress = 0.5

            # Deduplicate
            unique_businesses = self.deduplication_service.remove_duplicates(businesses)
            logger.info(f"Deduplicated to {len(unique_businesses)} unique businesses")
            search_job.progress = 0.75

            # Apply filters
            filtered_businesses = self._apply_filters(unique_businesses, search_job.criteria)
            logger.info(f"After filtering: {len(filtered_businesses)} businesses")

            # Save to database
            saved_count = self.data_service.save_businesses(filtered_businesses)
            logger.info(f"Saved {saved_count} businesses to database")

            search_job.progress = 1.0
            search_job.status = SearchStatus.COMPLETED
            search_job.completed_at = datetime.now()

            result = SearchResult(
                total_found=len(results),
                total_saved=saved_count,
                duplicates_found=len(businesses) - len(unique_businesses),
                elapsed_time=(search_job.completed_at - search_job.started_at).total_seconds(),
            )

            return result

        except Exception as e:
            logger.error(f"Search failed: {e}")
            search_job.status = SearchStatus.FAILED
            search_job.error = str(e)
            search_job.completed_at = datetime.now()
            raise

    async def execute_multiple_searches(self, search_jobs: List[SearchJob]) -> List[SearchResult]:
        """Execute multiple search jobs.

        Args:
            search_jobs: List of search jobs

        Returns:
            List of search results
        """
        results = []
        for job in search_jobs:
            try:
                result = await self.execute_search(job)
                results.append(result)
            except Exception as e:
                logger.error(f"Search job {job.id} failed: {e}")
                results.append(SearchResult(
                    total_found=0,
                    total_saved=0,
                    duplicates_found=0,
                    errors=[str(e)],
                ))
        return results

    def _build_query(self, criteria: SearchCriteria) -> str:
        """Build search query from criteria.

        Args:
            criteria: Search criteria

        Returns:
            Search query string
        """
        return criteria.to_query_string()

    def _convert_to_businesses(
        self,
        results: List[dict],
        criteria: SearchCriteria,
    ) -> List[Business]:
        """Convert scraper results to Business objects.

        Args:
            results: Raw scraper results
            criteria: Search criteria

        Returns:
            List of Business objects
        """
        businesses = []
        for result in results:
            try:
                business = Business(
                    name=result.get("name", ""),
                    url=result.get("url"),
                    address=result.get("address"),
                    phone=result.get("phone"),
                    website=result.get("website"),
                    rating=result.get("rating"),
                    review_count=result.get("review_count"),
                    category=criteria.category or result.get("category"),
                    search_query=criteria.to_query_string(),
                )
                if business.is_valid():
                    businesses.append(business)
            except Exception as e:
                logger.warning(f"Failed to convert result: {e}")
        return businesses

    def _apply_filters(self, businesses: List[Business], criteria: SearchCriteria) -> List[Business]:
        """Apply search criteria filters to businesses.

        Args:
            businesses: List of businesses
            criteria: Search criteria

        Returns:
            Filtered businesses
        """
        filtered = businesses

        # Filter by rating
        if criteria.min_rating is not None:
            filtered = [b for b in filtered if b.rating and b.rating >= criteria.min_rating]

        if criteria.max_rating is not None:
            filtered = [b for b in filtered if b.rating and b.rating <= criteria.max_rating]

        # Filter by review count
        if criteria.min_reviews is not None:
            filtered = [b for b in filtered if b.review_count and b.review_count >= criteria.min_reviews]

        return filtered

    async def close(self) -> None:
        """Close search service resources."""
        await self.scraper_service.close()
        self.data_service.close()
        logger.info("SearchService closed")
