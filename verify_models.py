"""Quick verification script for core models."""

from models.business import Business, Location
from models.search import SearchCriteria, SearchJob, SearchResult
from core.enums import SearchStatus

# Test Business model
b = Business(name="Test Business", address="123 Main St")
print(f"[OK] Business model works: {b.name}")

# Test Location model
loc = Location(latitude=41.0082, longitude=28.9784, address="Istanbul, Turkey")
print(f"[OK] Location model works: {loc.get_full_address()}")

# Test SearchCriteria
criteria = SearchCriteria(city="Istanbul", category="Restaurant")
print(f"[OK] SearchCriteria works: {criteria.to_query_string()}")

# Test SearchJob
job = SearchJob(id="test-1", criteria=criteria)
print(f"[OK] SearchJob works: {job.status.value}")

# Test SearchResult
result = SearchResult(total_found=10, total_saved=10, duplicates_found=0)
print(f"[OK] SearchResult works: {result.get_summary()}")

print("\n[OK] All core models working correctly!")

