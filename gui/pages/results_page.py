"""Results page for displaying search results."""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QTableWidget, QTableWidgetItem, QComboBox, QSpinBox
)
from PyQt6.QtCore import pyqtSignal

from gui.pages.base_page import BasePage


class ResultsPage(BasePage):
    """Results display page."""

    # Signals
    export_clicked = pyqtSignal()
    refresh_clicked = pyqtSignal()

    def setup_ui(self) -> None:
        """Setup results page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("Search Results")
        layout.addWidget(title)

        # Toolbar
        toolbar_layout = QHBoxLayout()

        # Search box
        search_label = QLabel("Search Results:")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Filter results...")
        toolbar_layout.addWidget(search_label)
        toolbar_layout.addWidget(self.search_box)

        # Sort dropdown
        sort_label = QLabel("Sort by:")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Name", "Rating", "Reviews", "Date Added"])
        toolbar_layout.addWidget(sort_label)
        toolbar_layout.addWidget(self.sort_combo)

        # Items per page
        items_label = QLabel("Items per page:")
        self.items_spinbox = QSpinBox()
        self.items_spinbox.setRange(10, 1000)
        self.items_spinbox.setValue(50)
        toolbar_layout.addWidget(items_label)
        toolbar_layout.addWidget(self.items_spinbox)

        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(8)
        self.results_table.setHorizontalHeaderLabels([
            "Name", "Address", "Phone", "Website", "Rating", "Reviews", "Category", "URL"
        ])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.results_table)

        # Statistics
        stats_layout = QHBoxLayout()
        self.total_label = QLabel("Total: 0")
        self.duplicates_label = QLabel("Duplicates: 0")
        self.unique_label = QLabel("Unique: 0")
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.duplicates_label)
        stats_layout.addWidget(self.unique_label)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        self.export_button = QPushButton("Export Data")
        self.export_button.clicked.connect(self.export_clicked.emit)
        buttons_layout.addWidget(self.export_button)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_clicked.emit)
        buttons_layout.addWidget(self.refresh_button)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

    def load_results(self, businesses: list) -> None:
        """Load results into table."""
        self.results_table.setRowCount(len(businesses))
        for row, business in enumerate(businesses):
            self.results_table.setItem(row, 0, QTableWidgetItem(business.get("name", "")))
            self.results_table.setItem(row, 1, QTableWidgetItem(business.get("address", "")))
            self.results_table.setItem(row, 2, QTableWidgetItem(business.get("phone", "")))
            self.results_table.setItem(row, 3, QTableWidgetItem(business.get("website", "")))
            self.results_table.setItem(row, 4, QTableWidgetItem(str(business.get("rating", ""))))
            self.results_table.setItem(row, 5, QTableWidgetItem(str(business.get("review_count", ""))))
            self.results_table.setItem(row, 6, QTableWidgetItem(business.get("category", "")))
            self.results_table.setItem(row, 7, QTableWidgetItem(business.get("url", "")))

        # Update statistics
        self.total_label.setText(f"Total: {len(businesses)}")
