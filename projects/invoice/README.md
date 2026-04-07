# Invoice Scrapper

> Fetch, parse, and export inbox/outbox invoice reports from
> [new.e-taxes.gov.az](https://new.e-taxes.gov.az) using ASAN IMZA digital signature authentication.

**Version:** 2.0.0 &nbsp;|&nbsp; **Company:** Memorise LLC &nbsp;|&nbsp; **License:** MIT

---

## Features

- **ASAN IMZA login** — phone number + 6-digit user ID, real-time confirmation polling
- **Multi-certificate support** — select from all accessible taxpayer certificates (legal & individual)
- **Inbox & outbox** — fetch received or sent invoices for any date range
- **Paginated fetch** — automatically handles multi-page result sets (200 records/page)
- **Direct Excel export** — pandas DataFrame pipeline writes `.xlsx` reports with no CSV intermediary
- **PyQt6 GUI** — wizard-style interface with light/dark theme and 3-language support (EN / AZ / RU)
- **CLI mode** — fully interactive terminal workflow for headless or scripted use
- **Windows executable** — single `.exe` via PyInstaller (`build.bat`)

---

## Requirements

- Python **3.11+**
- Dependencies:

| Package    | Version | Purpose                     |
| ---------- | ------- | --------------------------- |
| `requests` | >=2.31  | HTTP session & API calls    |
| `pandas`   | >=2.0   | Data parsing & Excel export |
| `openpyxl` | >=3.1   | Excel engine for pandas     |
| `PyQt6`    | >=6.6   | Desktop GUI                 |

---

## Installation

```bash
# From the repo root
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

---

## Usage

### GUI (recommended)

```bash
python projects/invoice/main.py
```

Navigate through the wizard:

1. **Sign In** — enter ASAN IMZA phone and user ID
2. **ASAN Confirm** — approve the login request on your phone
3. **Certificate** — select the taxpayer certificate
4. **Parameters** — choose inbox/outbox and date range
5. **Progress** — live log; open the generated report when done

### CLI

```bash
python projects/invoice/cli.py
```

Follows the same flow interactively in the terminal.

---

## Data Pipeline

```
ASAN IMZA login
      │
      ▼
list_certificates()  →  Certificate selection
      │
      ▼
get_dashboard()       →  Taxpayer session token
      │
      ▼
get_invoice_urls()    →  Paginated list of invoice URLs
      │
      ▼
get_overheads()       →  Fetch + _parse_invoice() per URL
      │                   returns pd.DataFrame
      ▼
convert_to_xlsx()     →  reports/invoices/<name>.xlsx  (via openpyxl)
```

---

## Package Structure

```
core/                      # Shared root-level library
├── __init__.py            # DEBUG flag
├── services.py            # All API calls + pandas data pipeline
├── models.py              # Certificate dataclass
├── validators.py          # Phone / date / ID validation
├── exceptions.py          # NETWORK_ERRORS and custom exceptions
└── colors.py              # ANSI terminal color codes

projects/invoice/          # Invoice scrapper application
├── __init__.py            # Version, company, copyright
├── i18n.py                # EN / AZ / RU translations
├── main.py                # GUI entry point
├── cli.py                 # CLI entry point
├── adapters/              # OS-specific file/path helpers
│   ├── base.py
│   ├── windows.py
│   ├── macos.py
│   └── linux.py
├── gui/
│   ├── app.py             # MainWindow, theme, language menu
│   ├── workers.py         # QThread workers (LoginWorker, FetchWorker)
│   └── views/
│       ├── login.py
│       ├── asan_confirm.py
│       ├── certificate.py
│       ├── params.py
│       └── progress.py
└── cli/
    ├── commands.py        # CLI workflow
    └── banner.py
```

---

## Building a Windows Executable

Requires Windows with Python 3.11+.

```bat
build.bat
```

Output: `dist/InvoiceScrapper.exe` — single portable executable, no Python installation needed.

---

## License

MIT License — Copyright (c) 2026 Memorise LLC
