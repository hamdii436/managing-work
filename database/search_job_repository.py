"""Search job repository."""

import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from core.enums import SearchStatus
from database.base_repository import BaseRepository
from database.models import SearchJobModel

logger = logging.getLogger(__name__)


class SearchJobRepository(BaseRepository[SearchJobModel]):
    """Repository for search job operations."""

    def __init__(self, db_session: Session) -> None:
        """Initialize search job repository."""
        super().__init__(db_session, SearchJobModel)

    def get_by_status(self, status: SearchStatus, skip: int = 0, limit: int = 100) -> List[SearchJobModel]:
        """Get search jobs by status.
        
        Args:
            status: Search status
            skip: Number to skip
            limit: Max results
            
        Returns:
            List of search jobs
        """
        try:
            return self.db_session.query(SearchJobModel).filter(
                SearchJobModel.status == status.value
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to get jobs by status: {e}")
            return []

    def get_pending_jobs(self) -> List[SearchJobModel]:
        """Get all pending search jobs.
        
        Returns:
            List of pending jobs
        """
        try:
            return self.db_session.query(SearchJobModel).filter(
                SearchJobModel.status == SearchStatus.PENDING.value
            ).all()
        except Exception as e:
            logger.error(f"Failed to get pending jobs: {e}")
            return []

    def get_running_jobs(self) -> List[SearchJobModel]:
        """Get all running search jobs.
        
        Returns:
            List of running jobs
        """
        try:
            return self.db_session.query(SearchJobModel).filter(
                SearchJobModel.status == SearchStatus.RUNNING.value
            ).all()
        except Exception as e:
            logger.error(f"Failed to get running jobs: {e}")
            return []

    def get_failed_jobs(self) -> List[SearchJobModel]:
        """Get all failed search jobs.
        
        Returns:
            List of failed jobs
        """
        try:
            return self.db_session.query(SearchJobModel).filter(
                SearchJobModel.status == SearchStatus.FAILED.value
            ).all()
        except Exception as e:
            logger.error(f"Failed to get failed jobs: {e}")
            return []

    def get_paused_jobs(self) -> List[SearchJobModel]:
        """Get all paused search jobs.
        
        Returns:
            List of paused jobs
        """
        try:
            return self.db_session.query(SearchJobModel).filter(
                SearchJobModel.status == SearchStatus.PAUSED.value
            ).all()
        except Exception as e:
            logger.error(f"Failed to get paused jobs: {e}")
            return []

    def count_by_status(self, status: SearchStatus) -> int:
        """Count jobs by status.
        
        Args:
            status: Search status
            
        Returns:
            Count of jobs
        """
        try:
            return self.db_session.query(SearchJobModel).filter(
                SearchJobModel.status == status.value
            ).count()
        except Exception as e:
            logger.error(f"Failed to count jobs by status: {e}")
            return 0

    def get_resumable_jobs(self) -> List[SearchJobModel]:
        """Get jobs that can be resumed (paused or failed).
        
        Returns:
            List of resumable jobs
        """
        try:
            return self.db_session.query(SearchJobModel).filter(
                SearchJobModel.status.in_([
                    SearchStatus.PAUSED.value,
                    SearchStatus.FAILED.value
                ])
            ).all()
        except Exception as e:
            logger.error(f"Failed to get resumable jobs: {e}")
            return []

    def get_recent_jobs(self, limit: int = 10) -> List[SearchJobModel]:
        """Get most recent search jobs.
        
        Args:
            limit: Number of results
            
        Returns:
            List of recent jobs
        """
        try:
            return self.db_session.query(SearchJobModel).order_by(
                SearchJobModel.created_at.desc()
            ).limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to get recent jobs: {e}")
            return []

    def get_completed_jobs(self, skip: int = 0, limit: int = 100) -> List[SearchJobModel]:
        """Get completed search jobs.
        
        Args:
            skip: Number to skip
            limit: Max results
            
        Returns:
            List of completed jobs
        """
        try:
            return self.db_session.query(SearchJobModel).filter(
                SearchJobModel.status == SearchStatus.COMPLETED.value
            ).order_by(
                SearchJobModel.completed_at.desc()
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to get completed jobs: {e}")
            return []

    def update_status(self, job_id: str, status: SearchStatus) -> bool:
        """Update job status.
        
        Args:
            job_id: Job ID
            status: New status
            
        Returns:
            True if successful, False otherwise
        """
        try:
            job = self.get_by_id(job_id)
            if job:
                job.status = status.value
                self.update(job)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update job status: {e}")
            return False

    def update_progress(self, job_id: str, progress: float, remaining_time: Optional[int] = None) -> bool:
        """Update job progress.
        
        Args:
            job_id: Job ID
            progress: Progress 0.0-1.0
            remaining_time: Estimated remaining time in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            job = self.get_by_id(job_id)
            if job:
                job.progress = max(0.0, min(1.0, progress))
                if remaining_time is not None:
                    job.estimated_remaining_time = remaining_time
                self.update(job)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to update job progress: {e}")
            return False

    def delete_old_jobs(self, days: int = 30) -> bool:
        """Delete jobs older than specified days.
        
        Args:
            days: Number of days
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.now() - timedelta(days=days)
            self.db_session.query(SearchJobModel).filter(
                SearchJobModel.created_at < cutoff_date
            ).delete()
            self.db_session.commit()
            logger.info(f"Deleted search jobs older than {days} days")
            return True
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Failed to delete old jobs: {e}")
            return False

    def get_jobs_by_criteria(self, city: Optional[str] = None, category: Optional[str] = None,
                             status: Optional[SearchStatus] = None, skip: int = 0,
                             limit: int = 100) -> List[SearchJobModel]:
        """Get jobs by multiple criteria.
        
        Args:
            city: City name (optional)
            category: Category (optional)
            status: Job status (optional)
            skip: Number to skip
            limit: Max results
            
        Returns:
            List of jobs matching criteria
        """
        try:
            query = self.db_session.query(SearchJobModel)
            
            if city:
                query = query.filter(SearchJobModel.city == city)
            if category:
                query = query.filter(SearchJobModel.category == category)
            if status:
                query = query.filter(SearchJobModel.status == status.value)
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to get jobs by criteria: {e}")
            return []
