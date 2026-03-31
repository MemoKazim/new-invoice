from typing import Optional
import pandas as pd
import requests
import time
import json
import sys
import os

from core.logger import logger
from core.models import Certificate
from core.endpoints import _url, HOST

_COLUMNS = [
    "Tarix", "Göndərən tərəf", "Göndərən VÖEN", "Qəbul edən tərəf", "Qəbul edən VÖEN",
    "Qeyd", "Əlavə qeyd", "Serial kod", "Status",
    "Malın adı", "Malın kodu", "Barkod", "Ölçü vahidi",
    "Miqdarı / Həcmi", "Vahidin satış qiyməti", "Cəmi məbləği(manatla) 6*7",
    "Aksiz dərəcəsi(%)", "Aksiz Məbləği(manatla)", "Cəmi 6*7+10",
    "ƏDV-yə 18% cəlb edilən", "ƏDV-yə 0% cəlb edilən", "ƏDV-dən azad olunan",
    "ƏDV-yə cəlb edilməyən", "ƏDV məbləği (11*0.18)", "Yol vergisi",
    "Yekun Məbləğ (11+16+17)", "URL",
]

_SANITIZE_TABLE = str.maketrans({
    "\n": ".", ",": "，", ";": "；", ":": "：",
    "'": "\u2018", '"': "\u201d", "`": "\u2018",
    "(": "（", ")": "）", "{": "｛", "}": "｝", "[": "【", "]": "】",
    "!": "！", "?": "？", "<": "＜", ">": "＞", "&": "＆",
    "$": "＄", "%": "％", "^": "＾", "*": "＊", "+": "＋",
    "-": "－", "=": "＝", "|": "｜",
})

def sanitize_field(field):
    if field is None: return 0.0
    if isinstance(field, float): return field
    if isinstance(field, int): return float(field)
    return str(field).translate(_SANITIZE_TABLE)


def _parse_invoice(json_data: dict, url: str) -> tuple[list[dict], list[str]]:
    """Parse one invoice JSON into row dicts. Returns (rows, failed_refs)."""
    rows = []
    failed_refs = []
    ref = _url("invoice_view") + url.split('/')[-1].replace('sourceSystem', 'source')

    date          = ' '.join(json_data['createdAt'].split('T'))
    sender_name   = sanitize_field(json_data['sender']['name'])
    sender_tin    = sanitize_field(json_data['sender']['tin'])
    receiver_name = sanitize_field(json_data['receiver']['name'])
    receiver_tin  = sanitize_field(json_data['receiver']['tin'])
    comment       = sanitize_field(json_data["invoiceComment"])
    comment2      = sanitize_field(json_data["invoiceComment2"])
    serial_number = sanitize_field(json_data['serialNumber'])
    status        = sanitize_field(json_data['status'])

    for item in json_data['items']:
        try:
            quantity       = float(sanitize_field(item['quantity']))
            price_per_unit = float(sanitize_field(item['pricePerUnit']))
            cost_amount    = quantity * price_per_unit
            excise_rate    = float(sanitize_field(item['exciseRate']))
            excise         = float(sanitize_field(item['excise']))
            cost           = cost_amount + excise
            vat18          = float(sanitize_field(item['vat18']))
            vat_cost       = vat18 * 0.18
            road_tax       = float(sanitize_field(item['roadTax']))

            rows.append({
                "Tarix"                         : date,
                "Göndərən tərəf"                : sender_name,
                "Göndərən VÖEN"                 : sender_tin,
                "Qəbul edən tərəf"              : receiver_name,
                "Qəbul edən VÖEN"               : receiver_tin,
                "Qeyd"                          : comment,
                "Əlavə qeyd"                    : comment2,
                "Serial kod"                    : serial_number,
                "Status"                        : status,
                "Malın adı"                     : sanitize_field(item['productName']),
                "Malın kodu"                    : sanitize_field(item['productGroup']['code']) if item['productGroup'] else None,
                "Barkod"                        : sanitize_field(item['barcode']),
                "Ölçü vahidi"                   : sanitize_field(item['unit']),
                "Miqdarı / Həcmi"               : quantity,
                "Vahidin satış qiyməti"         : price_per_unit,
                "Cəmi məbləği(manatla) 6*7"     : cost_amount,
                "Aksiz dərəcəsi(%)"             : excise_rate,
                "Aksiz Məbləği(manatla)"        : excise,
                "Cəmi 6*7+10"                   : cost,
                "ƏDV-yə 18% cəlb edilən"        : vat18,
                "ƏDV-yə 0% cəlb edilən"         : float(sanitize_field(item['vat0'])),
                "ƏDV-dən azad olunan"           : float(sanitize_field(item['vatFree'])),
                "ƏDV-yə cəlb edilməyən"         : float(sanitize_field(item['exempt'])),
                "ƏDV məbləği (11*0.18)"         : vat_cost,
                "Yol vergisi"                   : road_tax,
                "Yekun Məbləğ (11+16+17)"       : cost + vat_cost + road_tax,
                "URL"                           : ref,
            })
        except Exception as e:
            logger.error("Failed to parse invoice item | ref={} error={}", ref, e)
            failed_refs.append(ref)

    return rows, failed_refs


class EtaxesClient:
    """Stateful HTTP client for the e-taxes.gov.az invoice API."""

    # ── construction ──────────────────────────────────────────────────────

    def __init__(self):
        self._session = self._make_session()

    @staticmethod
    def _make_session() -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "Host": "new.e-taxes.gov.az",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Origin": "https://new.e-taxes.gov.az",
            "Accept-Language": "en-US,en;q=0.5",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Priority": "u=0, i",
            "Te": "trailers",
            "Connection": "keep-alive",
        })
        return session

    # ── authentication ────────────────────────────────────────────────────

    def asan_login(self, data: dict) -> None:
        phone   = data['phone']
        user_id = data['id']

        headers = {
            "Content-Type": "application/json",
            "Referer": f"{HOST}/eportal/az/login/asan",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

        r = self._session.post(
            _url("asan_start"), headers=headers,
            data=json.dumps({"phone": phone, "userId": user_id}),
        )

        try:
            token = r.headers['x-authorization']
            self._session.headers.update({"X-Authorization": f"Bearer {token}"})
        except Exception:
            logger.critical("Incorrect login information — no auth token in response")
            sys.exit()

        logger.info("Logging in via ASAN IMZA — waiting for confirmation on device")

        status_headers = {"Referer": f"{HOST}/eportal/az/verification/asan"}
        fail_count = 0

        while True:
            try:
                r = self._session.get(_url("asan_status"), headers=status_headers)
                while not r.json()['successful']:
                    r = self._session.get(_url("asan_status"), headers=status_headers)
                    time.sleep(3)
                break
            except Exception:
                fail_count += 1
                logger.warning("ASAN IMZA not confirmed yet (attempt {}/3)", fail_count)
                time.sleep(4)
                if fail_count == 3:
                    logger.error("ASAN login timed out after 3 attempts")
                    sys.exit()

        logger.bind(activity=True).success("ASAN IMZA login successful | phone={}", phone)

    def sv_login(self, data: dict) -> None:
        logger.warning("SV login is not available currently")

    def kps_login(self, data: dict) -> None:
        logger.warning("KPS login is not available currently")

    def list_certificates(self) -> list[Certificate]:
        certificates = []
        r = self._session.get(_url("list_certificates"))

        for cert in r.json()['certificates']:
            if not cert['hasAccess']:
                continue
            if cert['taxpayerType'] == 'legal':
                certificates.append(Certificate(
                    tin=cert['legalInfo']['tin'],
                    name=cert['legalInfo']['name'],
                    taxpayer_type='legal',
                ))
            elif cert['taxpayerType'] == 'individual':
                certificates.append(Certificate(
                    tin=cert['individualInfo']['fin'],
                    name=cert['individualInfo']['name'],
                    taxpayer_type='individual',
                ))

        logger.debug("Found {} accessible certificate(s)", len(certificates))
        return certificates

    # ── dashboard ─────────────────────────────────────────────────────────

    def get_dashboard(self, certificate: Certificate) -> None:
        key  = "Tin" if certificate.taxpayer_type == "legal" else "Fin"
        data = {
            "ownerType": certificate.taxpayer_type,
            f"{certificate.taxpayer_type}{key}": certificate.tin,
        }

        headers = {
            'Content-Type': 'application/json',
            'Origin': HOST,
            'Referer': f"{HOST}/eportal/az/verification/companies",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Priority": "u=0, i",
        }

        r = self._session.post(_url("choose_taxpayer"), json=data, headers=headers)

        if not r.json()['successful']:
            logger.error("chooseTaxpayer failed | tin={}", certificate.tin)
            sys.exit()

        self._session.headers.update({'X-Authorization': f"Bearer {r.headers['x-authorization']}"})
        logger.bind(activity=True).info("Dashboard loaded", tin=certificate.tin, type=certificate.taxpayer_type)

    # ── invoices ──────────────────────────────────────────────────────────

    def get_invoice_urls(self, direction: str, from_date: str, to_date: str) -> list[str]:
        filter_data = {
            "sortBy": "creationDate",
            "sortAsc": True,
            "statuses": [
                "approved", "onApproval", "updateApproval", "updateRequested",
                "cancelRequested", "approvedBySystem", "onApprovalEdited",
                "canceled", "deletedBySystem", "deactivated",
                "cancelationRefused", "correctionRefused",
            ],
            "types": ["current", "corrected"],
            "kinds": [
                "defaultInvoice", "agent", "resale", "recycling",
                "taxCodex163", "taxCodex177_5", "returnInvoice", "returnByAgent",
                "returnRecycled", "exportNoteInvoice", "exciseGoodsTransfer", "advanceInvoice",
            ],
            "serialNumber": None, "senderTin": None, "senderName": None,
            "productName": None, "productCode": None, "receiverTin": None, "receiverName": None,
            "creationDateFrom": f"{from_date} 00:00",
            "creationDateTo":   f"{to_date} 23:59",
            "amountFrom": None, "amountTo": None,
            "offset": 0, "maxCount": 200, "actionOwner": None,
        }

        urls = []
        page = 0
        while True:
            filter_data["offset"] = page * filter_data["maxCount"]
            data = self._session.post(_url("invoice_list", direction=direction), json=filter_data).json()
            urls.extend(
                _url("invoice_detail", id=item['id'], source=item['sourceSystem'])
                for item in data['invoices']
            )
            page += 1
            if not data['hasMore']:
                break

        logger.info("Found {} invoice(s) | direction={} from={} to={}", len(urls), direction, from_date, to_date)
        return urls

    def get_overheads(self, urls: list[str]) -> pd.DataFrame:
        logger.info("Downloading {} invoice(s) — this may take a while", len(urls))

        all_rows = []
        failed_refs = []

        for invoice_url in urls:
            rows, fails = _parse_invoice(self._session.get(invoice_url).json(), invoice_url)
            all_rows.extend(rows)
            failed_refs.extend(fails)

        if failed_refs:
            unique_fails = list(dict.fromkeys(failed_refs))
            logger.error("Failed to parse {} invoice(s)", len(unique_fails))
            with open("tmp/fail.csv", "a", encoding="UTF-8") as f:
                for ref in unique_fails:
                    logger.error("  | ref={}", ref)
                    f.write(f"{ref}\n")

        logger.debug("Parsed {} row(s) from {} invoice(s)", len(all_rows), len(urls))
        return pd.DataFrame(all_rows, columns=_COLUMNS)

    # ── session teardown ──────────────────────────────────────────────────

    def logout(self) -> None:
        r = self._session.post(_url("logout"))
        if r.ok:
            logger.bind(activity=True).success("Logged out successfully")
        self._session.cookies.clear()
        self._session.headers = {}
        self._session.close()
        logger.info("Session closed")

    # ── output utilities ──────────────────────────────────────────────────

    @staticmethod
    def convert_to_xlsx(df: pd.DataFrame, filename: str) -> None:
        logger.info("Generating Excel report...")
        xlsx_filename = filename.replace(".tmp", ".xlsx")
        sheet_name = os.path.splitext(xlsx_filename)[0][:31]

        while True:
            try:
                with pd.ExcelWriter(f"reports/invoices/{xlsx_filename}", engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                logger.bind(activity=True).success("Report saved | file=reports/invoices/{}", xlsx_filename)
                break
            except PermissionError:
                logger.warning("Excel file is open — close it and press Enter to retry")
                input()
            except Exception:
                logger.exception("Failed to write Excel file — raw data is in ./tmp/")
                break

    @staticmethod
    def clean_tmp() -> None:
        for file in os.listdir("./tmp"):
            os.remove(f"tmp/{file}")
        logger.debug("Tmp directory cleaned")
    
    def declaration_list(
        self,
        year: int
    ) -> list[tuple]:
        logger.info(f"Fetching declarations...", year=year)
        r = self._session.get(
            _url("declaration_list"),
            params={"year": year}
        )
        return r.json()
    
    def declaration_get(
        self,
        id: int,
    ) -> None:
        logger.info(f"Fetching declaration data...", id=id)
        r = self._session.get(
            _url("declaration_get"),
            params={
                "reg_number": id,
                "offset": 0,
                "maxCount": 1000,
                "private_emp": False,
            }
        )
        return r.json()
