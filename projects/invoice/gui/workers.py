import time
from PyQt6.QtCore import QThread, pyqtSignal
from invoice.core import services as s
from invoice.i18n import t


class LoginWorker(QThread):
    """Runs asan_login (blocking poll) + list_certificates in a background thread."""

    succeeded = pyqtSignal(object, list)   # (session, certificates)
    failed    = pyqtSignal(str)

    def __init__(self, credentials: dict, session):
        super().__init__()
        self._credentials = credentials
        self._session = session

    def run(self):
        try:
            session = s.asan_login(self._credentials, self._session)
            certs = s.list_certificates(session)
            self.succeeded.emit(session, certs)
        except SystemExit:
            self.failed.emit(t("w_login_fail"))
        except Exception as e:
            self.failed.emit(str(e))


class FetchWorker(QThread):
    """Runs the full fetch pipeline in a background thread."""

    progress  = pyqtSignal(str)
    succeeded = pyqtSignal(str)   # xlsx filename
    failed    = pyqtSignal(str)

    def __init__(self, session, certificate, overhead_choice: str,
                 from_date: str, to_date: str):
        super().__init__()
        self._session = session
        self._certificate = certificate
        self._overhead_choice = overhead_choice
        self._from_date = from_date
        self._to_date = to_date

    def run(self):
        from invoice.adapters import get_adapter

        try:
            adapter = get_adapter()
            adapter.ensure_dirs()
            s.clean_tmp()

            self.progress.emit(t("w_dashboard"))
            session = s.get_dashboard(self._certificate, self._session)

            today = time.localtime()
            overhead_name = self._overhead_choice.split(".")[1]
            filename = (
                f"{overhead_name}_report_"
                f"{self._from_date}-{self._to_date}_"
                f"{today.tm_hour}-{today.tm_min}-{today.tm_sec}.tmp"
            )

            self.progress.emit(t("w_fetch_list"))
            urls = s.get_invoice_urls(
                self._overhead_choice, self._from_date, self._to_date, session
            )

            self.progress.emit(t("w_downloading", n=len(urls)))
            df = s.get_overheads(urls, session)

            self.progress.emit(t("w_logout"))
            s.logout(session)

            self.progress.emit(t("w_generating"))
            s.convert_to_xlsx(df, filename)

            self.succeeded.emit(filename.replace(".tmp", ".xlsx"))

        except SystemExit:
            self.failed.emit(t("w_terminated"))
        except Exception as e:
            self.failed.emit(str(e))
