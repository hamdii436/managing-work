"""Export configuration models."""

from dataclasses import dataclass
from typing import Optional

from core.enums import ExportFormat


@dataclass
class ExportConfig:
    """Configuration for data export."""

    format: ExportFormat
    output_path: str
    include_headers: bool = True
    include_duplicates: bool = False
    min_rating: Optional[float] = None
    max_rating: Optional[float] = None
    min_reviews: Optional[int] = None
    custom_columns: Optional[list] = None
    compress: bool = False
    overwrite_existing: bool = True
