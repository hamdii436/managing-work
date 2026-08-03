"""Main application window."""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QMenuBar, QMenu, QStatusBar, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon

from config.settings import get_settings
from config.logger_config import get_logger
from gui.themes import ThemeManager, Theme
from gui.styles import StylesheetManager
from gui.pages.home_page import HomePage
from gui.pages.search_page import SearchPage
from gui.pages.results_page import ResultsPage
from gui.pages.history_page import HistoryPage
from gui.pages.settings_page import SettingsPage

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""

    # Signals
    app_closing = pyqtSignal()

    def __init__(self) -> None:
        """Initialize main window."""
        super().__init__()
        self.settings = get_settings()
        self.theme_manager = ThemeManager(Theme(self.settings.app_theme.value))

        # Window settings
        self.setWindowTitle("Google Maps Business Automation")
        self.setMinimumSize(self.settings.ui_window_width, self.settings.ui_window_height)

        # Setup UI
        self.setup_ui()
        self.setup_menu()
        self.setup_connections()

        # Apply theme
        self.apply_theme()

        logger.info("Application started")

    def setup_ui(self) -> None:
        """Setup main window UI."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Navigation bar
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(10, 10, 10, 10)
        nav_layout.setSpacing(10)

        # Navigation buttons
        self.home_button = QPushButton("Home")
        self.home_button.clicked.connect(lambda: self.show_page(0))
        nav_layout.addWidget(self.home_button)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(lambda: self.show_page(1))
        nav_layout.addWidget(self.search_button)

        self.results_button = QPushButton("Results")
        self.results_button.clicked.connect(lambda: self.show_page(2))
        nav_layout.addWidget(self.results_button)

        self.history_button = QPushButton("History")
        self.history_button.clicked.connect(lambda: self.show_page(3))
        nav_layout.addWidget(self.history_button)

        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(lambda: self.show_page(4))
        nav_layout.addWidget(self.settings_button)

        nav_layout.addStretch()
        layout.addLayout(nav_layout)

        # Stacked widget for pages
        self.stacked_widget = QStackedWidget()

        # Create pages
        self.home_page = HomePage()
        self.search_page = SearchPage()
        self.results_page = ResultsPage()
        self.history_page = HistoryPage()
        self.settings_page = SettingsPage()

        # Add pages to stack
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.search_page)
        self.stacked_widget.addWidget(self.results_page)
        self.stacked_widget.addWidget(self.history_page)
        self.stacked_widget.addWidget(self.settings_page)

        layout.addWidget(self.stacked_widget)

        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

    def setup_menu(self) -> None:
        """Setup menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        # View menu
        view_menu = menubar.addMenu("View")

        theme_menu = view_menu.addMenu("Theme")
        dark_theme_action = QAction("Dark", self, checkable=True)
        dark_theme_action.setChecked(self.theme_manager.current_theme == Theme.DARK)
        dark_theme_action.triggered.connect(lambda: self.set_theme(Theme.DARK))
        theme_menu.addAction(dark_theme_action)

        light_theme_action = QAction("Light", self, checkable=True)
        light_theme_action.setChecked(self.theme_manager.current_theme == Theme.LIGHT)
        light_theme_action.triggered.connect(lambda: self.set_theme(Theme.LIGHT))
        theme_menu.addAction(light_theme_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_connections(self) -> None:
        """Setup signal connections."""
        self.theme_manager.attach_observer(self)

    def show_page(self, page_index: int) -> None:
        """Show specific page.

        Args:
            page_index: Page index (0-4)
        """
        self.stacked_widget.setCurrentIndex(page_index)

    def set_theme(self, theme: Theme) -> None:
        """Set application theme.

        Args:
            theme: Theme to set
        """
        self.theme_manager.set_theme(theme)
        self.apply_theme()

    def apply_theme(self) -> None:
        """Apply current theme to application."""
        stylesheet = StylesheetManager.get_global_stylesheet()
        self.setStyleSheet(stylesheet)

    def show_about(self) -> None:
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About",
            f"{self.settings.app_name}\nVersion {self.settings.app_version}\n\n"
            f"Automated business data collection from Google Maps",
        )

    def update_theme(self, theme: any) -> None:
        """Update theme (called by ThemeManager).

        Args:
            theme: Theme colors
        """
        self.apply_theme()

    def closeEvent(self, event: any) -> None:
        """Handle window close event."""
        reply = QMessageBox.question(
            self,
            "Quit",
            "Are you sure you want to exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.app_closing.emit()
            event.accept()
        else:
            event.ignore()
