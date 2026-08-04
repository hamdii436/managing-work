"""History page for viewing past searches."""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QComboBox, QDateEdit
)
from PyQt6.QtCore import pyqtSignal, QDate

from gui.pages.base_page import BasePage


class HistoryPage(BasePage):
    """Search history page."""

    # Signals
    resume_clicked = pyqtSignal(str)  # Job ID
    delete_clicked = pyqtSignal(str)  # Job ID

    def setup_ui(self) -> None:
        """Setup history page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("Search History")
        layout.addWidget(title)

        # Filters
        filter_layout = QHBoxLayout()

        # Date filter
        date_label = QLabel("From:")
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        filter_layout.addWidget(date_label)
        filter_layout.addWidget(self.date_from)

        date_to_label = QLabel("To:")
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        filter_layout.addWidget(date_to_label)
        filter_layout.addWidget(self.date_to)

        # Status filter
        status_label = QLabel("Status:")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Completed", "Failed", "Paused"])
        filter_layout.addWidget(status_label)
        filter_layout.addWidget(self.status_combo)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "Search ID", "City", "Category", "Status", "Date", "Results", "Actions"
        ])
        self.history_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.history_table)

        # Action buttons
        buttons_layout = QHBoxLayout()
        self.resume_button = QPushButton("Resume Selected")
        self.resume_button.clicked.connect(self.on_resume)
        buttons_layout.addWidget(self.resume_button)

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.on_delete)
        buttons_layout.addWidget(self.delete_button)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

    def on_resume(self) -> None:
        """Resume selected search."""
        selected_rows = self.history_table.selectedIndexes()
        if selected_rows:
            row = selected_rows[0].row()
            job_id = self.history_table.item(row, 0).text()
            self.resume_clicked.emit(job_id)

    def on_delete(self) -> None:
        """Delete selected search."""
        selected_rows = self.history_table.selectedIndexes()
        if selected_rows:
            row = selected_rows[0].row()
            job_id = self.history_table.item(row, 0).text()
            self.delete_clicked.emit(job_id)
