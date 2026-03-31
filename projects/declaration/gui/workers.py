import json
import os
from PyQt6.QtCore import QThread, pyqtSignal
from core.services import EtaxesClient
from declaration.i18n import t


class LoginWorker(QThread):
    succeeded = pyqtSignal(object, list)   # (EtaxesClient, certificates)
    failed    = pyqtSignal(str)

    def __init__(self, credentials: dict):
        super().__init__()
        self._credentials = credentials

    def run(self):
        try:
            client = EtaxesClient()
            client.asan_login(self._credentials)
            certs = client.list_certificates()
            self.succeeded.emit(client, certs)
        except SystemExit:
            self.failed.emit(t("w_login_fail"))
        except Exception as e:
            self.failed.emit(str(e))


class LoadDeclarationsWorker(QThread):
    succeeded = pyqtSignal(dict)   # raw declarations response
    failed    = pyqtSignal(str)

    def __init__(self, client: EtaxesClient, certificate, year: int):
        super().__init__()
        self._client      = client
        self._certificate = certificate
        self._year        = year

    def run(self):
        try:
            self._client.get_dashboard(self._certificate)
            declarations = self._client.declaration_list(self._year)
            self.succeeded.emit(declarations)
        except SystemExit:
            self.failed.emit(t("w_terminated"))
        except Exception as e:
            self.failed.emit(str(e))


class FetchWorker(QThread):
    progress  = pyqtSignal(str)
    succeeded = pyqtSignal(str)   # saved filename
    failed    = pyqtSignal(str)

    def __init__(self, client: EtaxesClient, declaration_id: str, year: int):
        super().__init__()
        self._client         = client
        self._declaration_id = declaration_id
        self._year           = year

    def run(self):
        try:
            from openpyxl import Workbook
            from declaration.cli.commands import build_data_dict, write_headers, write_values, _EXCEL_MAP
            from declaration.adapters import get_adapter

            adapter = get_adapter()
            adapter.ensure_dirs()
            os.makedirs("reports/declarations", exist_ok=True)

            self.progress.emit(t("w_fetching"))
            raw_data  = self._client.declaration_get(self._declaration_id)
            json_data = json.loads(raw_data["calcPartJson"])

            self.progress.emit(t("w_generating"))
            wb = Workbook()
            ws = wb.active
            ws.title = "Declaration"

            write_headers(ws, _EXCEL_MAP)
            for i, record in enumerate(json_data):
                write_values(ws, build_data_dict(record), _EXCEL_MAP, col=3 + i)

            filename = f"reports/declarations/{self._declaration_id}_declaration_report_{self._year}.xlsx"
            wb.save(filename)
            self.succeeded.emit(filename)

        except SystemExit:
            self.failed.emit(t("w_terminated"))
        except Exception as e:
            self.failed.emit(str(e))
