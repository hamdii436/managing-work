"""Input validators."""

import re
from typing import Optional


class Validators:
    """Input validation utilities."""

    @staticmethod
    def validate_city(city: str) -> bool:
        """Validate city name.

        Args:
            city: City name

        Returns:
            True if valid
        """
        return bool(city and len(city) >= 2)

    @staticmethod
    def validate_category(category: str) -> bool:
        """Validate category name.

        Args:
            category: Category name

        Returns:
            True if valid
        """
        return bool(category and len(category) >= 2)

    @staticmethod
    def validate_rating(rating: float) -> bool:
        """Validate rating value.

        Args:
            rating: Rating value

        Returns:
            True if valid
        """
        return 0.0 <= rating <= 5.0

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address.

        Args:
            email: Email address

        Returns:
            True if valid
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL.

        Args:
            url: URL string

        Returns:
            True if valid
        """
        pattern = r"^https?://"
        return bool(re.match(pattern, url))
