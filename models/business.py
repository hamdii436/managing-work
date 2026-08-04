"""Business entity model."""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.utils import generate_hash, sanitize_string, validate_url, validate_phone

logger = logging.getLogger(__name__)


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

    DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    def is_open_today(self) -> bool:
        """Check if business is open today."""
        today = datetime.now().weekday()
        day_name = self.DAYS[today]
        hours = getattr(self, day_name, None)
        return hours is not None and hours.lower() != "closed"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())

    def to_csv_string(self) -> str:
        """Convert to CSV-friendly string."""
        return ";".join([f"{day}:{getattr(self, day, 'N/A')}" for day in self.DAYS])


@dataclass
class Location:
    """Business location information."""

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    postal_code: Optional[str] = None

    def is_valid(self) -> bool:
        """Check if location has valid coordinates."""
        return self.latitude is not None and self.longitude is not None

    def get_full_address(self) -> str:
        """Get complete address string."""
        parts = []
        if self.address:
            parts.append(self.address)
        if self.district:
            parts.append(self.district)
        if self.city:
            parts.append(self.city)
        if self.postal_code:
            parts.append(self.postal_code)
        return ", ".join(parts) if parts else "N/A"

    def distance_to(self, other: "Location") -> Optional[float]:
        """Calculate approximate distance to another location in km."""
        if not (self.is_valid() and other.is_valid()):
            return None
        
        # Simplified haversine formula
        from math import radians, sin, cos, sqrt, atan2
        
        lat1, lon1 = radians(self.latitude), radians(self.longitude)
        lat2, lon2 = radians(other.latitude), radians(other.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return 6371 * c  # Earth radius in km

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class Business:
    """Business information model with comprehensive validation."""

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
    tags: List[str] = field(default_factory=list)
    image_url: Optional[str] = None

    def __post_init__(self) -> None:
        """Post-initialization processing and validation."""
        self.name = sanitize_string(self.name)
        if self.address:
            self.address = sanitize_string(self.address)
        if self.description:
            self.description = sanitize_string(self.description)
        
        # Validate rating
        if self.rating is not None:
            if not (0.0 <= self.rating <= 5.0):
                logger.warning(f"Invalid rating {self.rating} for {self.name}, clamping to 0-5")
                self.rating = max(0.0, min(5.0, self.rating))
        
        # Validate review count
        if self.review_count is not None and self.review_count < 0:
            logger.warning(f"Negative review count for {self.name}, setting to 0")
            self.review_count = 0
        
        # Generate ID if not provided
        if not self.id:
            self.id = self.generate_id()

    def generate_id(self) -> str:
        """Generate unique ID for business."""
        if self.url:
            return generate_hash(self.url)
        # Fallback ID if URL is not available
        return generate_hash(self.name + (self.address or ""))

    def is_valid(self) -> bool:
        """Check if business data is valid for storage."""
        return bool(self.name and len(self.name) >= 2)

    def validate_comprehensive(self) -> tuple[bool, List[str]]:
        """Comprehensive validation returning (is_valid, error_messages)."""
        errors = []
        
        if not self.name or len(self.name) < 2:
            errors.append("Business name must be at least 2 characters")
        
        if self.url and not validate_url(self.url):
            errors.append(f"Invalid URL format: {self.url}")
        
        if self.website and not validate_url(self.website):
            errors.append(f"Invalid website URL: {self.website}")
        
        if self.phone and not validate_phone(self.phone):
            errors.append(f"Invalid phone number format: {self.phone}")
        
        if self.rating is not None and not (0.0 <= self.rating <= 5.0):
            errors.append(f"Rating must be between 0 and 5, got {self.rating}")
        
        if self.review_count is not None and self.review_count < 0:
            errors.append("Review count cannot be negative")
        
        return len(errors) == 0, errors

    def get_quality_score(self) -> float:
        """Calculate data quality score (0.0 to 1.0)."""
        score = 0.0
        
        # Name quality
        if self.name and len(self.name) >= 3:
            score += 0.15
        
        # Contact info
        if self.phone:
            score += 0.15
        if self.website:
            score += 0.15
        
        # Location
        if self.location.is_valid():
            score += 0.15
        
        # Rating and reviews
        if self.rating:
            score += 0.15
        if self.review_count and self.review_count > 0:
            score += 0.10
        
        # Metadata
        if self.hours.monday:
            score += 0.05
        if self.description:
            score += 0.05
        
        return min(1.0, score)

    def is_complete(self) -> bool:
        """Check if business has most information filled."""
        return self.get_quality_score() >= 0.7

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        data["location"] = self.location.to_dict()
        data["hours"] = self.hours.to_dict()
        data["quality_score"] = self.get_quality_score()
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

    def __lt__(self, other: "Business") -> bool:
        """Sort by rating (descending)."""
        if not isinstance(other, Business):
            return NotImplemented
        self_rating = self.rating or 0.0
        other_rating = other.rating or 0.0
        return self_rating > other_rating

    def __repr__(self) -> str:
        """String representation."""
        return f"Business(id={self.id}, name='{self.name}', rating={self.rating}, reviews={self.review_count})"
