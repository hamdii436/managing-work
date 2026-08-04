"""Search page for configuring searches."""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QComboBox, QSpinBox, QDoubleSpinBox, QFrame, QFormLayout, QCheckBox
)
from PyQt6.QtCore import pyqtSignal

from gui.pages.base_page import BasePage
from gui.widgets.progress_panel import ProgressPanel


class SearchPage(BasePage):
    """Search configuration page."""

    # Signals
    search_started = pyqtSignal(dict)  # Emits search criteria
    search_cancelled = pyqtSignal()

    def setup_ui(self) -> None:
        """Setup search page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("Business Search")
        layout.addWidget(title)

        # Search criteria form
        form_layout = QFormLayout()

        # City input
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("e.g., Istanbul, London, New York")
        form_layout.addRow("City:", self.city_input)

        # District input
        self.district_input = QLineEdit()
        self.district_input.setPlaceholderText("e.g., Besiktas, Central, Manhattan (optional)")
        form_layout.addRow("District:", self.district_input)

        # Category input
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("e.g., Restaurant, Hotel, Cafe")
        form_layout.addRow("Category:", self.category_input)

        # Keywords
        self.keywords_input = QLineEdit()
        self.keywords_input.setPlaceholderText("Additional keywords (optional)")
        form_layout.addRow("Keywords:", self.keywords_input)

        # Rating filter
        rating_layout = QHBoxLayout()
        min_rating_label = QLabel("Min Rating:")
        self.min_rating_spinbox = QDoubleSpinBox()
        self.min_rating_spinbox.setRange(0, 5)
        self.min_rating_spinbox.setSingleStep(0.1)
        max_rating_label = QLabel("Max Rating:")
        self.max_rating_spinbox = QDoubleSpinBox()
        self.max_rating_spinbox.setRange(0, 5)
        self.max_rating_spinbox.setValue(5)
        self.max_rating_spinbox.setSingleStep(0.1)
        rating_layout.addWidget(min_rating_label)
        rating_layout.addWidget(self.min_rating_spinbox)
        rating_layout.addWidget(max_rating_label)
        rating_layout.addWidget(self.max_rating_spinbox)
        form_layout.addRow("Rating Range:", rating_layout)

        # Min reviews
        self.min_reviews_spinbox = QSpinBox()
        self.min_reviews_spinbox.setRange(0, 10000)
        form_layout.addRow("Min Reviews:", self.min_reviews_spinbox)

        # Max results
        self.max_results_spinbox = QSpinBox()
        self.max_results_spinbox.setRange(1, 1000)
        self.max_results_spinbox.setValue(500)
        form_layout.addRow("Max Results:", self.max_results_spinbox)

        layout.addLayout(form_layout)

        # Export format selection
        export_layout = QHBoxLayout()
        export_label = QLabel("Export Format:")
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["CSV", "Excel", "JSON", "SQLite"])
        export_layout.addWidget(export_label)
        export_layout.addWidget(self.export_format_combo)
        export_layout.addStretch()
        layout.addLayout(export_layout)

        # Options
        self.deduplicate_checkbox = QCheckBox("Remove Duplicates")
        self.deduplicate_checkbox.setChecked(True)
        layout.addWidget(self.deduplicate_checkbox)

        # Progress panel
        self.progress_panel = ProgressPanel()
        self.progress_panel.hide()
        layout.addWidget(self.progress_panel)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Search")
        self.start_button.setMinimumHeight(40)
        self.start_button.clicked.connect(self.on_start_search)
        buttons_layout.addWidget(self.start_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.hide()
        self.cancel_button.clicked.connect(self.on_cancel_search)
        buttons_layout.addWidget(self.cancel_button)

        layout.addLayout(buttons_layout)
        layout.addStretch()

    def on_start_search(self) -> None:
        """Handle start search button click."""
        criteria = {
            "city": self.city_input.text(),
            "district": self.district_input.text() or None,
            "category": self.category_input.text(),
            "keywords": self.keywords_input.text() or None,
            "min_rating": self.min_rating_spinbox.value() if self.min_rating_spinbox.value() > 0 else None,
            "max_rating": self.max_rating_spinbox.value() if self.max_rating_spinbox.value() < 5 else None,
            "min_reviews": self.min_reviews_spinbox.value() if self.min_reviews_spinbox.value() > 0 else None,
            "max_results": self.max_results_spinbox.value(),
            "export_format": self.export_format_combo.currentText(),
            "deduplicate": self.deduplicate_checkbox.isChecked(),
        }
        self.search_started.emit(criteria)
        self.start_button.hide()
        self.cancel_button.show()
        self.progress_panel.show()

    def on_cancel_search(self) -> None:
        """Handle cancel search button click."""
        self.search_cancelled.emit()
        self.reset_ui()

    def reset_ui(self) -> None:
        """Reset UI to initial state."""
        self.start_button.show()
        self.cancel_button.hide()
        self.progress_panel.hide()
        self.progress_panel.reset()
