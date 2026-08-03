"""Data formatting utilities."""

from typing import Optional
from datetime import datetime


class Formatters:
    """Data formatting utilities."""

    @staticmethod
    def format_rating(rating: Optional[float]) -> str:
        """Format rating for display.

        Args:
            rating: Rating value

        Returns:
            Formatted rating string
        """
        if rating is None:
            return "N/A"
        return f"{rating:.1f}★"

    @staticmethod
    def format_phone(phone: Optional[str]) -> str:
        """Format phone number.

        Args:
            phone: Phone number

        Returns:
            Formatted phone number
        """
        if not phone:
            return "N/A"
        return phone.strip()

    @staticmethod
    def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Format datetime.

        Args:
            dt: Datetime object
            format_str: Format string

        Returns:
            Formatted datetime string
        """
        if not dt:
            return "N/A"
        return dt.strftime(format_str)

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size for display.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string
        """
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"

    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        """Truncate text to maximum length.

        Args:
            text: Text to truncate
            max_length: Maximum length

        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
