import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QMessageBox, QLineEdit,
)
from PyQt6.QtGui import QFont
from declaration.i18n import t


class DeclarationListView(QWidget):
    def __init__(self, window):
        super().__init__()
        self._window = window
        self._declarations = []
        self._filtered_indices = []   # indices into self._declarations for currently visible rows
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

        self._search = QLineEdit()
        self._search.setPlaceholderText(t("decl_search_placeholder"))
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._on_search)
        root.addWidget(self._search)

        self._list = QListWidget()
        self._list.itemDoubleClicked.connect(self._on_generate)
        root.addWidget(self._list)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._btn = QPushButton()
        self._btn.setFixedWidth(160)
        self._btn.clicked.connect(self._on_generate)
        btn_row.addWidget(self._btn)
        root.addLayout(btn_row)

        self.retranslate()

    def retranslate(self):
        self._title_lbl.setText(t("decl_title"))
        self._subtitle_lbl.setText(t("decl_subtitle"))
        self._search.setPlaceholderText(t("decl_search_placeholder"))
        self._btn.setText(t("decl_btn"))

    def load(self, declarations: dict):
        self._declarations = declarations.get("declarations", [])
        self._search.clear()

        try:
            with open("data/json/ui.json", encoding="utf-8") as f:
                ui = json.load(f)
            month_options = ui["ui"][0]["monthOptions"]
        except Exception:
            month_options = {}

        self._month_options = month_options
        self._populate(self._declarations, list(range(len(self._declarations))))

    def _make_label(self, decl: dict) -> str:
        period     = decl.get("reportingPeriod", {})
        year       = period.get("year", "")
        month      = f"{period.get('month', 0):02d}"
        month_name = self._month_options.get(month, month)
        status     = decl.get("declarationStatus", "")
        tax        = decl.get("taxName", "")
        amount     = decl.get("taxAmount", "")
        decl_id    = decl.get("id", "")
        return (
            f"{year}  {month_name}  |  {status}\n"
            f"  ID: {decl_id}    {tax}:  {amount} ₼"
        )

    def _populate(self, items: list, indices: list):
        self._list.clear()
        self._filtered_indices = indices
        for item in items:
            self._list.addItem(QListWidgetItem(self._make_label(item["declaration"])))
        if self._filtered_indices:
            self._list.setCurrentRow(0)

    def _on_search(self, text: str):
        query = text.strip().lower()
        if not query:
            self._populate(self._declarations, list(range(len(self._declarations))))
            return

        matched_items   = []
        matched_indices = []
        for i, item in enumerate(self._declarations):
            decl_id = str(item["declaration"].get("id", "")).lower()
            if query in decl_id:
                matched_items.append(item)
                matched_indices.append(i)

        self._populate(matched_items, matched_indices)

    def _on_generate(self):
        row = self._list.currentRow()
        if row < 0 or row >= len(self._filtered_indices):
            QMessageBox.warning(self, t("decl_nosel_title"), t("decl_nosel_msg"))
            return

        declaration_id = self._declarations[self._filtered_indices[row]]["declaration"]["id"]
        self._window.navigate(self._window.progress_view)
        self._window.progress_view.start(
            self._window.client,
            declaration_id,
            self._window.selected_year,
        )
