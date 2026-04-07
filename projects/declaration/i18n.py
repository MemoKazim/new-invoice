"""Lightweight i18n for declaration app. Usage: from declaration.i18n import t, set_language"""

_lang: str = "en"


def set_language(lang: str) -> None:
    global _lang
    if lang in _STRINGS:
        _lang = lang


def get_language() -> str:
    return _lang


def t(key: str, **kwargs) -> str:
    text = _STRINGS.get(_lang, {}).get(key) or _STRINGS["en"].get(key, key)
    return text.format(**kwargs) if kwargs else text


_STRINGS: dict[str, dict[str, str]] = {
    # ── English ────────────────────────────────────────────────────────────
    "en": {
        "app_title": "E-Taxes Declaration Report",

        # Login
        "login_title":        "Sign In",
        "login_method_label": "Login Method:",
        "login_kps":          "Code / Password / Passphrase  [Unavailable]",
        "login_sv":           "Identity Card  [Unavailable]",
        "login_asan":         "ASAN Signature",
        "login_phone_label":  "Phone:",
        "login_id_label":     "User ID:",
        "login_phone_hint":   "+994XXXXXXXXX",
        "login_id_hint":      "6-digit ID",
        "login_btn":          "Sign In",
        "login_err_title":    "Invalid Input",
        "login_err_phone":    "Enter a valid phone number (+994XXXXXXXXX).",
        "login_err_id":       "Enter a valid 6-digit User ID.",
        "login_fail_title":   "Login Failed",

        # ASAN confirm
        "asan_title": "ASAN Signature Confirmation",
        "asan_msg":   "Please confirm the request on your ASAN mobile app.",

        # Certificate
        "cert_title":       "Select Certificate",
        "cert_subtitle":    "Choose a taxpayer certificate to continue:",
        "cert_btn":         "Continue",
        "cert_nosel_title": "No Selection",
        "cert_nosel_msg":   "Please select a certificate.",

        # Year
        "year_title":     "Declaration Year",
        "year_label":     "Year:",
        "year_hint":      "e.g. 2024",
        "year_btn":       "Load Declarations",
        "year_err_title": "Invalid Year",
        "year_err_msg":   "Enter a valid 4-digit year.",

        # Declaration list
        "decl_title":              "Select Declaration",
        "decl_subtitle":           "Choose a declaration to generate the report:",
        "decl_search_placeholder": "Search by ID…",
        "decl_btn":                "Generate Report",
        "decl_nosel_title":        "No Selection",
        "decl_nosel_msg":          "Please select a declaration.",

        # Progress
        "progress_title": "Generating Report",
        "progress_done":  "Done",
        "progress_error": "Error",
        "progress_saved": "Report saved:  {filename}",
        "btn_open":       "Open Report",
        "btn_new":        "New Report",
        "btn_exit":       "Exit",

        # Worker messages
        "w_dashboard":     "Setting up dashboard...",
        "w_load_decls":    "Loading declarations...",
        "w_fetching":      "Fetching declaration data...",
        "w_generating":    "Generating Excel report...",
        "w_login_fail":    "Login failed. Please check your credentials.",
        "w_terminated":    "Operation was terminated unexpectedly.",

        # Menu
        "menu_view":     "View",
        "menu_dark":     "Dark Mode",
        "menu_light":    "Light Mode",
        "menu_language": "Language",
    },

    # ── Azerbaijani ────────────────────────────────────────────────────────
    "az": {
        "app_title": "E-Vergi Bəyannamə Hesabatı",

        # Login
        "login_title":        "Daxil ol",
        "login_method_label": "Giriş üsulu:",
        "login_kps":          "Kod / Parol / Şifrə  [Mövcud deyil]",
        "login_sv":           "Şəxsiyyət Vəsiqəsi  [Mövcud deyil]",
        "login_asan":         "ASAN İmza",
        "login_phone_label":  "Telefon:",
        "login_id_label":     "İstifadəçi ID:",
        "login_phone_hint":   "+994XXXXXXXXX",
        "login_id_hint":      "6 rəqəmli ID",
        "login_btn":          "Daxil ol",
        "login_err_title":    "Yanlış məlumat",
        "login_err_phone":    "Düzgün telefon nömrəsi daxil edin (+994XXXXXXXXX).",
        "login_err_id":       "Düzgün 6 rəqəmli İstifadəçi ID daxil edin.",
        "login_fail_title":   "Giriş alınmadı",

        # ASAN confirm
        "asan_title": "ASAN İmza Təsdiqi",
        "asan_msg":   "Zəhmət olmasa ASAN mobil tətbiqinizdə sorğunu təsdiqləyin.",

        # Certificate
        "cert_title":       "Sertifikat seçin",
        "cert_subtitle":    "Davam etmək üçün vergi ödəyicisi sertifikatını seçin:",
        "cert_btn":         "Davam et",
        "cert_nosel_title": "Seçim edilməyib",
        "cert_nosel_msg":   "Zəhmət olmasa sertifikat seçin.",

        # Year
        "year_title":     "Bəyannamə İli",
        "year_label":     "İl:",
        "year_hint":      "məs. 2024",
        "year_btn":       "Bəyannamələri yüklə",
        "year_err_title": "Yanlış il",
        "year_err_msg":   "Düzgün 4 rəqəmli il daxil edin.",

        # Declaration list
        "decl_title":              "Bəyannamə seçin",
        "decl_subtitle":           "Hesabat yaratmaq üçün bəyannaməni seçin:",
        "decl_search_placeholder": "ID ilə axtar…",
        "decl_btn":                "Hesabat yarat",
        "decl_nosel_title":        "Seçim edilməyib",
        "decl_nosel_msg":          "Zəhmət olmasa bəyannamə seçin.",

        # Progress
        "progress_title": "Hesabat yaradılır",
        "progress_done":  "Tamamlandı",
        "progress_error": "Xəta",
        "progress_saved": "Hesabat saxlanıldı:  {filename}",
        "btn_open":       "Hesabatı aç",
        "btn_new":        "Yeni hesabat",
        "btn_exit":       "Çıxış",

        # Worker messages
        "w_dashboard":     "İdarə paneli qurulur...",
        "w_load_decls":    "Bəyannamələr yüklənir...",
        "w_fetching":      "Bəyannamə məlumatları alınır...",
        "w_generating":    "Excel hesabatı yaradılır...",
        "w_login_fail":    "Giriş alınmadı. Məlumatlarınızı yoxlayın.",
        "w_terminated":    "Əməliyyat gözlənilmədən dayandırıldı.",

        # Menu
        "menu_view":     "Görünüş",
        "menu_dark":     "Qaranlıq rejim",
        "menu_light":    "İşıqlı rejim",
        "menu_language": "Dil",
    },

    # ── Russian ────────────────────────────────────────────────────────────
    "ru": {
        "app_title": "Электронные Налоги — Декларации",

        # Login
        "login_title":        "Войти",
        "login_method_label": "Способ входа:",
        "login_kps":          "Код / Пароль / Фраза  [Недоступно]",
        "login_sv":           "Удостоверение личности  [Недоступно]",
        "login_asan":         "ASAN подпись",
        "login_phone_label":  "Телефон:",
        "login_id_label":     "ID пользователя:",
        "login_phone_hint":   "+994XXXXXXXXX",
        "login_id_hint":      "6-значный ID",
        "login_btn":          "Войти",
        "login_err_title":    "Неверный ввод",
        "login_err_phone":    "Введите корректный номер телефона (+994XXXXXXXXX).",
        "login_err_id":       "Введите корректный 6-значный ID пользователя.",
        "login_fail_title":   "Ошибка входа",

        # ASAN confirm
        "asan_title": "Подтверждение ASAN подписи",
        "asan_msg":   "Пожалуйста, подтвердите запрос в мобильном приложении ASAN.",

        # Certificate
        "cert_title":       "Выбор сертификата",
        "cert_subtitle":    "Выберите сертификат налогоплательщика для продолжения:",
        "cert_btn":         "Продолжить",
        "cert_nosel_title": "Нет выбора",
        "cert_nosel_msg":   "Пожалуйста, выберите сертификат.",

        # Year
        "year_title":     "Год декларации",
        "year_label":     "Год:",
        "year_hint":      "напр. 2024",
        "year_btn":       "Загрузить декларации",
        "year_err_title": "Неверный год",
        "year_err_msg":   "Введите корректный 4-значный год.",

        # Declaration list
        "decl_title":              "Выбор декларации",
        "decl_subtitle":           "Выберите декларацию для формирования отчёта:",
        "decl_search_placeholder": "Поиск по ID…",
        "decl_btn":                "Сформировать отчёт",
        "decl_nosel_title":        "Нет выбора",
        "decl_nosel_msg":          "Пожалуйста, выберите декларацию.",

        # Progress
        "progress_title": "Формирование отчёта",
        "progress_done":  "Готово",
        "progress_error": "Ошибка",
        "progress_saved": "Отчёт сохранён:  {filename}",
        "btn_open":       "Открыть отчёт",
        "btn_new":        "Новый отчёт",
        "btn_exit":       "Выход",

        # Worker messages
        "w_dashboard":     "Настройка панели управления...",
        "w_load_decls":    "Загрузка деклараций...",
        "w_fetching":      "Получение данных декларации...",
        "w_generating":    "Формирование Excel отчёта...",
        "w_login_fail":    "Ошибка входа. Проверьте введённые данные.",
        "w_terminated":    "Операция была неожиданно прервана.",

        # Menu
        "menu_view":     "Вид",
        "menu_dark":     "Тёмный режим",
        "menu_light":    "Светлый режим",
        "menu_language": "Язык",
    },
}
