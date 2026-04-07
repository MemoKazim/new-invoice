import time
from PyQt6.QtCore import QThread, pyqtSignal
from core.services import EtaxesClient
from invoice.i18n import t


class LoginWorker(QThread):
    """Creates an EtaxesClient, runs asan_login + list_certificates in a background thread."""

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


class FetchWorker(QThread):
    """Runs the full fetch pipeline in a background thread."""

    progress  = pyqtSignal(str)
    succeeded = pyqtSignal(str)   # xlsx filename
    failed    = pyqtSignal(str)

    def __init__(self, client: EtaxesClient, certificate,
                 overhead_choice: str, from_date: str, to_date: str):
        super().__init__()
        self._client         = client
        self._certificate    = certificate
        self._overhead_choice = overhead_choice
        self._from_date      = from_date
        self._to_date        = to_date

    def run(self):
        from invoice.adapters import get_adapter

        try:
            adapter = get_adapter()
            adapter.ensure_dirs()
            self._client.clean_tmp()

            self.progress.emit(t("w_dashboard"))
            self._client.get_dashboard(self._certificate)

            today = time.localtime()
            overhead_name = self._overhead_choice.split(".")[1]
            filename = (
                f"{overhead_name}_report_"
                f"{self._from_date}-{self._to_date}_"
                f"{today.tm_hour}-{today.tm_min}-{today.tm_sec}.tmp"
            )

            self.progress.emit(t("w_fetch_list"))
            urls = self._client.get_invoice_urls(
                self._overhead_choice, self._from_date, self._to_date
            )

            self.progress.emit(t("w_downloading", n=len(urls)))
            df = self._client.get_overheads(urls)

            self.progress.emit(t("w_logout"))
            self._client.logout()

            self.progress.emit(t("w_generating"))
            self._client.convert_to_xlsx(df, filename)

            self.succeeded.emit(filename.replace(".tmp", ".xlsx"))

        except SystemExit:
            self.failed.emit(t("w_terminated"))
        except Exception as e:
            self.failed.emit(str(e))
