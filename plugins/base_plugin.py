"""Plugin system base interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BasePlugin(ABC):
    """Base class for plugins."""

    def __init__(self, name: str, version: str) -> None:
        """Initialize plugin.

        Args:
            name: Plugin name
            version: Plugin version
        """
        self.name = name
        self.version = version
        self.enabled = True

    @abstractmethod
    def initialize(self) -> None:
        """Initialize plugin."""
        pass

    @abstractmethod
    def on_search_complete(self, results: Dict[str, Any]) -> None:
        """Called when search completes.

        Args:
            results: Search results
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        pass

    def get_info(self) -> Dict[str, str]:
        """Get plugin information.

        Returns:
            Plugin info dictionary
        """
        return {
            "name": self.name,
            "version": self.version,
            "enabled": str(self.enabled),
        }
