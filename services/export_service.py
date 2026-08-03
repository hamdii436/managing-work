"""Export service for multi-format data export."""

import logging
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

import pandas as pd
from sqlalchemy import create_engine

from core.enums import ExportFormat
from core.exceptions import ExportError
from models.business import Business

logger = logging.getLogger(__name__)


class BaseExporter(ABC):
    """Base class for data exporters."""

    @abstractmethod
    async def export(self, businesses: List[Business], output_path: str) -> bool:
        """Export businesses to file."""
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """Get file extension for this format."""
        pass

    def _prepare_data(self, businesses: List[Business]) -> List[dict]:
        """Prepare businesses for export."""
        return [business.to_dict() for business in businesses]


class CSVExporter(BaseExporter):
    """Export data to CSV format."""

    async def export(self, businesses: List[Business], output_path: str) -> bool:
        """Export to CSV."""
        try:
            data = self._prepare_data(businesses)
            df = pd.DataFrame(data)
            df.to_csv(output_path, index=False, encoding="utf-8")
            logger.info(f"Exported {len(businesses)} businesses to CSV: {output_path}")
            return True
        except Exception as e:
            logger.error(f"CSV export failed: {e}")
            raise ExportError(f"Failed to export to CSV: {e}")

    def get_file_extension(self) -> str:
        """Get file extension."""
        return ".csv"


class ExcelExporter(BaseExporter):
    """Export data to Excel format."""

    async def export(self, businesses: List[Business], output_path: str) -> bool:
        """Export to Excel."""
        try:
            data = self._prepare_data(businesses)
            df = pd.DataFrame(data)

            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Businesses", index=False)

                # Add summary sheet
                summary_data = {
                    "Metric": ["Total Records", "Average Rating", "Unique Categories"],
                    "Value": [
                        len(businesses),
                        df["rating"].mean() if "rating" in df.columns else 0,
                        df["category"].nunique() if "category" in df.columns else 0,
                    ],
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name="Summary", index=False)

            logger.info(f"Exported {len(businesses)} businesses to Excel: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Excel export failed: {e}")
            raise ExportError(f"Failed to export to Excel: {e}")

    def get_file_extension(self) -> str:
        """Get file extension."""
        return ".xlsx"


class JSONExporter(BaseExporter):
    """Export data to JSON format."""

    async def export(self, businesses: List[Business], output_path: str) -> bool:
        """Export to JSON."""
        try:
            data = self._prepare_data(businesses)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Exported {len(businesses)} businesses to JSON: {output_path}")
            return True
        except Exception as e:
            logger.error(f"JSON export failed: {e}")
            raise ExportError(f"Failed to export to JSON: {e}")

    def get_file_extension(self) -> str:
        """Get file extension."""
        return ".json"


class SQLiteExporter(BaseExporter):
    """Export data to SQLite database."""

    async def export(self, businesses: List[Business], output_path: str) -> bool:
        """Export to SQLite."""
        try:
            data = self._prepare_data(businesses)
            df = pd.DataFrame(data)

            # Create SQLite connection
            engine = create_engine(f"sqlite:///{output_path}")
            df.to_sql("businesses", engine, if_exists="replace", index=False)

            logger.info(f"Exported {len(businesses)} businesses to SQLite: {output_path}")
            return True
        except Exception as e:
            logger.error(f"SQLite export failed: {e}")
            raise ExportError(f"Failed to export to SQLite: {e}")

    def get_file_extension(self) -> str:
        """Get file extension."""
        return ".db"


class ExportService:
    """Service for exporting business data in multiple formats."""

    def __init__(self) -> None:
        """Initialize export service."""
        self.exporters = {
            ExportFormat.CSV: CSVExporter(),
            ExportFormat.EXCEL: ExcelExporter(),
            ExportFormat.JSON: JSONExporter(),
            ExportFormat.SQLITE: SQLiteExporter(),
        }

    async def export(
        self,
        businesses: List[Business],
        format: ExportFormat,
        output_path: str,
    ) -> bool:
        """Export businesses in specified format.

        Args:
            businesses: List of businesses to export
            format: Export format
            output_path: Output file path

        Returns:
            True if export successful
        """
        try:
            # Create output directory if it doesn't exist
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            exporter = self.exporters.get(format)
            if not exporter:
                raise ExportError(f"Unsupported export format: {format}")

            return await exporter.export(businesses, output_path)

        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise

    def get_file_extension(self, format: ExportFormat) -> str:
        """Get file extension for format.

        Args:
            format: Export format

        Returns:
            File extension
        """
        exporter = self.exporters.get(format)
        if not exporter:
            raise ExportError(f"Unsupported export format: {format}")
        return exporter.get_file_extension()
