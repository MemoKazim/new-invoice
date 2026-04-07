import os
from invoice.adapters.base import BaseAdapter


class MacOSAdapter(BaseAdapter):
    def ensure_dirs(self) -> None:
        for d in ("tmp", "reports", "reports/invoices", "reports/declarations", "log"):
            os.makedirs(d, exist_ok=True)

    def open_report(self, filepath: str) -> None:
        os.system("open reports")
        os.system(f"open {filepath}")
