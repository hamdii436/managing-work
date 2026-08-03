"""Deduplication service for detecting duplicate businesses."""

import logging
from typing import List, Optional, Tuple

from difflib import SequenceMatcher

from models.business import Business

logger = logging.getLogger(__name__)


class DeduplicationService:
    """Service for detecting and handling duplicate businesses."""

    def __init__(self, similarity_threshold: float = 0.85) -> None:
        """Initialize deduplication service.

        Args:
            similarity_threshold: Threshold for considering items as duplicates (0.0 to 1.0)
        """
        self.similarity_threshold = similarity_threshold

    def find_duplicates(self, businesses: List[Business]) -> List[Tuple[Business, Business, float]]:
        """Find duplicate businesses in list.

        Args:
            businesses: List of businesses to check

        Returns:
            List of (business1, business2, similarity_score) tuples
        """
        duplicates = []
        for i, business1 in enumerate(businesses):
            for business2 in businesses[i + 1 :]:
                similarity = self._calculate_similarity(business1, business2)
                if similarity >= self.similarity_threshold:
                    duplicates.append((business1, business2, similarity))
        return duplicates

    def remove_duplicates(self, businesses: List[Business]) -> List[Business]:
        """Remove duplicates from list, keeping the highest quality record.

        Args:
            businesses: List of businesses

        Returns:
            Deduplicated list
        """
        if not businesses:
            return []

        seen_ids = set()
        result = []

        for business in sorted(businesses, key=self._get_quality_score, reverse=True):
            # Check if already added (or if duplicate of already added)
            is_duplicate = False
            for seen_business in result:
                if self._calculate_similarity(business, seen_business) >= self.similarity_threshold:
                    is_duplicate = True
                    break

            if not is_duplicate and business.id not in seen_ids:
                result.append(business)
                seen_ids.add(business.id)

        return result

    def _calculate_similarity(self, business1: Business, business2: Business) -> float:
        """Calculate similarity score between two businesses.

        Args:
            business1: First business
            business2: Second business

        Returns:
            Similarity score (0.0 to 1.0)
        """
        scores = []

        # Compare names (highest weight)
        if business1.name and business2.name:
            name_similarity = self._string_similarity(business1.name, business2.name)
            scores.append(name_similarity * 0.4)

        # Compare URLs (high weight)
        if business1.url and business2.url:
            url_similarity = 1.0 if business1.url == business2.url else 0.0
            scores.append(url_similarity * 0.3)

        # Compare addresses (medium weight)
        if business1.address and business2.address:
            address_similarity = self._string_similarity(business1.address, business2.address)
            scores.append(address_similarity * 0.2)

        # Compare phone (medium weight)
        if business1.phone and business2.phone:
            phone_similarity = 1.0 if business1.phone == business2.phone else 0.0
            scores.append(phone_similarity * 0.1)

        return sum(scores) if scores else 0.0

    def _string_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity using sequence matching.

        Args:
            str1: First string
            str2: Second string

        Returns:
            Similarity score (0.0 to 1.0)
        """
        if not str1 or not str2:
            return 0.0
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    def _get_quality_score(self, business: Business) -> float:
        """Calculate quality score for a business record.

        Args:
            business: Business object

        Returns:
            Quality score
        """
        score = 0.0

        # Has rating (higher is better)
        if business.rating:
            score += business.rating / 5.0 * 0.3

        # Has reviews
        if business.review_count:
            score += min(business.review_count / 100.0, 1.0) * 0.2

        # Has website
        if business.website:
            score += 0.2

        # Has phone
        if business.phone:
            score += 0.15

        # Is verified
        if business.is_verified:
            score += 0.15

        return score

    def mark_duplicates(self, businesses: List[Business], keep_business: Business) -> None:
        """Mark businesses as duplicates of a kept business.

        Args:
            businesses: List of potential duplicates
            keep_business: Business to keep
        """
        for business in businesses:
            if business.id != keep_business.id:
                if self._calculate_similarity(business, keep_business) >= self.similarity_threshold:
                    business.is_duplicate = True
