from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox,
)
from PyQt6.QtGui import QFont
from declaration.i18n import t
from declaration.gui.workers import LoadDeclarationsWorker


class YearView(QWidget):
    def __init__(self, window):
        super().__init__()
        self._window = window
        self._worker = None
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(44, 32, 44, 28)
        root.setSpacing(12)

        self._title_lbl = QLabel()
        self._title_lbl.setFont(QFont("", 18, QFont.Weight.Bold))
        root.addWidget(self._title_lbl)

        year_row = QHBoxLayout()
        self._year_lbl = QLabel()
        self._year_lbl.setFixedWidth(88)
        year_row.addWidget(self._year_lbl)
        self._year_input = QLineEdit()
        self._year_input.setFixedWidth(120)
        year_row.addWidget(self._year_input)
        year_row.addStretch()
        root.addLayout(year_row)

        root.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._btn = QPushButton()
        self._btn.setFixedWidth(160)
        self._btn.setDefault(True)
        self._btn.clicked.connect(self._on_load)
        btn_row.addWidget(self._btn)
        root.addLayout(btn_row)

        self.retranslate()

    def retranslate(self):
        self._title_lbl.setText(t("year_title"))
        self._year_lbl.setText(t("year_label"))
        self._year_input.setPlaceholderText(t("year_hint"))
        self._btn.setText(t("year_btn"))

    def _on_load(self):
        raw = self._year_input.text().strip()
        if not raw.isdigit() or len(raw) != 4:
            QMessageBox.warning(self, t("year_err_title"), t("year_err_msg"))
            return

        year = int(raw)
        self._btn.setEnabled(False)

        self._worker = LoadDeclarationsWorker(
            self._window.client,
            self._window.selected_cert,
            year,
        )
        self._worker.succeeded.connect(lambda data: self._on_success(data, year))
        self._worker.failed.connect(self._on_failed)
        self._worker.start()

    def _on_success(self, declarations: dict, year: int):
        self._btn.setEnabled(True)
        self._window.selected_year = year
        self._window.decl_view.load(declarations)
        self._window.navigate(self._window.decl_view)

    def _on_failed(self, msg: str):
        self._btn.setEnabled(True)
        QMessageBox.critical(self, t("year_err_title"), msg)
