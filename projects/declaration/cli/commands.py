from core.colors import bcolors as c
from core.services import EtaxesClient
from core import validators as v
from declaration.cli.banner import banner
from declaration.adapters import get_adapter

from openpyxl import load_workbook, Workbook
from openpyxl.utils import get_column_letter
from core.logger import logger
import pandas as pd
import time
import json
import os

_UI = json.load(open("data/json/ui.json", encoding="utf-8"))
_DECLARATIONS_AZ = _UI.get("declarations_az", {})
_TECH_PARK_PREFIX = "apps.declarations.unified.employeeForm.techParkMdssInvolveInfo."

def _tech_park_label(val: str) -> str:
    return _DECLARATIONS_AZ.get(_TECH_PARK_PREFIX + val, val)

def _row_of(cell_ref: str) -> int:
    """Extract row number from a cell reference like 'C5' → 5."""
    return int("".join(filter(str.isdigit, cell_ref)))


def write_headers(ws, excel_map: dict):
    """Write column A (titles/labels) and column B (M1/M2/M3/QR) once per sheet."""
    for field, config in excel_map.items():
        if "merge" in config:
            ws.merge_cells(config["merge"])
        if "title" in config:
            ws[config["coordinate"]] = config["title"]
            for label, key in [("M1", "m1"), ("M2", "m2"), ("M3", "m3"), ("QR", "qr")]:
                if key in config:
                    ws[config[key]] = label
        else:
            ws[config["coordinate"]] = field


def write_values(ws, data: dict, excel_map: dict, col: int):
    """Write one person's values into column `col` (3=C, 4=D, 5=E, …)."""
    letter = get_column_letter(col)
    for field, config in excel_map.items():
        if field not in data:
            continue
        value = data[field]
        if isinstance(value, str):
            ws[f"{letter}{_row_of(config['value'])}"] = value
        elif isinstance(value, list):
            for val_key, val in zip(["v1", "v2", "v3", "vq"], value):
                if val_key in config:
                    ws[f"{letter}{_row_of(config[val_key])}"] = val

def build_data_dict(record: dict) -> dict:
    main = record["main"]
    amounts = {a["indicator"]: a for a in record["amounts"]}

    data = {
        "Fullname": main["fullName"],
        "PIN":      main["pin"],
        "SSN":      main["ssn"],
        "mainWorkPlace": [
            "Bəli" if main.get("mainWorkPlaceM1") else "Xeyr",
            "Bəli" if main.get("mainWorkPlaceM2") else "Xeyr",
            "Bəli" if main.get("mainWorkPlaceM3") else "Xeyr",
            "",
        ],
        "dayCount": [
            main.get("dayCountM1", ""),
            main.get("dayCountM2", ""),
            main.get("dayCountM3", ""),
            main.get("dayCountQuarter", ""),
        ],
        "texnoParkInfo": [
            _tech_park_label(main.get("techParkMdssInvolveInfoM1", "")),
            _tech_park_label(main.get("techParkMdssInvolveInfoM2", "")),
            _tech_park_label(main.get("techParkMdssInvolveInfoM3", "")),
            "",
        ],
    }

    for indicator, amount in amounts.items():
        data[indicator] = [
            amount["amountM1"],
            amount["amountM2"],
            amount["amountM3"],
            amount["amountQuarter"],
        ]

    return data

def simple_row(row: int):
    return {
        "coordinate": f"A{row}",   # header label
        "value":      f"C{row}",   # actual value
    }

def block_row(start: int):
    return {
        "merge":      f"A{start}:A{start+3}",
        "coordinate": f"A{start}",        # section title (merged)
        "m1": f"B{start}",   "v1": f"C{start}",    # M1 label / M1 value
        "m2": f"B{start+1}", "v2": f"C{start+1}",  # M2 label / M2 value
        "m3": f"B{start+2}", "v3": f"C{start+2}",  # M3 label / M3 value
        "qr": f"B{start+3}", "vq": f"C{start+3}",  # QR label / QR value
    }

def get_asan_login() -> dict:
    print(f"{c.FG_GREEN}[+] Getting Asan Login requirements{c.END}")
    print(f"{c.FG_YELLOW}[*] Please enter ASAN Phone number in {c.BOLD}+994XXXXXXXXX{c.END + c.FG_YELLOW} format and User ID. e.g.(+994123456789):\n")

    phone = input(f"{c.FG_YELLOW}Phone: {c.END}")
    while not v.validatePhone(phone):
        print(f"{c.FG_RED}[!] Invalid Phone Number! Try again. {c.END}")
        phone = input(f"{c.FG_YELLOW}Phone: {c.END}")

    user_id = input(f"{c.FG_YELLOW}User ID: {c.END}")
    while not v.validateID(user_id):
        print(f"{c.FG_RED}[!] Invalid ID! Try again. {c.END}")
        user_id = input(f"{c.FG_YELLOW}User ID: {c.END}")

    return {"phone": phone, "id": user_id}

def get_sv_login() -> dict:
    print(f"{c.FG_GREEN}[+] Getting SV requirements{c.END}")

def get_kps_login() -> dict:
    print(f"{c.FG_GREEN}[+] Getting KPS requirements{c.END}")

def sign_in_handler() -> str:
    print(f"{c.FG_YELLOW}[+] Please Select SignIn option from list below!{c.FG_GREEN}")
    print(f"""
  1. Kod / Parol / Sifre  [Currently Unavailable]
  2. Sexsiyyet Vesiqesi   [Currently Unavailable]
  3. Asan Imza {c.END}
  """)

    choice = input(f"{c.FG_YELLOW}[*] Option: {c.END}")
    while True:
        try:
            if int(choice) >= 1 and int(choice) <= 3:
                if int(choice) != 3:
                    print(f"{c.FG_YELLOW}[-] This option is currently unavailable please choose other option!{c.END}")
                    raise Exception
                break
            else:
                raise Exception
        except Exception:
            print(f"{c.FG_RED}[-] Incorrect option! Try again{c.END}")
            choice = input(f"{c.FG_YELLOW}[*] Option: {c.END}")

    return choice

def overhead_handler() -> str:
    print(f"{c.FG_YELLOW}[+] Please Select overhead status!{c.FG_GREEN}")
    print(f"""
  1. Gelen qaimeler
  2. Gonderilen qaimeler{c.END}
  """)

    choice = input(f"{c.FG_YELLOW}[*] Option: {c.END}")
    while True:
        try:
            if int(choice) >= 1 and int(choice) <= 2:
                break
            else:
                raise Exception
        except Exception:
            print(f"{c.FG_RED}[-] Incorrect option! Try again{c.END}")
            choice = input(f"{c.FG_YELLOW}[*] Option: {c.END}")

    return choice

def date_handler() -> tuple:
    print(f"{c.FG_YELLOW}[*] Please enter declaration year you want to fetch: (e.g.: 2025)")

    date = input(f"{c.FG_YELLOW}Date: {c.END}")
    while True:
        try:
            date = int(date)
            break
        except:
            print("Invalid year!")
            date = input(f"{c.FG_YELLOW}Date: {c.END}")
    return date

def certificate_handler(certificates) -> int:
    print(f"{c.FG_YELLOW}[*] Please select tax payer certificate below!{c.FG_GREEN}\n")
    for i, cert in enumerate(certificates, 1):
        print(f'{i}. {cert.tin} - {cert.name}')
    print(f"{c.END}", end='')

    choice = input(f"\n{c.FG_YELLOW}[*] Option: {c.END}")
    while True:
        try:
            if int(choice) > 0 and int(choice) <= len(certificates):
                break
            else:
                raise Exception
        except Exception:
            print(f"{c.FG_RED}[-] Incorrect option! Try again{c.END}")
            choice = input(f"{c.FG_YELLOW}[*] Option: {c.END}")

    return int(choice)

def file_opener_handler(filename: str):
    adapter = get_adapter()
    user_input = input(f"{c.FG_YELLOW}[*] Do you want to open report file? [n/Y]: ")

    if user_input not in ["y", "Y", "", "n", "N"]:
        print(f"{c.FG_YELLOW}[!] Incorrect option. File opening aborted. \nHave a nice day :) {c.END}")
        return

    if user_input in ["y", "Y", ""]:
        print(f"{c.FG_GREEN}[+] Opening file...\nHave a nice day :) {c.END}")
        xlsx_path = f"reports/invoices/{filename.split('.')[0]}.xlsx"
        adapter.open_report(xlsx_path)

    if user_input in ["n", "N"]:
        print(f"{c.FG_YELLOW}[-] File opening aborted. Have a nice day :) {c.END}")

def declaration_handler(
    declarations: list[dict]
) -> None:
    declaration_format = """
{no}.   {year} {month} | {status}
        Id:             {id}
        Tax amount:     {tax_amount}
        Tax name:       {tax_name}
        Delivery type:  {delivery_type}
"""
    print(f"{c.FG_YELLOW}[*] Please choose declaration: {c.FG_GREEN}")
    ui = json.load(open("data/json/ui.json"))
    month_options = ui["ui"][0]["monthOptions"]
    delivery_options = ui["ui"][1]["declarations"]["filters"]
    for no, data in enumerate(declarations["declarations"]):
        declaration = data["declaration"]
        print(declaration_format.format(
            no=no,
            year=declaration["reportingPeriod"]["year"],
            month=month_options[f"{declaration['reportingPeriod']['month']:02d}"],
            status=declaration["declarationStatus"],
            id=declaration["id"],
            tax_amount=f"{declaration['taxAmount']} ₼",
            tax_name=declaration["taxName"],
            delivery_type=delivery_options[declaration["deliveryType"].lower()]
        ))
    
    choice = input(f"\n{c.FG_YELLOW}[*] Option: {c.END}")
    while True:
        try:
            if int(choice) >= 0 and int(choice) < len(declarations["declarations"]):
                choice = int(choice)
                break
            else:
                raise Exception
        except Exception:
            print(f"{c.FG_RED}[-] Incorrect option! Try again{c.END}")
            choice = input(f"{c.FG_YELLOW}[*] Option: {c.END}")

    return declarations["declarations"][choice]["declaration"]["id"]
    
_SIGN_IN_INPUT = {
    "1": get_kps_login,
    "2": get_sv_login,
    "3": get_asan_login,
}

_SIGN_IN = {
    "1": EtaxesClient.kps_login,
    "2": EtaxesClient.sv_login,
    "3": EtaxesClient.asan_login,
}

_EXCEL_MAP = {}

mapping_file = open("data/json/mapping.json", "r")
mapping = json.load(mapping_file)
mapping_file.close()

# Single rows
single_fields = ["Fullname", "PIN", "SSN"]

for i, field in enumerate(single_fields, start=1):
    _EXCEL_MAP[field] = simple_row(i)

# Block sections
block_fields = [
    "mainWorkPlace",
    "dayCount",
    "INCOME_AMOUNT",
    "OTHER_INCOME_AMOUNT",
    "COMPENSATION",
    "MDSS_LIFE_INSURANCE_INVOLVE_AMOUNT",
    "texnoParkInfo",
    "DISCOUNT_AMOUNT",
    "INVOLVE_AMOUNT",
    "TAX_AMOUNT",
    "MDSS_NON_INVOLVE_AMOUNT",
    "MDSS_INVOLVE_AMOUNT",
    "MDSS_INSURER_CALC_AMOUNT",
    "MDSS_INSURER_COMPENSATION_AMOUNT",
    "MDSS_LIFE_INSURANCE_AMOUNT",
    "MDSS_INSURANT_CALC_AMOUNT",
    "MDSS_INSURANT_COMPENSATION_AMOUNT",
    "UNEMPLOYMENT_NON_INVOLVE_AMOUNT",
    "UNEMPLOYMENT_INVOLVE_AMOUNT",
    "UNEMPLOYMENT_INSURER_CALC_AMOUNT",
    "UNEMPLOYMENT_INSURANT_CALC_AMOUNT",
    "COMPULSORY_INSURANCE_NON_INVOLVE_AMOUNT",
    "COMPULSORY_INSURANCE_INVOLVE_AMOUNT",
    "COMPULSORY_INSURANCE_INSURER_CALC_AMOUNT",
    "COMPULSORY_INSURANCE_INSURANT_CALC_AMOUNT",
]

start_row = len(single_fields) + 1

for field in block_fields:
    _EXCEL_MAP[field] = block_row(start_row)
    start_row += 4

for k, x in _EXCEL_MAP.items():
    if k in single_fields: continue
    try:
        _EXCEL_MAP[k]["title"] = f"{mapping[k]['section']} {mapping[k]['title']['az']}"
    except Exception as e:
        logger.exception(e)

def run():
    adapter = get_adapter()
    adapter.ensure_dirs()

    client = EtaxesClient()
    client.clean_tmp()

    print(banner)

    sign_in_choice = sign_in_handler()

    requirements = _SIGN_IN_INPUT[sign_in_choice]()
    _SIGN_IN[sign_in_choice](client, requirements)

    certificates = client.list_certificates()
    cert_choice = certificate_handler(certificates)
    client.get_dashboard(certificates[cert_choice - 1])

    date = date_handler()
    declarations = client.declaration_list(date)
    declaration = declaration_handler(declarations)
    json_data = client.declaration_get(declaration)

    wb = Workbook()
    ws = wb.active
    ws.title = "Declaration"

    write_headers(ws, _EXCEL_MAP)
    for i, record in enumerate(json_data):
        write_values(ws, build_data_dict(record), _EXCEL_MAP, col=3 + i)

    filename = f"reports/declarations/{declaration}_declaration_report_{date}.xlsx"
    wb.save(filename)
    print(f"{c.FG_GREEN}[+] Done: {filename}{c.END}")
    file_opener_handler(filename)