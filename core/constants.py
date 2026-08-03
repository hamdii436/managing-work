"""Application constants."""

# Application metadata
APP_NAME = "Google Maps Business Automation"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Your Name"
APP_DESCRIPTION = "Automated business data collection from Google Maps"

# File paths
DATA_DIR = "./data"
LOGS_DIR = "./logs"
EXPORTS_DIR = "./exports"
PLUGINS_DIR = "./plugins"
CONFIG_FILE = ".env"

# Database
DEFAULT_DB_NAME = "database.db"
DB_ECHO = False
DB_POOL_SIZE = 10
DB_POOL_RECYCLE = 3600

# Pagination
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 500

# Scraper defaults
DEFAULT_TIMEOUT = 30
DEFAULT_RETRY_ATTEMPTS = 3
DEFAULT_RETRY_DELAY = 2
DEFAULT_RATE_LIMIT_DELAY = 2

# Search defaults
DEFAULT_MAX_RESULTS = 500
DEFAULT_CONCURRENT_THREADS = 3
DEFAULT_SEARCH_TIMEOUT = 120

# Cache defaults
CACHE_TTL = 3600  # 1 hour
CACHE_MAX_SIZE = 100

# UI defaults
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800
DEFAULT_ANIMATION_DURATION = 300  # milliseconds

# API rate limiting
DEFAULT_RATE_LIMIT_REQUESTS = 100
DEFAULT_RATE_LIMIT_PERIOD = 60

# Export defaults
EXPORT_CHUNK_SIZE = 1000
CSV_CHUNK_SIZE = 5000

# Validation
MIN_RATING = 0.0
MAX_RATING = 5.0
MIN_REVIEWS = 0
PHONE_REGEX = r"^[\d\s\-\+\(\)]+$"
URL_REGEX = r"^https?://"

# Search history
MAX_HISTORY_RECORDS = 1000
HISTORY_RETENTION_DAYS = 365

# Thread pool
MAX_WORKERS = 5
MIN_WORKERS = 1

# Error messages
ERROR_NO_RESULTS = "No results found for the given criteria"
ERROR_INVALID_CONFIG = "Invalid configuration"
ERROR_DB_CONNECTION = "Could not connect to database"
ERROR_SCRAPER_TIMEOUT = "Scraper operation timed out"
ERROR_EXPORT_FAILED = "Export operation failed"
ERROR_RATE_LIMITED = "Rate limit exceeded"
ERROR_NETWORK_ERROR = "Network error occurred"

# Success messages
SUCCESS_EXPORT = "Data exported successfully"
SUCCESS_SEARCH = "Search completed successfully"
SUCCESS_SAVED = "Data saved successfully"
