"""Database models using SQLAlchemy."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, Boolean, Index, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()


class BusinessModel(Base):
    """SQLAlchemy model for Business."""

    __tablename__ = "businesses"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    url = Column(String(512), unique=True, index=True)
    address = Column(Text)
    phone = Column(String(50))
    website = Column(String(512))
    rating = Column(Float)
    review_count = Column(Integer)
    category = Column(String(100), index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    description = Column(Text)
    source = Column(String(50), default="google_maps")
    is_verified = Column(Boolean, default=False)
    is_duplicate = Column(Boolean, default=False)
    search_query = Column(String(255))
    created_at = Column(DateTime, default=datetime.now, index=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Indexes
    __table_args__ = (
        Index("idx_business_name", "name"),
        Index("idx_business_category", "category"),
        Index("idx_business_rating", "rating"),
        Index("idx_business_created", "created_at"),
    )


class SearchJobModel(Base):
    """SQLAlchemy model for SearchJob."""

    __tablename__ = "search_jobs"

    id = Column(String(64), primary_key=True, index=True)
    city = Column(String(100), nullable=False)
    district = Column(String(100))
    category = Column(String(100))
    min_rating = Column(Float)
    max_rating = Column(Float)
    min_reviews = Column(Integer)
    keywords = Column(String(255))
    status = Column(String(20), default="pending", index=True)
    total_found = Column(Integer, default=0)
    total_saved = Column(Integer, default=0)
    duplicates_found = Column(Integer, default=0)
    progress = Column(Float, default=0.0)
    estimated_remaining_time = Column(Integer)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.now, index=True)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    elapsed_time = Column(Float)

    __table_args__ = (
        Index("idx_search_status", "status"),
        Index("idx_search_created", "created_at"),
        Index("idx_search_city", "city"),
    )


class SearchHistoryModel(Base):
    """SQLAlchemy model for SearchHistory."""

    __tablename__ = "search_history"

    id = Column(String(64), primary_key=True, index=True)
    search_job_id = Column(String(64), index=True)
    business_count = Column(Integer, default=0)
    export_format = Column(String(20))
    export_path = Column(String(512))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now, index=True)

    __table_args__ = (
        Index("idx_history_created", "created_at"),
        Index("idx_history_job", "search_job_id"),
    )


class DuplicateModel(Base):
    """SQLAlchemy model for tracking duplicate detection."""

    __tablename__ = "duplicates"

    id = Column(String(64), primary_key=True, index=True)
    business_id = Column(String(64), nullable=False, index=True)
    duplicate_of = Column(String(64), nullable=False, index=True)
    similarity_score = Column(Float)
    detection_method = Column(String(50))
    detected_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        Index("idx_duplicate_business", "business_id"),
        Index("idx_duplicate_of", "duplicate_of"),
    )


class CacheModel(Base):
    """SQLAlchemy model for caching search results."""

    __tablename__ = "cache"

    id = Column(String(64), primary_key=True, index=True)
    query_hash = Column(String(64), unique=True, index=True)
    data = Column(Text)
    ttl = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime, index=True)

    __table_args__ = (
        Index("idx_cache_expires", "expires_at"),
    )


class SettingsModel(Base):
    """SQLAlchemy model for application settings."""

    __tablename__ = "settings"

    key = Column(String(100), primary_key=True, index=True)
    value = Column(Text)
    type = Column(String(20))
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
