"""Search-related models."""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.enums import ExportFormat, SearchStatus

logger = logging.getLogger(__name__)


@dataclass
class SearchCriteria:
    """Search criteria for business search with validation."""

    city: str
    district: Optional[str] = None
    category: Optional[str] = None
    min_rating: Optional[float] = None
    max_rating: Optional[float] = None
    min_reviews: Optional[int] = None
    keywords: Optional[str] = None
    exclude_keywords: Optional[str] = None
    max_results: int = 500
    language: str = "en"

    def __post_init__(self) -> None:
        """Validate criteria on initialization."""
        if not self.city or len(self.city) < 2:
            raise ValueError("City name must be at least 2 characters")
        
        if self.min_rating is not None and not (0.0 <= self.min_rating <= 5.0):
            raise ValueError("Minimum rating must be between 0 and 5")
        
        if self.max_rating is not None and not (0.0 <= self.max_rating <= 5.0):
            raise ValueError("Maximum rating must be between 0 and 5")
        
        if self.min_rating and self.max_rating:
            if self.min_rating > self.max_rating:
                raise ValueError("Minimum rating cannot be greater than maximum")
        
        if self.min_reviews is not None and self.min_reviews < 0:
            raise ValueError("Minimum reviews cannot be negative")
        
        if self.max_results <= 0:
            raise ValueError("Maximum results must be positive")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_query_string(self) -> str:
        """Convert to search query string for web scraping."""
        parts = [self.city]
        if self.district:
            parts.append(self.district)
        if self.category:
            parts.append(self.category)
        if self.keywords:
            parts.append(self.keywords)
        return ", ".join(parts)

    def get_hash(self) -> str:
        """Get hash of criteria for caching."""
        from core.utils import generate_hash
        return generate_hash(self.to_query_string())

    def matches_business(self, business_dict: Dict[str, Any]) -> bool:
        """Check if a business matches these criteria."""
        if self.min_rating and business_dict.get("rating", 0) < self.min_rating:
            return False
        
        if self.max_rating and business_dict.get("rating", 5) > self.max_rating:
            return False
        
        if self.min_reviews and business_dict.get("review_count", 0) < self.min_reviews:
            return False
        
        if self.exclude_keywords:
            exclude_list = [k.lower() for k in self.exclude_keywords.split(",")]
            business_name = business_dict.get("name", "").lower()
            if any(excl in business_name for excl in exclude_list):
                return False
        
        return True


@dataclass
class SearchResult:
    """Result of a search operation."""

    total_found: int
    total_saved: int
    duplicates_found: int
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    elapsed_time: float = 0.0
    successful: bool = True

    def add_error(self, error: str) -> None:
        """Add error message."""
        self.errors.append(error)
        self.successful = False

    def add_warning(self, warning: str) -> None:
        """Add warning message."""
        self.warnings.append(warning)

    def get_summary(self) -> str:
        """Get human-readable summary."""
        lines = [
            f"Total Found: {self.total_found}",
            f"Total Saved: {self.total_saved}",
            f"Duplicates: {self.duplicates_found}",
            f"Time: {self.elapsed_time:.2f}s",
        ]
        if self.errors:
            lines.append(f"Errors: {len(self.errors)}")
        if self.warnings:
            lines.append(f"Warnings: {len(self.warnings)}")
        return " | ".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class SearchJob:
    """Search job for execution with complete tracking."""

    id: str
    criteria: SearchCriteria
    status: SearchStatus = SearchStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[SearchResult] = None
    error: Optional[str] = None
    progress: float = 0.0  # 0.0 to 1.0
    estimated_remaining_time: Optional[int] = None  # in seconds
    retry_count: int = 0
    max_retries: int = 3

    def start(self) -> None:
        """Mark job as started."""
        self.status = SearchStatus.RUNNING
        self.started_at = datetime.now()
        self.progress = 0.0

    def complete(self, result: SearchResult) -> None:
        """Mark job as completed."""
        self.status = SearchStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result
        self.progress = 1.0

    def fail(self, error: str) -> None:
        """Mark job as failed."""
        self.status = SearchStatus.FAILED
        self.error = error
        self.completed_at = datetime.now()

    def pause(self) -> None:
        """Pause the job."""
        self.status = SearchStatus.PAUSED

    def resume(self) -> None:
        """Resume the job."""
        self.status = SearchStatus.PENDING

    def can_retry(self) -> bool:
        """Check if job can be retried."""
        return self.retry_count < self.max_retries

    def retry(self) -> None:
        """Mark for retry."""
        if self.can_retry():
            self.retry_count += 1
            self.status = SearchStatus.PENDING
            self.error = None

    def get_duration(self) -> Optional[float]:
        """Get job duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def is_finished(self) -> bool:
        """Check if job is in a finished state."""
        return self.status in (SearchStatus.COMPLETED, SearchStatus.FAILED, SearchStatus.CANCELLED)

    def is_active(self) -> bool:
        """Check if job is currently running."""
        return self.status == SearchStatus.RUNNING

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        if self.started_at:
            data["started_at"] = self.started_at.isoformat()
        if self.completed_at:
            data["completed_at"] = self.completed_at.isoformat()
        if self.result:
            data["result"] = self.result.to_dict()
        data["status"] = self.status.value
        return data

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)

    def __repr__(self) -> str:
        """String representation."""
        return f"SearchJob(id={self.id}, status={self.status.value}, progress={self.progress:.1%})"


@dataclass
class SearchHistory:
    """Search history record with metadata."""

    id: str
    search_job: SearchJob
    business_count: int
    export_format: Optional[ExportFormat] = None
    export_path: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)

    def add_tag(self, tag: str) -> None:
        """Add tag to history."""
        if tag not in self.tags:
            self.tags.append(tag)

    def get_summary(self) -> str:
        """Get human-readable summary."""
        duration = self.search_job.get_duration()
        return (
            f"Search: {self.search_job.criteria.to_query_string()} | "
            f"Found: {self.business_count} | "
            f"Status: {self.search_job.status.value} | "
            f"Duration: {duration:.1f}s" if duration else "Duration: N/A"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "search_job": self.search_job.to_dict(),
            "business_count": self.business_count,
            "export_format": self.export_format.value if self.export_format else None,
            "export_path": self.export_path,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "tags": self.tags,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)

    def __repr__(self) -> str:
        """String representation."""
        return f"SearchHistory(id={self.id}, businesses={self.business_count}, created={self.created_at.strftime('%Y-%m-%d %H:%M')})"
