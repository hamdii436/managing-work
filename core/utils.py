"""Utility functions and helpers."""

import hashlib
import json
import re
from typing import Any, Callable, Dict, List, Optional, TypeVar
from urllib.parse import urlparse

T = TypeVar("T")


def sanitize_string(value: str) -> str:
    """Sanitize string by removing extra whitespace."""
    if not value:
        return ""
    return " ".join(value.split())


def validate_url(url: str) -> bool:
    """Validate if string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    # Allow digits, spaces, hyphens, plus, and parentheses
    pattern = r"^[\d\s\-\+\(\)]{7,}$"
    return re.match(pattern, phone) is not None


def generate_hash(data: str) -> str:
    """Generate SHA256 hash of data."""
    return hashlib.sha256(data.encode()).hexdigest()


def extract_domain(url: str) -> Optional[str]:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None


def format_rating(rating: Optional[float]) -> str:
    """Format rating for display."""
    if rating is None:
        return "N/A"
    return f"{rating:.1f}"


def format_phone(phone: Optional[str]) -> str:
    """Format phone number for display."""
    if not phone:
        return "N/A"
    return phone.strip()


def truncate_string(text: str, max_length: int = 100) -> str:
    """Truncate string to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def flatten_dict(d: Dict[str, Any], parent_key: str = "", sep: str = "_") -> Dict[str, Any]:
    """Flatten nested dictionary."""
    items: List[tuple] = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def chunk_list(lst: List[T], chunk_size: int) -> List[List[T]]:
    """Split list into chunks of specified size."""
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def remove_duplicates(items: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
    """Remove duplicates from list of dicts by key."""
    seen = set()
    result = []
    for item in items:
        value = item.get(key)
        if value not in seen:
            seen.add(value)
            result.append(item)
    return result


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries."""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def retry_on_exception(
    func: Callable[..., T],
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
) -> T:
    """Retry function execution on exception.

    Args:
        func: Function to execute
        max_attempts: Maximum retry attempts
        delay: Initial delay between retries
        backoff: Multiplier for delay after each attempt

    Returns:
        Function result

    Raises:
        Exception: If all attempts fail
    """
    import time

    last_exception = None
    current_delay = delay

    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            last_exception = e
            if attempt < max_attempts - 1:
                time.sleep(current_delay)
                current_delay *= backoff

    raise last_exception or Exception("Function failed after all retry attempts")


def bytes_to_human_readable(bytes_count: int) -> str:
    """Convert bytes to human readable format."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_count < 1024.0:
            return f"{bytes_count:.2f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.2f} PB"


def serialize_to_json(obj: Any) -> str:
    """Serialize object to JSON string."""
    return json.dumps(obj, default=str)


def deserialize_from_json(json_str: str) -> Any:
    """Deserialize JSON string to object."""
    return json.loads(json_str)
