from invoice.colors import bcolors as c
from invoice.cli.banner import banner
from invoice.core import validators as v
from invoice.core import services as s
from invoice.adapters import get_adapter
import importlib
import time
import os


def check_lib():
    for lib in ('pandas', 'requests', 'openpyxl'):
        try:
            importlib.import_module(lib)
        except ImportError:
            os.system(f"pip install {lib}")


def get_asan_login() -> dict:
    print(f"{c.FG_GREEN}[+] Getting Asan Login requirements{c.END}")
    print(f"{c.FG_YELLOW}[*] Please enter ASAN Phone number in {c.BOLD}+994XXXXXXXXX{c.END + c.FG_YELLOW} format and User ID. e.g.(+994123456789):\n")

    phone = input(f"{c.FG_YELLOW}Phone: {c.END}")
    while not v.validatePhone(phone):
        print(f"{c.FG_RED}[!] Invalid Phone Number! Try again. {c.END}")
        phone = input(f"{c.FG_YELLOW}Phone:{c.END}")

    user_id = input(f"{c.FG_YELLOW}User ID: {c.END}")
    while not v.validateID(user_id):
        print(f"{c.FG_RED}[!] Invalid ID! Try again. {c.END}")
        user_id = input(f"{c.FG_YELLOW}User ID:{c.END}")

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
    print(f"{c.FG_YELLOW}[*] Please enter Date range in {c.BOLD}dd-mm-yyyy{c.END + c.FG_YELLOW} format. e.g. (30-12-2024)\n")

    from_date = input(f"{c.FG_YELLOW}From: {c.END}")
    while not v.validateDate(from_date):
        print(f"{c.FG_RED}[-] Incorrect fromDate value! Try again!{c.END}\n")
        from_date = input(f"{c.FG_YELLOW}From: {c.END}")

    to_date = input(f"{c.FG_YELLOW}To: {c.END}")
    while not v.validateDate(to_date):
        print(f"{c.FG_RED}[-] Incorrect toDate value! Try again!{c.END}\n")
        to_date = input(f"{c.FG_YELLOW}To: {c.END}")

    return from_date, to_date


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
        xlsx_path = f"reports/{filename.split('.')[0]}.xlsx"
        adapter.open_report(xlsx_path)

    if user_input in ["n", "N"]:
        print(f"{c.FG_YELLOW}[-] File opening aborted. Have a nice day :) {c.END}")


_SIGN_IN_INPUT = {
    "1": get_kps_login,
    "2": get_sv_login,
    "3": get_asan_login,
}

_SIGN_IN = {
    "1": s.kps_login,
    "2": s.sv_login,
    "3": s.asan_login,
}

_OVERHEAD_OPTIONS = {
    "1": "find.inbox",
    "2": "find.outbox",
}


def run():
    adapter = get_adapter()
    adapter.ensure_dirs()

    check_lib()
    s.clean_tmp()

    print(banner)

    sign_in_choice = sign_in_handler()
    overhead_choice = overhead_handler()
    from_date, to_date = date_handler()

    requirements = _SIGN_IN_INPUT[sign_in_choice]()
    session = s.create_session()
    session = _SIGN_IN[sign_in_choice](requirements, session)

    certificates = s.list_certificates(session)
    cert_choice = certificate_handler(certificates)
    selected_cert = certificates[cert_choice - 1]

    session = s.get_dashboard(selected_cert, session)

    today = time.localtime()
    overhead_name = _OVERHEAD_OPTIONS[overhead_choice].split('.')[1]
    filename = f"{overhead_name}_report_{from_date}-{to_date}_{today.tm_hour}-{today.tm_min}-{today.tm_sec}.tmp"

    urls = s.get_invoice_urls(_OVERHEAD_OPTIONS[overhead_choice], from_date, to_date, session)
    df = s.get_overheads(urls, session)
    s.logout(session)
    s.convert_to_xlsx(df, filename)
    file_opener_handler(filename)
