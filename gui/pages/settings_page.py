"""Settings page for application configuration."""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QTabWidget,
    QWidget, QFormLayout, QGroupBox
)
from PyQt6.QtCore import pyqtSignal

from gui.pages.base_page import BasePage


class SettingsPage(BasePage):
    """Application settings page."""

    # Signals
    settings_changed = pyqtSignal(dict)
    save_clicked = pyqtSignal()

    def setup_ui(self) -> None:
        """Setup settings page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("Settings")
        layout.addWidget(title)

        # Tab widget
        self.tabs = QTabWidget()

        # General tab
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)

        # Theme setting
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        general_layout.addRow("Theme:", self.theme_combo)

        # Language setting
        language_label = QLabel("Language:")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Turkish", "Spanish"])
        general_layout.addRow("Language:", self.language_combo)

        # Auto-update
        self.auto_update_checkbox = QCheckBox("Check for updates automatically")
        self.auto_update_checkbox.setChecked(True)
        general_layout.addRow("Updates:", self.auto_update_checkbox)

        self.tabs.addTab(general_tab, "General")

        # Scraper tab
        scraper_tab = QWidget()
        scraper_layout = QFormLayout(scraper_tab)

        # Timeout
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(5, 300)
        self.timeout_spinbox.setValue(30)
        scraper_layout.addRow("Timeout (seconds):", self.timeout_spinbox)

        # Retry attempts
        self.retry_spinbox = QSpinBox()
        self.retry_spinbox.setRange(1, 10)
        self.retry_spinbox.setValue(3)
        scraper_layout.addRow("Retry Attempts:", self.retry_spinbox)

        # Rate limit delay
        self.rate_limit_spinbox = QDoubleSpinBox()
        self.rate_limit_spinbox.setRange(0.5, 60)
        self.rate_limit_spinbox.setValue(2.0)
        scraper_layout.addRow("Rate Limit Delay (sec):", self.rate_limit_spinbox)

        # Max concurrent
        self.max_concurrent_spinbox = QSpinBox()
        self.max_concurrent_spinbox.setRange(1, 10)
        self.max_concurrent_spinbox.setValue(3)
        scraper_layout.addRow("Max Concurrent Searches:", self.max_concurrent_spinbox)

        self.tabs.addTab(scraper_tab, "Scraper")

        # Export tab
        export_tab = QWidget()
        export_layout = QFormLayout(export_tab)

        # Export path
        self.export_path_input = QLineEdit()
        self.export_path_input.setText("./exports")
        export_layout.addRow("Export Path:", self.export_path_input)

        # Default format
        self.default_format_combo = QComboBox()
        self.default_format_combo.addItems(["CSV", "Excel", "JSON", "SQLite"])
        export_layout.addRow("Default Format:", self.default_format_combo)

        self.tabs.addTab(export_tab, "Export")

        layout.addWidget(self.tabs)

        # Buttons
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_clicked.emit)
        buttons_layout.addWidget(self.save_button)

        self.reset_button = QPushButton("Reset to Defaults")
        buttons_layout.addWidget(self.reset_button)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        layout.addStretch()
        self.tabs.addTab(export_tab, "Export")
