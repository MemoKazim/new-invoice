from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QButtonGroup, QRadioButton, QMessageBox,
)
from PyQt6.QtGui import QFont
from core import validators as v
from declaration.gui.workers import LoginWorker
from declaration.i18n import t


class LoginView(QWidget):
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

        self._method_lbl = QLabel()
        root.addWidget(self._method_lbl)

        self._kps  = QRadioButton()
        self._kps.setEnabled(False)
        self._sv   = QRadioButton()
        self._sv.setEnabled(False)
        self._asan = QRadioButton()
        self._asan.setChecked(True)

        group = QButtonGroup(self)
        for i, rb in enumerate((self._kps, self._sv, self._asan), 1):
            group.addButton(rb, i)
            root.addWidget(rb)

        root.addSpacing(4)

        phone_row = QHBoxLayout()
        self._phone_lbl = QLabel()
        self._phone_lbl.setFixedWidth(88)
        phone_row.addWidget(self._phone_lbl)
        self._phone = QLineEdit()
        phone_row.addWidget(self._phone)
        root.addLayout(phone_row)

        id_row = QHBoxLayout()
        self._id_lbl = QLabel()
        self._id_lbl.setFixedWidth(88)
        id_row.addWidget(self._id_lbl)
        self._user_id = QLineEdit()
        id_row.addWidget(self._user_id)
        root.addLayout(id_row)

        root.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._btn = QPushButton()
        self._btn.setFixedWidth(120)
        self._btn.setDefault(True)
        self._btn.clicked.connect(self._on_sign_in)
        btn_row.addWidget(self._btn)
        root.addLayout(btn_row)

        self.retranslate()

    def retranslate(self):
        self._title_lbl.setText(t("login_title"))
        self._method_lbl.setText(t("login_method_label"))
        self._kps.setText(t("login_kps"))
        self._sv.setText(t("login_sv"))
        self._asan.setText(t("login_asan"))
        self._phone_lbl.setText(t("login_phone_label"))
        self._id_lbl.setText(t("login_id_label"))
        self._phone.setPlaceholderText(t("login_phone_hint"))
        self._user_id.setPlaceholderText(t("login_id_hint"))
        self._btn.setText(t("login_btn"))

    def _on_sign_in(self):
        phone = self._phone.text().strip()
        uid   = self._user_id.text().strip()

        if not v.validatePhone(phone):
            QMessageBox.warning(self, t("login_err_title"), t("login_err_phone"))
            return
        if not v.validateID(uid):
            QMessageBox.warning(self, t("login_err_title"), t("login_err_id"))
            return

        self._btn.setEnabled(False)

        self._worker = LoginWorker({"phone": phone, "id": uid})
        self._worker.succeeded.connect(self._on_success)
        self._worker.failed.connect(self._on_failed)
        self._worker.start()

        self._window.asan_view.start()
        self._window.navigate(self._window.asan_view)

    def _on_success(self, client, certs):
        self._btn.setEnabled(True)
        self._window.client = client
        self._window.certificates = certs
        self._window.asan_view.stop()
        self._window.cert_view.load(certs)
        self._window.navigate(self._window.cert_view)

    def _on_failed(self, msg):
        self._btn.setEnabled(True)
        self._window.asan_view.stop()
        self._window.navigate(self)
        QMessageBox.critical(self, t("login_fail_title"), msg)
