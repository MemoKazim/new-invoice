from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QButtonGroup, QRadioButton, QDateEdit, QMessageBox,
)
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QFont
from invoice.i18n import t


class ParamsView(QWidget):
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

        self._type_lbl = QLabel()
        root.addWidget(self._type_lbl)

        self._inbox  = QRadioButton()
        self._inbox.setChecked(True)
        self._outbox = QRadioButton()

        grp = QButtonGroup(self)
        grp.addButton(self._inbox,  1)
        grp.addButton(self._outbox, 2)
        root.addWidget(self._inbox)
        root.addWidget(self._outbox)

        root.addSpacing(6)
        self._date_lbl = QLabel()
        root.addWidget(self._date_lbl)

        from_row = QHBoxLayout()
        self._from_lbl = QLabel()
        self._from_lbl.setFixedWidth(88)
        from_row.addWidget(self._from_lbl)
        self._from = QDateEdit()
        self._from.setDisplayFormat("dd-MM-yyyy")
        self._from.setDate(QDate(QDate.currentDate().year(), 1, 1))
        self._from.setCalendarPopup(True)
        self._from.setFixedWidth(150)
        from_row.addWidget(self._from)
        from_row.addStretch()
        root.addLayout(from_row)

        to_row = QHBoxLayout()
        self._to_lbl = QLabel()
        self._to_lbl.setFixedWidth(88)
        to_row.addWidget(self._to_lbl)
        self._to = QDateEdit()
        self._to.setDisplayFormat("dd-MM-yyyy")
        self._to.setDate(QDate.currentDate())
        self._to.setCalendarPopup(True)
        self._to.setFixedWidth(150)
        to_row.addWidget(self._to)
        to_row.addStretch()
        root.addLayout(to_row)

        root.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._btn = QPushButton()
        self._btn.clicked.connect(self._on_fetch)
        btn_row.addWidget(self._btn)
        root.addLayout(btn_row)

        self.retranslate()

    def retranslate(self):
        self._title_lbl.setText(t("params_title"))
        self._type_lbl.setText(t("params_type_label"))
        self._inbox.setText(t("params_inbox"))
        self._outbox.setText(t("params_outbox"))
        self._date_lbl.setText(t("params_date_label"))
        self._from_lbl.setText(t("params_from"))
        self._to_lbl.setText(t("params_to"))
        self._btn.setText(t("params_btn"))

    def _on_fetch(self):
        if self._from.date() > self._to.date():
            QMessageBox.warning(self, t("params_err_title"), t("params_err_msg"))
            return

        from_date = self._from.date().toString("dd-MM-yyyy")
        to_date   = self._to.date().toString("dd-MM-yyyy")
        overhead  = "find.inbox" if self._inbox.isChecked() else "find.outbox"

        self._window.navigate(self._window.progress_view)
        self._window.progress_view.start(
            self._window.client,
            self._window.selected_cert,
            overhead,
            from_date,
            to_date,
        )
