"""Base dialog class."""

from PyQt6.QtWidgets import QDialog


class BaseDialog(QDialog):
    """Base class for all dialogs."""

    def __init__(self, parent: any = None, title: str = "Dialog") -> None:
        """Initialize base dialog.

        Args:
            parent: Parent widget
            title: Dialog title
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup user interface. Override in subclasses."""
        pass
