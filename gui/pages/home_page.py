"""Home page (Dashboard)."""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget,
    QCard, QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from gui.pages.base_page import BasePage


class HomePage(BasePage):
    """Home/Dashboard page."""

    # Signals
    start_search_clicked = pyqtSignal()
    view_results_clicked = pyqtSignal()
    view_history_clicked = pyqtSignal()
    settings_clicked = pyqtSignal()

    def setup_ui(self) -> None:
        """Setup home page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Title
        title = QLabel("Google Maps Business Automation")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Automate your business data collection")
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle.setFont(subtitle_font)
        layout.addWidget(subtitle)

        # Quick actions grid
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        # Start Search Button
        btn_start_search = QPushButton("Start New Search")
        btn_start_search.setMinimumHeight(100)
        btn_start_search.setMinimumWidth(200)
        btn_start_search.clicked.connect(self.start_search_clicked.emit)
        grid_layout.addWidget(btn_start_search, 0, 0)

        # View Results Button
        btn_view_results = QPushButton("View Results")
        btn_view_results.setMinimumHeight(100)
        btn_view_results.setMinimumWidth(200)
        btn_view_results.clicked.connect(self.view_results_clicked.emit)
        grid_layout.addWidget(btn_view_results, 0, 1)

        # View History Button
        btn_view_history = QPushButton("Search History")
        btn_view_history.setMinimumHeight(100)
        btn_view_history.setMinimumWidth(200)
        btn_view_history.clicked.connect(self.view_history_clicked.emit)
        grid_layout.addWidget(btn_view_history, 1, 0)

        # Settings Button
        btn_settings = QPushButton("Settings")
        btn_settings.setMinimumHeight(100)
        btn_settings.setMinimumWidth(200)
        btn_settings.clicked.connect(self.settings_clicked.emit)
        grid_layout.addWidget(btn_settings, 1, 1)

        layout.addLayout(grid_layout)

        # Statistics section
        stats_label = QLabel("Statistics")
        stats_font = QFont()
        stats_font.setPointSize(14)
        stats_font.setBold(True)
        stats_label.setFont(stats_font)
        layout.addWidget(stats_label)

        # Stats placeholders
        self.stats_layout = QHBoxLayout()
        for stat_name in ["Total Businesses", "Recent Searches", "Exported Files"]:
            stat_widget = QWidget()
            stat_layout = QVBoxLayout(stat_widget)
            stat_label = QLabel(stat_name)
            stat_value = QLabel("0")
            stat_value_font = QFont()
            stat_value_font.setPointSize(18)
            stat_value_font.setBold(True)
            stat_value.setFont(stat_value_font)
            stat_layout.addWidget(stat_value)
            stat_layout.addWidget(stat_label)
            self.stats_layout.addWidget(stat_widget)

        layout.addLayout(self.stats_layout)

        # Stretch
        layout.addStretch()
