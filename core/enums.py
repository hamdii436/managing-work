"""Enumerations for the application."""

from enum import Enum, auto


class SearchStatus(str, Enum):
    """Search execution status."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExportFormat(str, Enum):
    """Supported export formats."""

    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    SQLITE = "sqlite"


class SortOrder(str, Enum):
    """Sort order for results."""

    ASCENDING = "asc"
    DESCENDING = "desc"


class Theme(str, Enum):
    """Application theme."""

    DARK = "dark"
    LIGHT = "light"


class BrowserType(str, Enum):
    """Supported browser types."""

    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


class LogLevel(str, Enum):
    """Log levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class UIComponent(str, Enum):
    """UI component identifiers."""

    HOME_PAGE = "home_page"
    SEARCH_PAGE = "search_page"
    RESULTS_PAGE = "results_page"
    HISTORY_PAGE = "history_page"
    SETTINGS_PAGE = "settings_page"


class FieldType(str, Enum):
    """Business data field types."""

    NAME = "name"
    ADDRESS = "address"
    PHONE = "phone"
    WEBSITE = "website"
    RATING = "rating"
    REVIEWS = "reviews"
    HOURS = "hours"
    LATITUDE = "latitude"
    LONGITUDE = "longitude"
    URL = "url"
    CATEGORY = "category"
