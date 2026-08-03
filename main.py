"""Main application entry point."""

import sys
import logging

from PyQt6.QtWidgets import QApplication

from config.settings import get_settings
from config.logger_config import setup_logging
from gui.main_window import MainWindow

logger = logging.getLogger(__name__)


def main() -> None:
    """Main application entry point."""
    try:
        # Setup logging
        setup_logging()
        logger.info("Starting Google Maps Business Automation")

        # Create application
        app = QApplication(sys.argv)

        # Get settings
        settings = get_settings()
        logger.info(f"App version: {settings.app_version}")
        logger.info(f"Debug mode: {settings.app_debug}")

        # Create and show main window
        window = MainWindow()
        window.show()

        # Run application
        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
