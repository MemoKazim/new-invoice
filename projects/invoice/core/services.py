import pandas as pd
import datetime
import requests
import time
import json
import sys
import os

from invoice.colors import bcolors as c
from invoice.core.models import Certificate
import invoice as app

HOST = "https://new.e-taxes.gov.az"

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


def create_session() -> requests.Session:
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


def asan_login(data: dict, session: requests.Session) -> requests.Session:
    phone = data['phone']
    user_id = data['id']

    headers = {
        "Content-Type": "application/json",
        "Referer": "https://new.e-taxes.gov.az/eportal/az/login/asan",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    payload = json.dumps({"phone": phone, "userId": user_id})
    r = session.post(HOST + "/api/po/auth/public/v1/asanImza/start", headers=headers, data=payload)

    try:
        token = r.headers['x-authorization']
        session.headers.update({"X-Authorization": f"Bearer {token}"})
    except Exception:
        print(f"{c.FG_RED}[!] Incorrect login information. Exiting...{c.END}")
        sys.exit()

    print(f"{c.FG_GREEN}[+] Logging in system via ASAN IMZA\n{c.FG_YELLOW}[*] Waiting for confirmation!{c.END}")

    temp_header = {"Referer": "https://new.e-taxes.gov.az/eportal/az/verification/asan"}
    fail_count = 0

    while True:
        try:
            r = session.get(HOST + "/api/po/auth/public/v1/asanImza/status", headers=temp_header)
            while not r.json()['successful']:
                r = session.get(HOST + "/api/po/auth/public/v1/asanImza/status", headers=temp_header)
                time.sleep(3)
            break
        except Exception:
            fail_count += 1
            print(f"{c.FG_RED}[-] ASAN IMZA is not confirmed yet!{c.END}")
            time.sleep(4)
            r = session.get(HOST + "/api/po/auth/public/v1/asanImza/status", headers=temp_header)
            if fail_count == 3:
                print(f"{c.FG_RED}[!] Something went wrong. Please try again. \nExiting program...{c.END}")
                sys.exit()

    print(f"{c.FG_GREEN}[+] Login Success!{c.END}")
    return session


def sv_login(data: dict, session: requests.Session) -> requests.Session:
    print(f"{c.FG_YELLOW}[*] This login functionality is not available currently.{c.END}")
    return session


def kps_login(data: dict, session: requests.Session) -> requests.Session:
    print(f"{c.FG_YELLOW}[*] This login functionality is not available currently.{c.END}")
    return session


def list_certificates(session: requests.Session) -> list[Certificate]:
    certificates = []
    r = session.get(HOST + "/api/po/auth/public/v1/asanImza/certificates")

    for cert in r.json()['certificates']:
        if not cert['hasAccess']:
            continue
        if cert['taxpayerType'] == 'legal':
            name = cert['legalInfo']['name']
            tin = cert['legalInfo']['tin']
            certificates.append(Certificate(tin=tin, name=name, taxpayer_type='legal'))
        if cert['taxpayerType'] == 'individual':
            name = cert['individualInfo']['name']
            tin = cert['individualInfo']['fin']
            certificates.append(Certificate(tin=tin, name=name, taxpayer_type='individual'))

    return certificates


def get_dashboard(certificate: Certificate, session: requests.Session) -> requests.Session:
    data = {}
    if certificate.taxpayer_type == "legal":
        data = {"ownerType": certificate.taxpayer_type, f"{certificate.taxpayer_type}Tin": certificate.tin}
    if certificate.taxpayer_type == "individual":
        data = {"ownerType": certificate.taxpayer_type, f"{certificate.taxpayer_type}Fin": certificate.tin}

    headers = {
        'Content-Type': 'application/json',
        'Origin': 'https://new.e-taxes.gov.az',
        'Referer': 'https://new.e-taxes.gov.az/eportal/az/verification/companies',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Priority": "u=0, i",
    }

    r = session.post(HOST + "/api/po/auth/public/v1/asanImza/chooseTaxpayer", json=data, headers=headers)

    if not r.json()['successful']:
        print(f"{c.FG_RED}[!] Something went wrong. Please try again later{c.END}")
        sys.exit()

    session.headers.update({'X-Authorization': f"Bearer {r.headers['x-authorization']}"})
    return session


def get_invoice_urls(overhead_choice: str, from_date: str, to_date: str, session: requests.Session) -> list[str]:
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
        "creationDateTo": f"{to_date} 23:59",
        "amountFrom": None, "amountTo": None,
        "offset": 0, "maxCount": 200, "actionOwner": None,
    }

    urls = []
    page = 0
    while True:
        filter_data["offset"] = page * filter_data["maxCount"]
        data = session.post(
            HOST + f"/api/po/invoice/public/v2/invoice/{overhead_choice}", json=filter_data
        ).json()
        urls.extend(
            f"{HOST}/api/po/invoice/public/v2/invoice/{item['id']}?sourceSystem={item['sourceSystem']}"
            for item in data['invoices']
        )
        page += 1
        if not data['hasMore']:
            break

    return urls


def get_overheads(urls: list[str], session: requests.Session) -> pd.DataFrame:
    print(f"{c.FG_GREEN}[*] Retrieving data from server. Please wait.\n[*] This might take a while{c.END}")

    all_rows = []
    failed_urls = []

    for invoice_url in urls:
        rows, fails = _parse_invoice(session.get(invoice_url).json(), invoice_url)
        all_rows.extend(rows)
        failed_urls.extend(fails)

    if failed_urls:
        print(f"{c.FG_RED}[!] Failed to parse some URLs. See below:{c.END}")
        with open("tmp/fail.csv", "a", encoding="UTF-8") as f:
            for failed_url in dict.fromkeys(failed_urls):   # deduplicated, order-preserved
                f.write(f"{failed_url}\n")
                print(f"{c.FG_RED}Source [-] {failed_url}{c.END}")

    return pd.DataFrame(all_rows, columns=_COLUMNS)


def logout(session: requests.Session):
    r = session.post(HOST + "/api/po/auth/public/v1/legacyLogout")
    if r.ok:
        print(f"{c.FG_GREEN}[+] Successfully logged out.{c.END}")
    session.cookies.clear()
    session.headers = {}
    print(f"{c.FG_GREEN}[+] Session terminated!{c.END}")
    session.close()


def sanitize_field(field):
    if field is None:
        return 0.0
    if isinstance(field, float):
        return field
    if isinstance(field, int):
        return float(field)
    return str(field).translate(_SANITIZE_TABLE)


def _parse_invoice(json_data: dict, url: str) -> tuple[list[dict], list[str]]:
    """Parse one invoice JSON into a list of row dicts. Returns (rows, failed_urls)."""
    rows = []
    failed_urls = []
    ref = (
        "https://new.e-taxes.gov.az/eportal/az/invoice/view/"
        + url.split('/')[-1].replace('sourceSystem', 'source')
    )

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
                "Tarix":                        date,
                "Göndərən tərəf":               sender_name,
                "Göndərən VÖEN":                sender_tin,
                "Qəbul edən tərəf":             receiver_name,
                "Qəbul edən VÖEN":              receiver_tin,
                "Qeyd":                         comment,
                "Əlavə qeyd":                   comment2,
                "Serial kod":                   serial_number,
                "Status":                       status,
                "Malın adı":                    sanitize_field(item['productName']),
                "Malın kodu":                   sanitize_field(item['productGroup']['code']) if item['productGroup'] else None,
                "Barkod":                       sanitize_field(item['barcode']),
                "Ölçü vahidi":                  sanitize_field(item['unit']),
                "Miqdarı / Həcmi":              quantity,
                "Vahidin satış qiyməti":        price_per_unit,
                "Cəmi məbləği(manatla) 6*7":   cost_amount,
                "Aksiz dərəcəsi(%)":            excise_rate,
                "Aksiz Məbləği(manatla)":       excise,
                "Cəmi 6*7+10":                  cost,
                "ƏDV-yə 18% cəlb edilən":      vat18,
                "ƏDV-yə 0% cəlb edilən":       float(sanitize_field(item['vat0'])),
                "ƏDV-dən azad olunan":          float(sanitize_field(item['vatFree'])),
                "ƏDV-yə cəlb edilməyən":       float(sanitize_field(item['exempt'])),
                "ƏDV məbləği (11*0.18)":        vat_cost,
                "Yol vergisi":                  road_tax,
                "Yekun Məbləğ (11+16+17)":     cost + vat_cost + road_tax,
                "URL":                          ref,
            })
        except Exception as e:
            if app.DEBUG:
                print(f"{c.FG_RED}[!] Error parsing item: {e}{c.END}")
            with open("log/error.log", "a", encoding="UTF-8") as ef:
                ef.write(f"{datetime.datetime.now()} - {e}\n")
            failed_urls.append(ref)

    return rows, failed_urls


def convert_to_xlsx(df: pd.DataFrame, filename: str):
    import traceback

    print(f"{c.FG_GREEN}[+] Generating excel report, please wait...{c.END}")
    xlsx_filename = filename.replace(".tmp", ".xlsx")
    sheet_name = os.path.splitext(xlsx_filename)[0][:31]

    while True:
        try:
            with pd.ExcelWriter(f"reports/{xlsx_filename}", engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"{c.FG_GREEN}[+] Generated excel file under ./reports/{c.END}")
            break
        except PermissionError:
            input(f"{c.FG_YELLOW}[*] Excel file is open. Please close it and press Enter to retry...{c.END}")
        except Exception as e:
            print(f"{c.FG_RED}[!] Could not convert to Excel. Falling back — raw data in ./tmp/{c.END}")
            if app.DEBUG:
                traceback.print_exc()
            break


def clean_tmp():
    for file in os.listdir("./tmp"):
        os.remove(f"tmp/{file}")
    print(f"{c.FG_GREEN}[+] Tmp directory cleaned{c.END}")
