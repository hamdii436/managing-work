"""Search queue service for managing concurrent searches."""

import logging
import uuid
from collections import deque
from typing import Deque, List, Optional

from models.search import SearchCriteria, SearchJob

logger = logging.getLogger(__name__)


class SearchQueueService:
    """Service for managing search queue."""

    def __init__(self, max_concurrent: int = 3) -> None:
        """Initialize search queue service.

        Args:
            max_concurrent: Maximum concurrent searches
        """
        self.queue: Deque[SearchJob] = deque()
        self.active_searches: List[SearchJob] = []
        self.completed_searches: List[SearchJob] = []
        self.max_concurrent = max_concurrent

    def enqueue(self, criteria: SearchCriteria) -> SearchJob:
        """Add search to queue.

        Args:
            criteria: Search criteria

        Returns:
            SearchJob object
        """
        job = SearchJob(
            id=str(uuid.uuid4()),
            criteria=criteria,
        )
        self.queue.append(job)
        logger.info(f"Enqueued search: {job.id}")
        return job

    def enqueue_multiple(self, criteria_list: List[SearchCriteria]) -> List[SearchJob]:
        """Add multiple searches to queue.

        Args:
            criteria_list: List of search criteria

        Returns:
            List of SearchJob objects
        """
        jobs = [self.enqueue(criteria) for criteria in criteria_list]
        logger.info(f"Enqueued {len(jobs)} searches")
        return jobs

    def dequeue(self) -> Optional[SearchJob]:
        """Get next search from queue.

        Returns:
            SearchJob or None if queue is empty or at max concurrency
        """
        if len(self.active_searches) >= self.max_concurrent:
            return None

        if self.queue:
            job = self.queue.popleft()
            self.active_searches.append(job)
            logger.info(f"Dequeued search: {job.id}")
            return job

        return None

    def get_next_available(self) -> Optional[SearchJob]:
        """Get next available search without modifying queue.

        Returns:
            SearchJob or None
        """
        if self.queue and len(self.active_searches) < self.max_concurrent:
            return self.queue[0]
        return None

    def mark_completed(self, job_id: str) -> bool:
        """Mark search as completed.

        Args:
            job_id: Search job ID

        Returns:
            True if found and marked
        """
        for i, job in enumerate(self.active_searches):
            if job.id == job_id:
                self.active_searches.pop(i)
                self.completed_searches.append(job)
                logger.info(f"Marked search as completed: {job_id}")
                return True
        return False

    def mark_failed(self, job_id: str, error: str) -> bool:
        """Mark search as failed.

        Args:
            job_id: Search job ID
            error: Error message

        Returns:
            True if found and marked
        """
        for i, job in enumerate(self.active_searches):
            if job.id == job_id:
                job.error = error
                self.active_searches.pop(i)
                self.completed_searches.append(job)
                logger.info(f"Marked search as failed: {job_id}")
                return True
        return False

    def pause(self, job_id: str) -> bool:
        """Pause active search.

        Args:
            job_id: Search job ID

        Returns:
            True if paused
        """
        for job in self.active_searches:
            if job.id == job_id:
                from core.enums import SearchStatus
                job.status = SearchStatus.PAUSED
                return True
        return False

    def resume(self, job_id: str) -> bool:
        """Resume paused search.

        Args:
            job_id: Search job ID

        Returns:
            True if resumed
        """
        # Search in completed searches for paused job
        for job in self.completed_searches:
            if job.id == job_id:
                from core.enums import SearchStatus
                if job.status.value == "paused":
                    job.status = SearchStatus.PENDING
                    self.queue.append(job)
                    self.completed_searches.remove(job)
                    return True
        return False

    def get_queue_size(self) -> int:
        """Get number of pending searches."""
        return len(self.queue)

    def get_active_count(self) -> int:
        """Get number of active searches."""
        return len(self.active_searches)

    def get_completed_count(self) -> int:
        """Get number of completed searches."""
        return len(self.completed_searches)

    def clear_queue(self) -> None:
        """Clear all pending searches."""
        self.queue.clear()
        logger.info("Search queue cleared")

    def get_all_jobs(self) -> List[SearchJob]:
        """Get all jobs (pending, active, completed)."""
        return list(self.queue) + self.active_searches + self.completed_searches

    def get_active_searches(self) -> List[SearchJob]:
        """Get all active searches."""
        return self.active_searches.copy()

    def get_pending_searches(self) -> List[SearchJob]:
        """Get all pending searches."""
        return list(self.queue)
