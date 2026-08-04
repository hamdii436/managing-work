"""Export service for multi-format data export."""

import logging
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

import pandas as pd
from sqlalchemy import create_engine

from config.settings import get_settings
from core.enums import ExportFormat
from core.exceptions import ExportError
from models.business import Business

logger = logging.getLogger(__name__)


class BaseExporter(ABC):
    """Base class for data exporters."""

    def __init__(self, export_path: Optional[str] = None) -> None:
        """Initialize exporter."""
        settings = get_settings()
        self.export_path = Path(export_path or settings.export_path)
        self.export_path.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def export(self, businesses: List[Business], filename: str) -> tuple[bool, str]:
        """Export businesses to file."""
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """Get file extension for this format."""
        pass

    def _prepare_data(self, businesses: List[Business]) -> List[dict]:
        """Prepare businesses for export."""
        data = []
        for business in businesses:
            data.append({
                'Name': business.name,
                'Address': business.location.address if business.location else '',
                'City': business.city,
                'District': business.district or '',
                'Category': business.category or '',
                'Phone': business.phone or '',
                'Website': business.website or '',
                'Email': business.email or '',
                'Rating': business.rating,
                'Reviews': business.review_count,
                'URL': business.url or '',
                'Latitude': business.location.latitude if business.location else '',
                'Longitude': business.location.longitude if business.location else '',
                'Description': business.description or '',
            })
        return data


class CSVExporter(BaseExporter):
    """Export data to CSV format."""

    def export(self, businesses: List[Business], filename: str) -> tuple[bool, str]:
        """Export to CSV."""
        try:
            if not filename.endswith('.csv'):
                filename += '.csv'
            
            data = self._prepare_data(businesses)
            df = pd.DataFrame(data)
            
            output_file = self.export_path / filename
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            
            msg = f"Exported {len(businesses)} businesses to CSV: {output_file}"
            logger.info(msg)
            return True, msg
        except Exception as e:
            error_msg = f"CSV export failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def get_file_extension(self) -> str:
        """Get file extension."""
        return ".csv"


class ExcelExporter(BaseExporter):
    """Export data to Excel format."""

    def export(self, businesses: List[Business], filename: str) -> tuple[bool, str]:
        """Export to Excel."""
        try:
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            data = self._prepare_data(businesses)
            df = pd.DataFrame(data)

            output_file = self.export_path / filename
            with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name="Businesses", index=False)

                # Add summary sheet
                summary_data = {
                    "Metric": ["Total Records", "Average Rating", "Has Website", "Has Phone"],
                    "Value": [
                        len(businesses),
                        df["Rating"].mean() if "Rating" in df.columns else 0,
                        len([b for b in businesses if b.website]),
                        len([b for b in businesses if b.phone]),
                    ],
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name="Summary", index=False)

            msg = f"Exported {len(businesses)} businesses to Excel: {output_file}"
            logger.info(msg)
            return True, msg
        except Exception as e:
            error_msg = f"Excel export failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def get_file_extension(self) -> str:
        """Get file extension."""
        return ".xlsx"


class JSONExporter(BaseExporter):
    """Export data to JSON format."""

    def export(self, businesses: List[Business], filename: str) -> tuple[bool, str]:
        """Export to JSON."""
        try:
            if not filename.endswith('.json'):
                filename += '.json'
            
            data = {
                'export_timestamp': pd.Timestamp.now().isoformat(),
                'total_count': len(businesses),
                'businesses': self._prepare_data(businesses)
            }
            
            output_file = self.export_path / filename
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            msg = f"Exported {len(businesses)} businesses to JSON: {output_file}"
            logger.info(msg)
            return True, msg
        except Exception as e:
            error_msg = f"JSON export failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def get_file_extension(self) -> str:
        """Get file extension."""
        return ".json"


class SQLiteExporter(BaseExporter):
    """Export data to SQLite database."""

    def export(self, businesses: List[Business], filename: str) -> tuple[bool, str]:
        """Export to SQLite."""
        try:
            if not filename.endswith('.db'):
                filename += '.db'
            
            data = self._prepare_data(businesses)
            df = pd.DataFrame(data)

            output_file = self.export_path / filename
            engine = create_engine(f"sqlite:///{output_file}")
            df.to_sql("businesses", engine, if_exists="replace", index=False)

            msg = f"Exported {len(businesses)} businesses to SQLite: {output_file}"
            logger.info(msg)
            return True, msg
        except Exception as e:
            error_msg = f"SQLite export failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def get_file_extension(self) -> str:
        """Get file extension."""
        return ".db"


class ExportService:
    """Service for exporting business data in multiple formats."""

    def __init__(self, export_path: Optional[str] = None) -> None:
        """Initialize export service."""
        self.exporters = {
            ExportFormat.CSV: CSVExporter(export_path),
            ExportFormat.EXCEL: ExcelExporter(export_path),
            ExportFormat.JSON: JSONExporter(export_path),
        }
        self.export_path = self.exporters[ExportFormat.CSV].export_path

    def export(
        self,
        businesses: List[Business],
        format: ExportFormat,
        filename: str,
    ) -> tuple[bool, str]:
        """Export businesses in specified format.

        Args:
            businesses: List of businesses to export
            format: Export format
            filename: Output filename

        Returns:
            Tuple of (success, message)
        """
        if not businesses:
            return False, "No businesses to export"
        
        exporter = self.exporters.get(format)
        if not exporter:
            return False, f"Unsupported export format: {format}"

        return exporter.export(businesses, filename)

    def export_all_formats(self, businesses: List[Business], base_filename: str) -> dict:
        """Export businesses in all formats.
        
        Args:
            businesses: List of businesses to export
            base_filename: Base filename without extension
            
        Returns:
            Dictionary with results for each format
        """
        results = {}
        for format in ExportFormat:
            success, message = self.export(businesses, format, base_filename)
            results[format.value] = {
                'success': success,
                'message': message
            }
        return results

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

    def get_export_path(self) -> Path:
        """Get export directory path."""
        return self.export_path
