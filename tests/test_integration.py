"""Integration tests for core functionality."""

import unittest
import tempfile
from pathlib import Path

from config.settings import get_settings, Settings
from config.logging_config import setup_logging
from database.db_manager import get_db_manager
from models.business import Business, Location, BusinessHours
from models.search import SearchCriteria, SearchJob, SearchResult
from services.export_service import ExportService
from services.search_service import SearchService, SearchQueue
from services.deduplication_service import DeduplicationService
from services.data_service import DataService
from core.enums import ExportFormat, SearchStatus


class TestDataModels(unittest.TestCase):
    """Test data model functionality."""

    def test_business_creation(self):
        """Test business model creation."""
        business = Business(
            name="Test Business",
            city="Test City",
            rating=4.5,
            review_count=100,
        )
        self.assertEqual(business.name, "Test Business")
        self.assertEqual(business.city, "Test City")
        self.assertEqual(business.rating, 4.5)

    def test_search_criteria_validation(self):
        """Test search criteria validation."""
        # Valid criteria
        criteria = SearchCriteria(
            city="Istanbul",
            category="Restaurant",
            min_rating=3.0,
            max_rating=5.0,
        )
        self.assertEqual(criteria.city, "Istanbul")

        # Invalid rating
        with self.assertRaises(ValueError):
            SearchCriteria(city="Istanbul", min_rating=10.0)

    def test_search_job_lifecycle(self):
        """Test search job status transitions."""
        criteria = SearchCriteria(city="Istanbul")
        job = SearchJob(id="test-1", criteria=criteria)

        self.assertEqual(job.status, SearchStatus.PENDING)

        job.start()
        self.assertEqual(job.status, SearchStatus.RUNNING)

        result = SearchResult(total_found=10, total_saved=10, duplicates_found=0)
        job.complete(result)
        self.assertEqual(job.status, SearchStatus.COMPLETED)
        self.assertEqual(job.progress, 1.0)


class TestSearchQueue(unittest.TestCase):
    """Test search queue functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.queue = SearchQueue()

    def test_add_job_to_queue(self):
        """Test adding job to queue."""
        criteria = SearchCriteria(city="Istanbul")
        job = self.queue.add(criteria)

        self.assertIsNotNone(job.id)
        self.assertEqual(job.status, SearchStatus.PENDING)
        self.assertEqual(self.queue.size(), 1)

    def test_get_next_job(self):
        """Test getting next job from queue."""
        criteria1 = SearchCriteria(city="Istanbul")
        criteria2 = SearchCriteria(city="Ankara")

        self.queue.add(criteria1)
        self.queue.add(criteria2)

        next_job = self.queue.get_next()
        self.assertIsNotNone(next_job)
        self.assertEqual(next_job.criteria.city, "Istanbul")


class TestDeduplication(unittest.TestCase):
    """Test deduplication functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.dedup_service = DeduplicationService(threshold=0.85)

    def test_similarity_calculation(self):
        """Test similarity calculation between businesses."""
        business1 = Business(
            name="McDonald's Istanbul",
            city="Istanbul",
            phone="+1234567890",
            url="https://maps.google.com/1",
        )

        business2 = Business(
            name="McDonald's Istanbul",
            city="Istanbul",
            phone="+1234567890",
            url="https://maps.google.com/1",
        )

        score = self.dedup_service.calculate_similarity(business1, business2)
        self.assertGreater(score, 0.8)

    def test_remove_duplicates(self):
        """Test duplicate removal."""
        business1 = Business(name="Store A", city="Istanbul")
        business2 = Business(name="Store A", city="Istanbul")
        business3 = Business(name="Store B", city="Ankara")

        businesses = [business1, business2, business3]
        unique = self.dedup_service.remove_duplicates(businesses)

        self.assertLess(len(unique), len(businesses))


class TestExportService(unittest.TestCase):
    """Test export functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.export_service = ExportService(self.temp_dir)

    def tearDown(self):
        """Clean up test artifacts."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_csv_export(self):
        """Test CSV export."""
        business = Business(
            name="Test Business",
            city="Istanbul",
            rating=4.5,
            review_count=100,
        )

        success, message = self.export_service.export([business], ExportFormat.CSV, "test")
        self.assertTrue(success)

        # Check file exists
        csv_file = Path(self.temp_dir) / "test.csv"
        self.assertTrue(csv_file.exists())

    def test_json_export(self):
        """Test JSON export."""
        business = Business(
            name="Test Business",
            city="Istanbul",
            rating=4.5,
        )

        success, message = self.export_service.export([business], ExportFormat.JSON, "test")
        self.assertTrue(success)

        # Check file exists
        json_file = Path(self.temp_dir) / "test.json"
        self.assertTrue(json_file.exists())


if __name__ == '__main__':
    unittest.main()
