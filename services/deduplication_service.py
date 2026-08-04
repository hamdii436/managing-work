"""Deduplication service for detecting duplicate businesses."""

import logging
from typing import List, Optional, Tuple, Dict, Any

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
        if not (0.0 <= similarity_threshold <= 1.0):
            raise ValueError("Similarity threshold must be between 0.0 and 1.0")
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
                    logger.debug(f"Found duplicate: {business1.name} <-> {business2.name} (score: {similarity:.2f})")
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

            if not is_duplicate and business.name not in seen_ids:
                result.append(business)
                seen_ids.add(business.name)

        logger.info(f"Deduplication: {len(businesses)} -> {len(result)} businesses")
        return result

    def is_duplicate(self, business1: Business, business2: Business) -> bool:
        """Check if two businesses are duplicates.
        
        Args:
            business1: First business
            business2: Second business
            
        Returns:
            True if businesses are duplicates
        """
        return self._calculate_similarity(business1, business2) >= self.similarity_threshold

    def _calculate_similarity(self, business1: Business, business2: Business) -> float:
        """Calculate similarity score between two businesses.

        Args:
            business1: First business
            business2: Second business

        Returns:
            Similarity score (0.0 to 1.0)
        """
        scores = []

        # Compare names (highest weight - 40%)
        if business1.name and business2.name:
            name_similarity = self._string_similarity(business1.name, business2.name)
            scores.append(name_similarity * 0.4)

        # Compare URLs (high weight - 30%)
        if business1.url and business2.url:
            url_similarity = 1.0 if business1.url == business2.url else 0.0
            scores.append(url_similarity * 0.3)

        # Compare addresses (medium weight - 20%)
        if business1.location and business2.location:
            addr1 = business1.location.address or ""
            addr2 = business2.location.address or ""
            if addr1 and addr2:
                address_similarity = self._string_similarity(addr1, addr2)
                scores.append(address_similarity * 0.2)

        # Compare phone (medium weight - 10%)
        if business1.phone and business2.phone:
            phone_similarity = 1.0 if business1.phone == business2.phone else 0.0
            scores.append(phone_similarity * 0.1)

        return sum(scores) if scores else 0.0

    def merge_duplicates(self, business1: Business, business2: Business) -> Business:
        """Merge two duplicate businesses, keeping best data from each.
        
        Args:
            business1: First business
            business2: Second business
            
        Returns:
            Merged business
        """
        # Use higher quality score as base
        if self._get_quality_score(business1) >= self._get_quality_score(business2):
            primary = business1
            secondary = business2
        else:
            primary = business2
            secondary = business1

        # Create merged business
        merged = Business(
            name=primary.name,
            city=primary.city,
            district=primary.district or secondary.district,
            category=primary.category or secondary.category,
            phone=primary.phone or secondary.phone,
            website=primary.website or secondary.website,
            email=primary.email or secondary.email,
            url=primary.url or secondary.url,
            rating=max(primary.rating or 0, secondary.rating or 0),
            review_count=max(primary.review_count or 0, secondary.review_count or 0),
            description=primary.description or secondary.description,
        )

        # Merge location
        if primary.location:
            merged.location = primary.location
        elif secondary.location:
            merged.location = secondary.location

        # Merge hours
        if primary.hours:
            merged.hours = primary.hours
        elif secondary.hours:
            merged.hours = secondary.hours

        logger.info(f"Merged duplicates: {primary.name} + {secondary.name}")
        return merged

    def get_duplicate_groups(self, businesses: List[Business]) -> List[List[Business]]:
        """Group duplicate businesses together.
        
        Args:
            businesses: List of businesses
            
        Returns:
            List of duplicate groups
        """
        groups = []
        used_indices = set()

        for i, business1 in enumerate(businesses):
            if i in used_indices:
                continue

            group = [business1]
            used_indices.add(i)

            for j, business2 in enumerate(businesses):
                if j <= i or j in used_indices:
                    continue

                if self.is_duplicate(business1, business2):
                    group.append(business2)
                    used_indices.add(j)

            if len(group) > 1:
                groups.append(group)

        return groups

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
            score += (business.rating / 5.0) * 0.3

        # Has reviews
        if business.review_count:
            score += min(business.review_count / 100.0, 1.0) * 0.2

        # Has website
        if business.website:
            score += 0.2

        # Has phone
        if business.phone:
            score += 0.15

        # Has description
        if business.description:
            score += 0.1

        # Has complete location
        if business.location and business.location.latitude and business.location.longitude:
            score += 0.05

        return min(score, 1.0)

    def get_summary(self, businesses: List[Business]) -> Dict[str, Any]:
        """Get deduplication analysis summary.
        
        Args:
            businesses: List of businesses
            
        Returns:
            Summary dictionary
        """
        duplicates = self.find_duplicates(businesses)
        duplicate_businesses = set()
        for b1, b2, _ in duplicates:
            duplicate_businesses.add(b1.name)
            duplicate_businesses.add(b2.name)

        return {
            'total_businesses': len(businesses),
            'duplicate_pairs': len(duplicates),
            'affected_businesses': len(duplicate_businesses),
            'threshold': self.similarity_threshold,
            'unique_after_dedup': len(self.remove_duplicates(businesses)),
        }

    def set_threshold(self, threshold: float) -> None:
        """Update similarity threshold.
        
        Args:
            threshold: New threshold (0.0-1.0)
        """
        if not (0.0 <= threshold <= 1.0):
            raise ValueError("Threshold must be between 0.0 and 1.0")
        old_threshold = self.similarity_threshold
        self.similarity_threshold = threshold
        logger.info(f"Deduplication threshold updated from {old_threshold} to {threshold}")
