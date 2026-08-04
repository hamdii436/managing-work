"""Search service for managing and executing searches."""

import logging
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from config.settings import get_settings
from core.enums import SearchStatus
from models.search import SearchJob, SearchCriteria, SearchResult
from models.business import Business

logger = logging.getLogger(__name__)


class SearchQueue:
    """Manages search job queue."""

    def __init__(self):
        """Initialize search queue."""
        self.queue: List[SearchJob] = []
        self.running_jobs: Dict[str, SearchJob] = {}

    def add(self, criteria: SearchCriteria) -> SearchJob:
        """Add search job to queue.
        
        Args:
            criteria: Search criteria
            
        Returns:
            Created search job
        """
        job = SearchJob(
            id=str(uuid.uuid4()),
            criteria=criteria,
        )
        self.queue.append(job)
        logger.info(f"Added search job to queue: {job.id}")
        return job

    def add_many(self, criteria_list: List[SearchCriteria]) -> List[SearchJob]:
        """Add multiple search jobs to queue.
        
        Args:
            criteria_list: List of search criteria
            
        Returns:
            List of created search jobs
        """
        jobs = []
        for criteria in criteria_list:
            job = self.add(criteria)
            jobs.append(job)
        return jobs

    def get_pending(self, limit: int = 10) -> List[SearchJob]:
        """Get pending jobs from queue.
        
        Args:
            limit: Maximum number of jobs
            
        Returns:
            List of pending jobs
        """
        return [job for job in self.queue if job.status == SearchStatus.PENDING][:limit]

    def get_next(self) -> Optional[SearchJob]:
        """Get next pending job from queue.
        
        Returns:
            Next pending job or None
        """
        pending = self.get_pending(1)
        return pending[0] if pending else None

    def pop_job(self, job_id: str) -> Optional[SearchJob]:
        """Remove job from queue.
        
        Args:
            job_id: Job ID
            
        Returns:
            Removed job or None
        """
        for i, job in enumerate(self.queue):
            if job.id == job_id:
                return self.queue.pop(i)
        return None

    def mark_running(self, job_id: str) -> bool:
        """Mark job as running.
        
        Args:
            job_id: Job ID
            
        Returns:
            True if successful
        """
        job = self.pop_job(job_id)
        if job:
            job.start()
            self.running_jobs[job_id] = job
            return True
        return False

    def mark_completed(self, job_id: str, result: SearchResult) -> bool:
        """Mark job as completed.
        
        Args:
            job_id: Job ID
            result: Search result
            
        Returns:
            True if successful
        """
        if job_id in self.running_jobs:
            job = self.running_jobs.pop(job_id)
            job.complete(result)
            return True
        return False

    def mark_failed(self, job_id: str, error: str) -> bool:
        """Mark job as failed.
        
        Args:
            job_id: Job ID
            error: Error message
            
        Returns:
            True if successful
        """
        if job_id in self.running_jobs:
            job = self.running_jobs.pop(job_id)
            job.fail(error)
            if job.can_retry():
                job.retry()
                self.queue.append(job)
            return True
        return False

    def get_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status.
        
        Args:
            job_id: Job ID
            
        Returns:
            Status dictionary or None
        """
        # Check pending queue
        for job in self.queue:
            if job.id == job_id:
                return {
                    'id': job.id,
                    'status': job.status.value,
                    'progress': job.progress,
                    'estimated_remaining_time': job.estimated_remaining_time,
                }
        
        # Check running jobs
        if job_id in self.running_jobs:
            job = self.running_jobs[job_id]
            return {
                'id': job.id,
                'status': job.status.value,
                'progress': job.progress,
                'estimated_remaining_time': job.estimated_remaining_time,
            }
        
        return None

    def clear(self) -> int:
        """Clear all completed jobs.
        
        Returns:
            Number of jobs cleared
        """
        original_count = len(self.queue)
        self.queue = [job for job in self.queue if job.status != SearchStatus.COMPLETED]
        return original_count - len(self.queue)

    def size(self) -> int:
        """Get queue size."""
        return len(self.queue)

    def running_count(self) -> int:
        """Get count of running jobs."""
        return len(self.running_jobs)


class SearchService:
    """Service for managing and executing searches."""

    def __init__(self, max_workers: Optional[int] = None):
        """Initialize search service.
        
        Args:
            max_workers: Maximum concurrent threads (uses settings if not provided)
        """
        settings = get_settings()
        self.max_workers = max_workers or settings.search_max_concurrent_threads
        self.queue = SearchQueue()
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self._scraper_function = None

    def set_scraper(self, scraper_function) -> None:
        """Set scraper function to use for searches.
        
        Args:
            scraper_function: Function to scrape businesses
        """
        self._scraper_function = scraper_function

    def search_single(self, criteria: SearchCriteria) -> SearchJob:
        """Add single search to queue.
        
        Args:
            criteria: Search criteria
            
        Returns:
            Search job
        """
        return self.queue.add(criteria)

    def search_batch(self, criteria_list: List[SearchCriteria]) -> List[SearchJob]:
        """Add batch of searches to queue.
        
        Args:
            criteria_list: List of search criteria
            
        Returns:
            List of search jobs
        """
        return self.queue.add_many(criteria_list)

    def execute_pending(self) -> Dict[str, Any]:
        """Execute all pending searches up to max_workers.
        
        Returns:
            Dictionary with execution results
        """
        available_slots = self.max_workers - self.queue.running_count()
        pending_jobs = self.queue.get_pending(available_slots)
        
        if not pending_jobs:
            return {'executed': 0, 'jobs': []}

        results = []
        futures = {}

        for job in pending_jobs:
            self.queue.mark_running(job.id)
            future = self.executor.submit(self._execute_search, job)
            futures[future] = job

        # Collect results
        completed = []
        for future in as_completed(futures):
            job = futures[future]
            try:
                result = future.result()
                self.queue.mark_completed(job.id, result)
                completed.append(job)
            except Exception as e:
                logger.error(f"Search execution failed: {e}")
                self.queue.mark_failed(job.id, str(e))

        return {
            'executed': len(completed),
            'jobs': [job.id for job in completed]
        }

    def _execute_search(self, job: SearchJob) -> SearchResult:
        """Execute a single search job.
        
        Args:
            job: Search job to execute
            
        Returns:
            Search result
        """
        logger.info(f"Executing search job: {job.id}")
        start_time = datetime.now()
        
        result = SearchResult(
            total_found=0,
            total_saved=0,
            duplicates_found=0,
        )

        if self._scraper_function:
            try:
                businesses = self._scraper_function(job.criteria)
                result.total_found = len(businesses)
                result.total_saved = len(businesses)
                logger.info(f"Search completed: {result.total_found} businesses found")
            except Exception as e:
                logger.error(f"Scraper error: {e}")
                result.add_error(str(e))
                result.successful = False
        else:
            logger.warning("No scraper function configured")

        result.elapsed_time = (datetime.now() - start_time).total_seconds()
        return result

    def pause_job(self, job_id: str) -> bool:
        """Pause a job.
        
        Args:
            job_id: Job ID
            
        Returns:
            True if successful
        """
        for job in self.queue.queue:
            if job.id == job_id:
                job.pause()
                return True
        return False

    def resume_job(self, job_id: str) -> bool:
        """Resume a paused job.
        
        Args:
            job_id: Job ID
            
        Returns:
            True if successful
        """
        for job in self.queue.queue:
            if job.id == job_id and job.status == SearchStatus.PAUSED:
                job.resume()
                return True
        return False

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a job.
        
        Args:
            job_id: Job ID
            
        Returns:
            True if successful
        """
        job = self.queue.pop_job(job_id)
        if job:
            job.status = SearchStatus.CANCELLED
            return True
        return False

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a job.
        
        Args:
            job_id: Job ID
            
        Returns:
            Status dictionary or None
        """
        return self.queue.get_status(job_id)

    def get_queue_status(self) -> Dict[str, Any]:
        """Get overall queue status.
        
        Returns:
            Queue status dictionary
        """
        return {
            'pending': len([j for j in self.queue.queue if j.status == SearchStatus.PENDING]),
            'running': self.queue.running_count(),
            'paused': len([j for j in self.queue.queue if j.status == SearchStatus.PAUSED]),
            'total_in_queue': self.queue.size(),
        }

    def shutdown(self) -> None:
        """Shutdown the search service."""
        self.executor.shutdown(wait=True)
        logger.info("Search service shutdown complete")

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
