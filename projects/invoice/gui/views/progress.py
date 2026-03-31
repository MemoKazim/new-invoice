from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QProgressBar, QTextEdit, QPushButton, QApplication,
)
from PyQt6.QtGui import QFont
from invoice.gui.workers import FetchWorker
from invoice.i18n import t


class ProgressView(QWidget):
    def __init__(self, window):
        super().__init__()
        self._window = window
        self._worker = None
        self._filename = None
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(44, 32, 44, 28)
        root.setSpacing(14)

        self._title = QLabel()
        self._title.setFont(QFont("", 18, QFont.Weight.Bold))
        root.addWidget(self._title)

        self._bar = QProgressBar()
        self._bar.setRange(0, 0)
        self._bar.setFixedHeight(12)
        root.addWidget(self._bar)

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        root.addWidget(self._log)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self._open_btn = QPushButton()
        self._open_btn.setVisible(False)
        self._open_btn.clicked.connect(self._on_open)
        btn_row.addWidget(self._open_btn)

        self._new_btn = QPushButton()
        self._new_btn.setVisible(False)
        self._new_btn.clicked.connect(self._on_new)
        btn_row.addWidget(self._new_btn)

        self._exit_btn = QPushButton()
        self._exit_btn.clicked.connect(QApplication.instance().quit)
        btn_row.addWidget(self._exit_btn)

        root.addLayout(btn_row)

        self.retranslate()

    def retranslate(self):
        # Only update the static button labels; dynamic title is set at runtime
        self._open_btn.setText(t("btn_open"))
        self._new_btn.setText(t("btn_new"))
        self._exit_btn.setText(t("btn_exit"))
        # Refresh title text if it matches a known translated state
        current = self._title.text()
        for key in ("progress_title", "progress_done", "progress_error"):
            # compare against all languages so a retranslate mid-session still works
            from invoice.i18n import _STRINGS
            for lang_dict in _STRINGS.values():
                if current == lang_dict.get(key, ""):
                    self._title.setText(t(key))
                    return
        if not current:
            self._title.setText(t("progress_title"))

    def start(self, client, certificate, overhead_choice: str,
              from_date: str, to_date: str):
        self._log.clear()
        self._bar.setRange(0, 0)
        self._open_btn.setVisible(False)
        self._new_btn.setVisible(False)
        self._filename = None
        self._title.setText(t("progress_title"))

        self._worker = FetchWorker(client, certificate, overhead_choice,
                                   from_date, to_date)
        self._worker.progress.connect(self._on_progress)
        self._worker.succeeded.connect(self._on_success)
        self._worker.failed.connect(self._on_failed)
        self._worker.start()

    def _on_progress(self, msg: str):
        self._log.append(f"→  {msg}")

    def _on_success(self, filename: str):
        self._filename = filename
        self._bar.setRange(0, 1)
        self._bar.setValue(1)
        self._title.setText(t("progress_done"))
        self._log.append(f"\n✓  {t('progress_saved', filename=filename)}")
        self._open_btn.setVisible(True)
        self._new_btn.setVisible(True)

    def _on_failed(self, msg: str):
        self._bar.setRange(0, 1)
        self._bar.setValue(0)
        self._title.setText(t("progress_error"))
        self._log.append(f"\n✗  {msg}")
        self._new_btn.setVisible(True)

    def _on_open(self):
        from invoice.adapters import get_adapter
        get_adapter().open_report(f"reports/invoices/{self._filename}")

    def _on_new(self):
        self._window.navigate(self._window.params_view)
