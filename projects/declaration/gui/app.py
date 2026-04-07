import sys
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QApplication, QLabel
from PyQt6.QtGui import QAction, QActionGroup
from declaration import __version__, __copyright__
from declaration.i18n import t, set_language


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(t("app_title"))
        self.setFixedSize(540, 520)

        self._is_dark = False

        # shared state passed between views
        self.client        = None
        self.certificates  = []
        self.selected_cert = None
        self.selected_year = None

        self._build_menu()
        self._build_statusbar()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self._build_views()
        self.stack.setCurrentWidget(self.login_view)

    # ── menu bar ───────────────────────────────────────────────────────────

    def _build_menu(self):
        self._view_menu = self.menuBar().addMenu(t("menu_view"))

        self._theme_action = QAction(t("menu_dark"), self, checkable=True)
        self._theme_action.triggered.connect(self._toggle_theme)
        self._view_menu.addAction(self._theme_action)

        self._view_menu.addSeparator()

        self._lang_menu = self._view_menu.addMenu(t("menu_language"))
        lang_group = QActionGroup(self)
        lang_group.setExclusive(True)

        for code, label in [("en", "English"), ("az", "Azərbaycan"), ("ru", "Русский")]:
            action = QAction(label, self, checkable=True)
            action.setChecked(code == "en")
            action.triggered.connect(lambda checked, c=code: self._set_language(c))
            lang_group.addAction(action)
            self._lang_menu.addAction(action)

    # ── status bar ─────────────────────────────────────────────────────────

    def _build_statusbar(self):
        self.statusBar().setSizeGripEnabled(False)
        self._version_lbl = QLabel(f"v{__version__}  ·  {__copyright__}")
        self.statusBar().addPermanentWidget(self._version_lbl)

    # ── views ──────────────────────────────────────────────────────────────

    def _build_views(self):
        from declaration.gui.views.login import LoginView
        from declaration.gui.views.asan_confirm import AsanConfirmView
        from declaration.gui.views.certificate import CertificateView
        from declaration.gui.views.year import YearView
        from declaration.gui.views.declaration_list import DeclarationListView
        from declaration.gui.views.progress import ProgressView

        self.login_view  = LoginView(self)
        self.asan_view   = AsanConfirmView(self)
        self.cert_view   = CertificateView(self)
        self.year_view   = YearView(self)
        self.decl_view   = DeclarationListView(self)
        self.progress_view = ProgressView(self)

        for view in (self.login_view, self.asan_view, self.cert_view,
                     self.year_view, self.decl_view, self.progress_view):
            self.stack.addWidget(view)

    def navigate(self, view):
        self.stack.setCurrentWidget(view)

    # ── theme ──────────────────────────────────────────────────────────────

    def _toggle_theme(self, checked: bool):
        self._is_dark = checked
        self._theme_action.setText(t("menu_light") if checked else t("menu_dark"))
        QApplication.instance().setStyleSheet(_DARK if checked else _LIGHT)

    # ── language ───────────────────────────────────────────────────────────

    def _set_language(self, lang: str):
        set_language(lang)
        self.setWindowTitle(t("app_title"))
        self._view_menu.setTitle(t("menu_view"))
        self._theme_action.setText(t("menu_light") if self._is_dark else t("menu_dark"))
        self._lang_menu.setTitle(t("menu_language"))
        for view in (self.login_view, self.asan_view, self.cert_view,
                     self.year_view, self.decl_view, self.progress_view):
            view.retranslate()


# ── stylesheets ────────────────────────────────────────────────────────────

_BASE = """
    QPushButton {
        background-color: #0078d4;
        color: white;
        border: none;
        padding: 7px 20px;
        border-radius: 4px;
        min-width: 90px;
    }
    QPushButton:hover   { background-color: #106ebe; }
    QPushButton:pressed { background-color: #005a9e; }
    QProgressBar        { border-radius: 4px; text-align: center; }
    QProgressBar::chunk { background-color: #0078d4; border-radius: 3px; }
    QListWidget         { border-radius: 4px; outline: none; }
    QListWidget::item:selected { background: #0078d4; color: white; }
    QLineEdit  { border-radius: 4px; padding: 6px 8px; }
    QTextEdit  { border-radius: 4px; font-family: Consolas, Monaco, monospace; font-size: 12px; }
    QLineEdit:focus { border-color: #0078d4; }
    QScrollBar:vertical            { width: 10px; border: none; }
    QScrollBar::handle:vertical    { border-radius: 4px; min-height: 20px; }
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical  { height: 0; }
    QScrollBar:horizontal          { height: 10px; border: none; }
    QScrollBar::handle:horizontal  { border-radius: 4px; min-width: 20px; }
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal { width: 0; }
    QMenu::item:selected { background: #0078d4; color: white; }
"""

_LIGHT = _BASE + """
    QWidget      { background-color: #f5f5f5; color: #1a1a1a; font-size: 13px; }
    QMainWindow  { background-color: #f5f5f5; }
    QPushButton:disabled { background-color: #b0c8e0; color: #e8e8e8; }
    QLineEdit    { background: white;   color: #1a1a1a; border: 1px solid #c0c0c0; }
    QListWidget  { background: white;   color: #1a1a1a; border: 1px solid #c0c0c0; }
    QListWidget::item { color: #1a1a1a; padding: 7px 10px; }
    QListWidget::item:hover:!selected { background: #e5f1fb; }
    QProgressBar { background: #e8e8e8; border: 1px solid #c0c0c0; color: #1a1a1a; }
    QTextEdit    { background: white;   color: #1a1a1a; border: 1px solid #c0c0c0; }
    QMenuBar     { background: #ebebeb; color: #1a1a1a; }
    QMenuBar::item:selected { background: #d5d5d5; }
    QMenu        { background: white;   color: #1a1a1a; border: 1px solid #c0c0c0; }
    QScrollBar:vertical   { background: #e0e0e0; }
    QScrollBar::handle:vertical   { background: #b0b0b0; }
    QScrollBar:horizontal { background: #e0e0e0; }
    QScrollBar::handle:horizontal { background: #b0b0b0; }
    QStatusBar   { border-top: 1px solid #d0d0d0; font-size: 11px; }
    QStatusBar QLabel { color: #909090; padding-right: 6px; }
"""

_DARK = _BASE + """
    QWidget      { background-color: #1e1e1e; color: #e8e8e8; font-size: 13px; }
    QMainWindow  { background-color: #1e1e1e; }
    QPushButton:disabled { background-color: #2a4a6a; color: #888888; }
    QLineEdit    { background: #3c3c3c; color: #e8e8e8; border: 1px solid #555555; }
    QListWidget  { background: #2d2d2d; color: #e8e8e8; border: 1px solid #555555; }
    QListWidget::item { color: #e8e8e8; padding: 7px 10px; }
    QListWidget::item:hover:!selected { background: #383838; }
    QProgressBar { background: #3c3c3c; border: 1px solid #555555; color: #e8e8e8; }
    QTextEdit    { background: #2d2d2d; color: #e8e8e8; border: 1px solid #555555; }
    QLabel       { color: #e8e8e8; }
    QRadioButton { color: #e8e8e8; }
    QCheckBox    { color: #e8e8e8; }
    QMenuBar     { background: #2d2d2d; color: #e8e8e8; }
    QMenuBar::item:selected { background: #3c3c3c; }
    QMenu        { background: #2d2d2d; color: #e8e8e8; border: 1px solid #555555; }
    QDialog      { background: #2d2d2d; }
    QAbstractItemView { background: #2d2d2d; color: #e8e8e8; }
    QScrollBar:vertical   { background: #2d2d2d; }
    QScrollBar::handle:vertical   { background: #555555; }
    QScrollBar:horizontal { background: #2d2d2d; }
    QScrollBar::handle:horizontal { background: #555555; }
    QHeaderView::section { background: #3c3c3c; color: #e8e8e8; border: 1px solid #555; }
    QStatusBar   { border-top: 1px solid #383838; font-size: 11px; }
    QStatusBar QLabel { color: #666666; padding-right: 6px; }
"""


def launch():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(_LIGHT)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
