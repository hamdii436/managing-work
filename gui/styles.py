"""PyQt6 stylesheets."""

from gui.themes import ThemeManager, Theme


class StylesheetManager:
    """Manages application stylesheets."""

    @staticmethod
    def get_global_stylesheet() -> str:
        """Get global stylesheet."""
        return """
            * {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
            }
            
            QMainWindow {
                margin: 0;
                padding: 0;
            }
            
            QWidget {
                margin: 0;
                padding: 0;
            }
            
            QPushButton {
                min-height: 32px;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: 500;
            }
            
            QPushButton:hover {
                opacity: 0.8;
            }
            
            QPushButton:pressed {
                opacity: 0.6;
            }
            
            QLineEdit, QTextEdit, QComboBox, QSpinBox {
                min-height: 32px;
                padding: 6px;
                border-radius: 4px;
            }
            
            QTableWidget {
                border-collapse: collapse;
                gridline-color: #e0e0e0;
            }
            
            QHeaderView::section {
                padding: 4px;
                text-align: left;
            }
            
            QLabel {
                margin: 0;
                padding: 0;
            }
            
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 4px;
                text-align: center;
                height: 20px;
            }
            
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 4px;
            }
            
            QMenuBar {
                padding: 2px;
            }
            
            QMenuBar::item:selected {
                background-color: #e0e0e0;
            }
            
            QMenu {
                padding: 4px 0;
            }
            
            QMenu::item:selected {
                background-color: #e0e0e0;
            }
            
            QStatusBar {
                border-top: 1px solid #ccc;
                padding: 4px;
            }
            
            QTabBar::tab {
                padding: 6px 20px;
                margin: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 2px solid #00bcd4;
            }
            
            QComboBox QAbstractItemView {
                padding: 4px;
            }
        """

    @staticmethod
    def get_button_style(style_type: str = "primary") -> str:
        """Get button-specific style."""
        styles = {
            "primary": "background-color: #00bcd4; color: white; font-weight: bold;",
            "danger": "background-color: #f44336; color: white; font-weight: bold;",
            "success": "background-color: #4caf50; color: white; font-weight: bold;",
            "warning": "background-color: #ff9800; color: white; font-weight: bold;",
        }
        return styles.get(style_type, styles["primary"])

    @staticmethod
    def get_input_style() -> str:
        """Get input field style."""
        return """
            QLineEdit {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                padding: 6px;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 2px solid #00bcd4;
            }
        """

    @staticmethod
    def get_table_style() -> str:
        """Get table style."""
        return """
            QTableWidget {
                background-color: #ffffff;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 4px;
                border-right: 1px solid #e0e0e0;
                border-bottom: 1px solid #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 6px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
            }
        """
