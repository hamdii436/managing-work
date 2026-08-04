"""Base page class for all pages."""

from abc import ABC, abstractmethod

from PyQt6.QtWidgets import QWidget


class BasePage(ABC, QWidget):
    """Base class for all pages."""

    def __init__(self, parent: any = None) -> None:
        """Initialize base page.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setup_ui()

    @abstractmethod
    def setup_ui(self) -> None:
        """Setup user interface."""
        pass

    def show_message(self, message: str, msg_type: str = "info") -> None:
        """Show message to user.

        Args:
            message: Message text
            msg_type: Message type (info, warning, error, success)
        """
        pass

    def update_theme(self, theme: any) -> None:
        """Update theme colors.

        Args:
            theme: Theme colors object
        """
        pass
