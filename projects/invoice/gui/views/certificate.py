from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QPushButton, QMessageBox,
)
from PyQt6.QtGui import QFont
from invoice.i18n import t


class CertificateView(QWidget):
    def __init__(self, window):
        super().__init__()
        self._window = window
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(44, 32, 44, 28)
        root.setSpacing(12)

        self._title_lbl = QLabel()
        self._title_lbl.setFont(QFont("", 18, QFont.Weight.Bold))
        root.addWidget(self._title_lbl)

        self._subtitle_lbl = QLabel()
        root.addWidget(self._subtitle_lbl)

        self._list = QListWidget()
        self._list.itemDoubleClicked.connect(self._on_continue)
        root.addWidget(self._list)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._btn = QPushButton()
        self._btn.setFixedWidth(120)
        self._btn.clicked.connect(self._on_continue)
        btn_row.addWidget(self._btn)
        root.addLayout(btn_row)

        self.retranslate()

    def retranslate(self):
        self._title_lbl.setText(t("cert_title"))
        self._subtitle_lbl.setText(t("cert_subtitle"))
        self._btn.setText(t("cert_btn"))

    def load(self, certificates):
        self._list.clear()
        for cert in certificates:
            self._list.addItem(f"{cert.tin}  —  {cert.name}")
        if certificates:
            self._list.setCurrentRow(0)

    def _on_continue(self):
        row = self._list.currentRow()
        if row < 0:
            QMessageBox.warning(self, t("cert_nosel_title"), t("cert_nosel_msg"))
            return
        self._window.selected_cert = self._window.certificates[row]
        self._window.navigate(self._window.params_view)
