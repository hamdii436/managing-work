"""Progress panel widget."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class ProgressPanel(QWidget):
    """Widget for displaying search progress."""

    def __init__(self, parent: any = None) -> None:
        """Initialize progress panel.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Progress label
        self.progress_label = QLabel("Searching... 0%")
        layout.addWidget(self.progress_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Status info
        info_layout = QHBoxLayout()
        self.status_label = QLabel("Status: Preparing...")
        info_layout.addWidget(self.status_label)

        self.time_label = QLabel("Time: --:--")
        info_layout.addWidget(self.time_label)

        info_layout.addStretch()
        layout.addLayout(info_layout)

    def set_progress(self, current: int, total: int) -> None:
        """Update progress.

        Args:
            current: Current progress
            total: Total amount
        """
        if total > 0:
            percentage = (current / total) * 100
            self.progress_bar.setValue(int(percentage))
            self.progress_label.setText(f"Searching... {percentage:.0f}%")

    def set_status(self, status: str) -> None:
        """Update status text.

        Args:
            status: Status text
        """
        self.status_label.setText(f"Status: {status}")

    def set_time_remaining(self, seconds: int) -> None:
        """Update time remaining.

        Args:
            seconds: Seconds remaining
        """
        minutes = seconds // 60
        secs = seconds % 60
        self.time_label.setText(f"Time remaining: {minutes:02d}:{secs:02d}")

    def reset(self) -> None:
        """Reset progress panel."""
        self.progress_bar.setValue(0)
        self.progress_label.setText("Searching... 0%")
        self.status_label.setText("Status: Ready")
        self.time_label.setText("Time: --:--")
