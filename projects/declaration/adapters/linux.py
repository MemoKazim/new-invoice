import os
from declaration.adapters.base import BaseAdapter


class LinuxAdapter(BaseAdapter):
    def ensure_dirs(self) -> None:
        for d in ("tmp", "reports", "reports/invoices", "reports/declarations", "log"):
            os.makedirs(d, exist_ok=True)

    def open_report(self, filepath: str) -> None:
        os.system(f"xdg-open {filepath}")
