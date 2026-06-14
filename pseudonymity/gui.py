"""Optional Qt GUI for Pseudonymity."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pseudonymity.constants import (
    DEFAULT_PROFILE_PATH,
    KEY_FILE,
    MANIFEST_FILE,
    PSEUDONYMISED_DATASET,
    RAW_DATASET,
    REIDENTIFIED_DATASET,
    RISK_REPORT_FILE,
    VAULT_DATASET,
)
from pseudonymity.datasets import generate_sample_dataset
from pseudonymity.engine import parse_reference_date, pseudonymise_dataset
from pseudonymity.inspect import inspect_csv
from pseudonymity.vault import reidentify_dataset


def _load_qt() -> dict[str, Any]:
    try:
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import (
            QApplication,
            QCheckBox,
            QFileDialog,
            QFormLayout,
            QGridLayout,
            QGroupBox,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QMainWindow,
            QMessageBox,
            QPushButton,
            QSpinBox,
            QTabWidget,
            QTextEdit,
            QVBoxLayout,
            QWidget,
        )

        return locals()
    except ImportError:
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import (
            QApplication,
            QCheckBox,
            QFileDialog,
            QFormLayout,
            QGridLayout,
            QGroupBox,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QMainWindow,
            QMessageBox,
            QPushButton,
            QSpinBox,
            QTabWidget,
            QTextEdit,
            QVBoxLayout,
            QWidget,
        )

        return locals()


qt = _load_qt()
QApplication = qt["QApplication"]
QCheckBox = qt["QCheckBox"]
QFileDialog = qt["QFileDialog"]
QFormLayout = qt["QFormLayout"]
QGridLayout = qt["QGridLayout"]
QGroupBox = qt["QGroupBox"]
QHBoxLayout = qt["QHBoxLayout"]
QLabel = qt["QLabel"]
QLineEdit = qt["QLineEdit"]
QMainWindow = qt["QMainWindow"]
QMessageBox = qt["QMessageBox"]
QPushButton = qt["QPushButton"]
QSpinBox = qt["QSpinBox"]
QTabWidget = qt["QTabWidget"]
QTextEdit = qt["QTextEdit"]
QVBoxLayout = qt["QVBoxLayout"]
QWidget = qt["QWidget"]


class PseudonymityWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Pseudonymity")
        self.resize(980, 720)

        tabs = QTabWidget()
        tabs.addTab(self._build_demo_tab(), "Demo")
        tabs.addTab(self._build_pseudonymise_tab(), "Pseudonymise")
        tabs.addTab(self._build_reidentify_tab(), "Re-identify")
        tabs.addTab(self._build_inspect_tab(), "Inspect CSV")
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        layout.addWidget(QLabel("Run log"))
        layout.addWidget(self.log)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def _field(self, default: Path | str = "") -> QLineEdit:
        return QLineEdit(str(default))

    def _browse_row(self, field: QLineEdit, title: str, save: bool = False) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        button = QPushButton("Browse")
        button.clicked.connect(lambda: self._browse(field, title, save))
        layout.addWidget(field)
        layout.addWidget(button)
        row.setLayout(layout)
        return row

    def _browse(self, field: QLineEdit, title: str, save: bool) -> None:
        if save:
            path, _selected_filter = QFileDialog.getSaveFileName(self, title, field.text())
        else:
            path, _selected_filter = QFileDialog.getOpenFileName(self, title, field.text())
        if path:
            field.setText(path)

    def _append(self, text: str) -> None:
        self.log.append(text)

    def _error(self, title: str, error: Exception) -> None:
        QMessageBox.critical(self, title, str(error))
        self._append(f"ERROR: {error}")

    def _build_demo_tab(self) -> QWidget:
        rows = QSpinBox()
        rows.setRange(1, 1_000_000)
        rows.setValue(120)
        profile = self._field(DEFAULT_PROFILE_PATH)
        reference_date = self._field("2026-06-14")
        use_auto = QCheckBox("Use automatic risk engine fallback")
        use_auto.setChecked(True)
        run = QPushButton("Run Demo")

        form = QFormLayout()
        form.addRow("Rows", rows)
        form.addRow("Profile", self._browse_row(profile, "Select profile"))
        form.addRow("Reference date", reference_date)
        form.addRow("", use_auto)
        form.addRow("", run)

        def execute() -> None:
            try:
                generate_sample_dataset(RAW_DATASET, rows.value(), 20260614)
                result = pseudonymise_dataset(
                    input_path=RAW_DATASET,
                    output_path=PSEUDONYMISED_DATASET,
                    vault_path=VAULT_DATASET,
                    key_file=KEY_FILE,
                    secret_env="PSEUDONYMITY_SECRET",
                    create_key=True,
                    manifest_path=MANIFEST_FILE,
                    risk_report_path=RISK_REPORT_FILE,
                    reference_date=parse_reference_date(reference_date.text()),
                    profile_path=Path(profile.text()),
                    risk_engine="auto" if use_auto.isChecked() else "python",
                )
                self._append(f"Demo completed: {result}")
            except Exception as error:
                self._error("Demo failed", error)

        run.clicked.connect(execute)
        tab = QWidget()
        tab.setLayout(form)
        return tab

    def _build_pseudonymise_tab(self) -> QWidget:
        fields = {
            "input": self._field(RAW_DATASET),
            "output": self._field(PSEUDONYMISED_DATASET),
            "vault": self._field(VAULT_DATASET),
            "profile": self._field(DEFAULT_PROFILE_PATH),
            "manifest": self._field(MANIFEST_FILE),
            "risk": self._field(RISK_REPORT_FILE),
            "key": self._field(KEY_FILE),
            "reference": self._field("2026-06-14"),
        }
        create_key = QCheckBox("Create demo key if missing")
        create_key.setChecked(True)
        run = QPushButton("Pseudonymise")

        form = QFormLayout()
        for label, key in [
            ("Input CSV", "input"),
            ("Output CSV", "output"),
            ("Vault CSV", "vault"),
            ("Profile JSON", "profile"),
            ("Manifest JSON", "manifest"),
            ("Risk report JSON", "risk"),
            ("Key file", "key"),
        ]:
            form.addRow(label, self._browse_row(fields[key], f"Select {label}", save=key in {"output", "vault", "manifest", "risk", "key"}))
        form.addRow("Reference date", fields["reference"])
        form.addRow("", create_key)
        form.addRow("", run)

        def execute() -> None:
            try:
                result = pseudonymise_dataset(
                    input_path=Path(fields["input"].text()),
                    output_path=Path(fields["output"].text()),
                    vault_path=Path(fields["vault"].text()),
                    key_file=Path(fields["key"].text()),
                    secret_env="PSEUDONYMITY_SECRET",
                    create_key=create_key.isChecked(),
                    manifest_path=Path(fields["manifest"].text()),
                    risk_report_path=Path(fields["risk"].text()),
                    reference_date=parse_reference_date(fields["reference"].text()),
                    profile_path=Path(fields["profile"].text()),
                    risk_engine="auto",
                )
                self._append(f"Pseudonymisation completed: {result}")
            except Exception as error:
                self._error("Pseudonymisation failed", error)

        run.clicked.connect(execute)
        tab = QWidget()
        tab.setLayout(form)
        return tab

    def _build_reidentify_tab(self) -> QWidget:
        input_path = self._field(PSEUDONYMISED_DATASET)
        vault_path = self._field(VAULT_DATASET)
        output_path = self._field(REIDENTIFIED_DATASET)
        columns = self._field("customer_id,email,phone")
        audit = self._field("output/reidentification_audit.jsonl")
        reason = self._field("GUI authorised recovery")
        run = QPushButton("Re-identify")

        form = QFormLayout()
        form.addRow("Input CSV", self._browse_row(input_path, "Select pseudonymised CSV"))
        form.addRow("Vault CSV", self._browse_row(vault_path, "Select vault CSV"))
        form.addRow("Output CSV", self._browse_row(output_path, "Select output CSV", save=True))
        form.addRow("Columns", columns)
        form.addRow("Audit log", self._browse_row(audit, "Select audit log", save=True))
        form.addRow("Reason", reason)
        form.addRow("", run)

        def execute() -> None:
            try:
                selected = [item.strip() for item in columns.text().split(",") if item.strip()]
                result = reidentify_dataset(
                    pseudonymised_path=Path(input_path.text()),
                    vault_path=Path(vault_path.text()),
                    output_path=Path(output_path.text()),
                    columns=selected,
                    audit_log_path=Path(audit.text()) if audit.text() else None,
                    reason=reason.text(),
                )
                self._append(f"Re-identification completed: {result}")
            except Exception as error:
                self._error("Re-identification failed", error)

        run.clicked.connect(execute)
        tab = QWidget()
        tab.setLayout(form)
        return tab

    def _build_inspect_tab(self) -> QWidget:
        input_path = self._field(RAW_DATASET)
        output_path = self._field("output/inspection_report.json")
        run = QPushButton("Inspect CSV")

        form = QFormLayout()
        form.addRow("Input CSV", self._browse_row(input_path, "Select CSV"))
        form.addRow("Output JSON", self._browse_row(output_path, "Select report", save=True))
        form.addRow("", run)

        def execute() -> None:
            try:
                report = inspect_csv(Path(input_path.text()))
                from pseudonymity.io import write_json

                write_json(Path(output_path.text()), report)
                self._append(f"Inspection completed: {output_path.text()} ({len(report['columns'])} columns)")
            except Exception as error:
                self._error("Inspection failed", error)

        run.clicked.connect(execute)
        tab = QWidget()
        tab.setLayout(form)
        return tab


def run_gui() -> int:
    app = QApplication([])
    window = PseudonymityWindow()
    window.show()
    return app.exec()
