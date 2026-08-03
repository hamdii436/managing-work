"""Business entity model."""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.utils import generate_hash, sanitize_string


@dataclass
class BusinessHours:
    """Business operating hours."""

    monday: Optional[str] = None
    tuesday: Optional[str] = None
    wednesday: Optional[str] = None
    thursday: Optional[str] = None
    friday: Optional[str] = None
    saturday: Optional[str] = None
    sunday: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class Location:
    """Business location information."""

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    postal_code: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class Business:
    """Business information model."""

    id: Optional[str] = None
    name: str = ""
    url: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    category: Optional[str] = None
    location: Location = field(default_factory=Location)
    hours: BusinessHours = field(default_factory=BusinessHours)
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    search_query: Optional[str] = None
    source: str = "google_maps"
    is_verified: bool = False
    is_duplicate: bool = False

    def __post_init__(self) -> None:
        """Post-initialization processing."""
        self.name = sanitize_string(self.name)
        if not self.id:
            self.id = self.generate_id()

    def generate_id(self) -> str:
        """Generate unique ID for business."""
        if not self.url:
            # Fallback ID if URL is not available
            return generate_hash(self.name + (self.address or ""))
        return generate_hash(self.url)

    def is_valid(self) -> bool:
        """Check if business data is valid."""
        return bool(self.name and (self.url or self.address))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        data["location"] = self.location.to_dict()
        data["hours"] = self.hours.to_dict()
        return data

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str)

    def __hash__(self) -> int:
        """Hash based on ID."""
        return hash(self.id)

    def __eq__(self, other: Any) -> bool:
        """Equality based on ID."""
        if not isinstance(other, Business):
            return False
        return self.id == other.id
