"""Custom exceptions for the application."""

from typing import Optional


class ApplicationError(Exception):
    """Base exception for the application."""

    def __init__(self, message: str, code: Optional[str] = None) -> None:
        """Initialize the exception.

        Args:
            message: Error message
            code: Optional error code for categorization
        """
        self.message = message
        self.code = code or "UNKNOWN_ERROR"
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation."""
        return f"[{self.code}] {self.message}"


class ConfigurationError(ApplicationError):
    """Raised when configuration is invalid."""

    def __init__(self, message: str) -> None:
        super().__init__(message, "CONFIG_ERROR")


class DatabaseError(ApplicationError):
    """Raised when database operation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, "DB_ERROR")


class ScraperError(ApplicationError):
    """Raised when scraper encounters an error."""

    def __init__(self, message: str) -> None:
        super().__init__(message, "SCRAPER_ERROR")


class ExportError(ApplicationError):
    """Raised when export operation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, "EXPORT_ERROR")


class ValidationError(ApplicationError):
    """Raised when validation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, "VALIDATION_ERROR")


class RateLimitError(ApplicationError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str, retry_after: Optional[int] = None) -> None:
        super().__init__(message, "RATE_LIMIT_ERROR")
        self.retry_after = retry_after


class NetworkError(ApplicationError):
    """Raised when network operation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, "NETWORK_ERROR")


class PluginError(ApplicationError):
    """Raised when plugin operation fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message, "PLUGIN_ERROR")
