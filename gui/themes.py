"""Theme management for dark and light modes."""

from dataclasses import dataclass
from typing import Dict, Optional

from core.enums import Theme


@dataclass
class ThemeColors:
    """Color palette for a theme."""

    primary: str
    primary_dark: str
    primary_light: str
    accent: str
    background: str
    surface: str
    text_primary: str
    text_secondary: str
    border: str
    success: str
    warning: str
    error: str
    info: str


# Dark theme colors
DARK_THEME = ThemeColors(
    primary="#1f1f1f",
    primary_dark="#0d0d0d",
    primary_light="#2d2d2d",
    accent="#00bcd4",
    background="#121212",
    surface="#1e1e1e",
    text_primary="#ffffff",
    text_secondary="#b3b3b3",
    border="#333333",
    success="#4caf50",
    warning="#ff9800",
    error="#f44336",
    info="#2196f3",
)

# Light theme colors
LIGHT_THEME = ThemeColors(
    primary="#f5f5f5",
    primary_dark="#e0e0e0",
    primary_light="#ffffff",
    accent="#00bcd4",
    background="#ffffff",
    surface="#f5f5f5",
    text_primary="#212121",
    text_secondary="#757575",
    border="#e0e0e0",
    success="#4caf50",
    warning="#ff9800",
    error="#f44336",
    info="#2196f3",
)


class ThemeManager:
    """Manager for application themes."""

    def __init__(self, initial_theme: Theme = Theme.DARK) -> None:
        """Initialize theme manager.

        Args:
            initial_theme: Initial theme
        """
        self.current_theme = initial_theme
        self.themes: Dict[Theme, ThemeColors] = {
            Theme.DARK: DARK_THEME,
            Theme.LIGHT: LIGHT_THEME,
        }
        self._observers = []

    def set_theme(self, theme: Theme) -> None:
        """Set application theme.

        Args:
            theme: Theme to set
        """
        if theme in self.themes:
            self.current_theme = theme
            self.notify_observers()

    def get_theme(self) -> ThemeColors:
        """Get current theme colors.

        Returns:
            Current theme colors
        """
        return self.themes[self.current_theme]

    def get_stylesheet(self) -> str:
        """Get QSS stylesheet for current theme.

        Returns:
            QSS stylesheet string
        """
        theme = self.get_theme()
        return f"""
            QMainWindow {{
                background-color: {theme.background};
                color: {theme.text_primary};
            }}
            QWidget {{
                background-color: {theme.background};
                color: {theme.text_primary};
            }}
            QLineEdit, QTextEdit, QComboBox {{
                background-color: {theme.surface};
                color: {theme.text_primary};
                border: 1px solid {theme.border};
                border-radius: 4px;
                padding: 5px;
            }}
            QPushButton {{
                background-color: {theme.accent};
                color: {theme.primary_dark};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme.primary_light};
            }}
            QTableWidget {{
                background-color: {theme.surface};
                color: {theme.text_primary};
                border: 1px solid {theme.border};
            }}
            QHeaderView::section {{
                background-color: {theme.primary_dark};
                color: {theme.text_primary};
                padding: 5px;
                border: 1px solid {theme.border};
            }}
        """

    def attach_observer(self, observer: any) -> None:
        """Attach theme change observer.

        Args:
            observer: Observer with update() method
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def detach_observer(self, observer: any) -> None:
        """Detach theme change observer.

        Args:
            observer: Observer to detach
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self) -> None:
        """Notify all observers of theme change."""
        for observer in self._observers:
            if hasattr(observer, "update_theme"):
                observer.update_theme(self.get_theme())
