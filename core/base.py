"""Base classes and interfaces for the application."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")


class BaseModel(ABC):
    """Base model for all domain models."""

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        pass

    @abstractmethod
    def to_json(self) -> str:
        """Convert model to JSON string."""
        pass


class Repository(ABC, Generic[T]):
    """Abstract repository pattern interface."""

    @abstractmethod
    def add(self, entity: T) -> T:
        """Add entity to repository."""
        pass

    @abstractmethod
    def update(self, entity: T) -> T:
        """Update existing entity."""
        pass

    @abstractmethod
    def delete(self, entity_id: Any) -> bool:
        """Delete entity by ID."""
        pass

    @abstractmethod
    def get_by_id(self, entity_id: Any) -> Optional[T]:
        """Get entity by ID."""
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination."""
        pass


class Service(ABC):
    """Base service class."""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the service."""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup the service."""
        pass


class Observer(ABC):
    """Observer pattern interface."""

    @abstractmethod
    def update(self, subject: Any) -> None:
        """Update observer with new state."""
        pass


class Observable(ABC):
    """Observable pattern interface."""

    def __init__(self) -> None:
        """Initialize observable."""
        self._observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        """Attach observer."""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        """Detach observer."""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self) -> None:
        """Notify all observers."""
        for observer in self._observers:
            observer.update(self)


class Exporter(ABC, Generic[T]):
    """Abstract exporter interface."""

    @abstractmethod
    async def export(self, data: List[T], path: str) -> bool:
        """Export data to specified path."""
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """Get file extension for this exporter."""
        pass


class Scraper(ABC):
    """Abstract scraper interface."""

    @abstractmethod
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Execute search and return results."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close scraper resources."""
        pass
