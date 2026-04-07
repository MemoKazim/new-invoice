from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from declaration.i18n import t


class AsanConfirmView(QWidget):
    def __init__(self, window):
        super().__init__()
        self._window = window
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(44, 60, 44, 60)
        root.setSpacing(24)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._title_lbl = QLabel()
        self._title_lbl.setFont(QFont("", 18, QFont.Weight.Bold))
        self._title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._title_lbl)

        self._msg = QLabel()
        self._msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._msg.setWordWrap(True)
        root.addWidget(self._msg)

        self._bar = QProgressBar()
        self._bar.setRange(0, 0)
        self._bar.setFixedHeight(12)
        root.addWidget(self._bar)

        self.retranslate()

    def retranslate(self):
        self._title_lbl.setText(t("asan_title"))
        self._msg.setText(t("asan_msg"))

    def start(self):
        self._bar.setRange(0, 0)
        self._msg.setText(t("asan_msg"))

    def stop(self):
        self._bar.setRange(0, 1)
        self._bar.setValue(1)
