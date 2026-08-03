"""Search history service for tracking past searches."""

import logging
import uuid
from typing import List, Optional

from database.db_manager import get_session
from database.models import SearchHistoryModel
from database.repository import BaseRepository
from models.search import SearchHistory, SearchJob

logger = logging.getLogger(__name__)


class HistoryService:
    """Service for managing search history."""

    def __init__(self) -> None:
        """Initialize history service."""
        self.db_session = get_session()
        self.repository = BaseRepository(self.db_session, SearchHistoryModel)

    def add_to_history(
        self,
        search_job: SearchJob,
        business_count: int,
        export_path: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> SearchHistory:
        """Add search to history.

        Args:
            search_job: Completed search job
            business_count: Number of businesses found
            export_path: Path where data was exported
            notes: Optional notes

        Returns:
            SearchHistory object
        """
        history = SearchHistory(
            id=str(uuid.uuid4()),
            search_job=search_job,
            business_count=business_count,
            export_path=export_path,
            notes=notes,
        )

        try:
            db_history = SearchHistoryModel(
                id=history.id,
                search_job_id=search_job.id,
                business_count=business_count,
                export_path=export_path,
                notes=notes,
            )
            self.repository.add(db_history)
            logger.info(f"Added search to history: {history.id}")
            return history
        except Exception as e:
            logger.error(f"Failed to add to history: {e}")
            raise

    def get_history(self, history_id: str) -> Optional[SearchHistory]:
        """Get history record by ID.

        Args:
            history_id: History ID

        Returns:
            SearchHistory or None
        """
        try:
            db_history = self.repository.get_by_id(history_id)
            if db_history:
                return self._model_to_history(db_history)
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
        return None

    def get_all_history(self, skip: int = 0, limit: int = 100) -> List[SearchHistory]:
        """Get all history records with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            List of SearchHistory objects
        """
        try:
            db_histories = self.repository.get_all(skip, limit)
            return [self._model_to_history(h) for h in db_histories if h]
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            raise

    def get_recent_searches(self, limit: int = 10) -> List[SearchHistory]:
        """Get recent searches.

        Args:
            limit: Number of recent searches to return

        Returns:
            List of SearchHistory objects
        """
        try:
            db_histories = (
                self.db_session.query(SearchHistoryModel)
                .order_by(SearchHistoryModel.created_at.desc())
                .limit(limit)
                .all()
            )
            return [self._model_to_history(h) for h in db_histories if h]
        except Exception as e:
            logger.error(f"Failed to get recent searches: {e}")
            raise

    def delete_history(self, history_id: str) -> bool:
        """Delete history record.

        Args:
            history_id: History ID

        Returns:
            True if deleted
        """
        try:
            return self.repository.delete(history_id)
        except Exception as e:
            logger.error(f"Failed to delete history: {e}")
            raise

    def get_total_searches(self) -> int:
        """Get total number of searches in history.

        Returns:
            Total count
        """
        try:
            return self.repository.count()
        except Exception as e:
            logger.error(f"Failed to get search count: {e}")
            raise

    def _model_to_history(self, db_history: SearchHistoryModel) -> Optional[SearchHistory]:
        """Convert database model to SearchHistory."""
        if not db_history:
            return None

        # Note: Full SearchJob reconstruction would require additional data
        # For now, we return basic history info
        return SearchHistory(
            id=db_history.id,
            search_job=None,  # Would need to reconstruct from search_job_id
            business_count=db_history.business_count,
            export_path=db_history.export_path,
            notes=db_history.notes,
        )

    def close(self) -> None:
        """Close database session."""
        if self.db_session:
            self.db_session.close()
