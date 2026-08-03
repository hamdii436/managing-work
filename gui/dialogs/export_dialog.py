"""Export dialog for configuring exports."""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QComboBox, QCheckBox, QFileDialog, QMessageBox
)
from PyQt6.QtCore import pyqtSignal

from gui.dialogs.base_dialog import BaseDialog


class ExportDialog(BaseDialog):
    """Dialog for configuring data export."""

    # Signals
    export_confirmed = pyqtSignal(dict)

    def setup_ui(self) -> None:
        """Setup export dialog UI."""
        self.setMinimumWidth(500)
        layout = QVBoxLayout(self)

        # Format selection
        format_layout = QHBoxLayout()
        format_label = QLabel("Export Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["CSV", "Excel", "JSON", "SQLite"])
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        layout.addLayout(format_layout)

        # Output path
        path_layout = QHBoxLayout()
        path_label = QLabel("Output Path:")
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("/path/to/export.csv")
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_path)
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_button)
        layout.addLayout(path_layout)

        # Options
        self.include_headers_checkbox = QCheckBox("Include Headers")
        self.include_headers_checkbox.setChecked(True)
        layout.addWidget(self.include_headers_checkbox)

        self.compress_checkbox = QCheckBox("Compress File")
        layout.addWidget(self.compress_checkbox)

        # Buttons
        buttons_layout = QHBoxLayout()
        export_button = QPushButton("Export")
        export_button.clicked.connect(self.on_export)
        buttons_layout.addWidget(export_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)

    def browse_path(self) -> None:
        """Browse for output path."""
        file_filter = "All Files (*.*)"
        path, _ = QFileDialog.getSaveFileName(self, "Save As", "", file_filter)
        if path:
            self.path_input.setText(path)

    def on_export(self) -> None:
        """Handle export button click."""
        if not self.path_input.text():
            QMessageBox.warning(self, "Validation", "Please specify output path")
            return

        config = {
            "format": self.format_combo.currentText(),
            "path": self.path_input.text(),
            "include_headers": self.include_headers_checkbox.isChecked(),
            "compress": self.compress_checkbox.isChecked(),
        }
        self.export_confirmed.emit(config)
        self.accept()
