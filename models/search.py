"""Search-related models."""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.enums import ExportFormat, SearchStatus


@dataclass
class SearchCriteria:
    """Search criteria for business search."""

    city: str
    district: Optional[str] = None
    category: Optional[str] = None
    min_rating: Optional[float] = None
    max_rating: Optional[float] = None
    min_reviews: Optional[int] = None
    keywords: Optional[str] = None
    exclude_keywords: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_query_string(self) -> str:
        """Convert to search query string."""
        parts = [self.city]
        if self.district:
            parts.append(self.district)
        if self.category:
            parts.append(self.category)
        if self.keywords:
            parts.append(self.keywords)
        return ", ".join(parts)


@dataclass
class SearchResult:
    """Result of a search operation."""

    total_found: int
    total_saved: int
    duplicates_found: int
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    elapsed_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class SearchJob:
    """Search job for execution."""

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
        return data

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)


@dataclass
class SearchHistory:
    """Search history record."""

    id: str
    search_job: SearchJob
    business_count: int
    export_format: Optional[ExportFormat] = None
    export_path: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "search_job": self.search_job.to_dict(),
            "business_count": self.business_count,
            "export_format": self.export_format.value if self.export_format else None,
            "export_path": self.export_path,
            "notes": self.notes,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)
