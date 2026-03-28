"""CLI entry point — python projects/invoice/cli.py"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import datetime
import traceback

from invoice.cli.commands import run
from invoice.colors import bcolors as c
from invoice.core.exceptions import NETWORK_ERRORS
import invoice as app

if __name__ == "__main__":
    try:
        if sys.platform == 'nt':
            os.system('cls')
        else:
            os.system('clear')
        run()
    except KeyboardInterrupt:
        print(f"\n{c.FG_RED}[!] Exiting Program! {c.END}")
        sys.exit()
    except NETWORK_ERRORS as e:
        print(f"\n{c.FG_RED}[!] Bad news! Did you connect to the internet? {c.END}")
        sys.exit()
    except Exception as e:
        print(f"\n{c.FG_RED}[!] Unexpected error happened! Please contact to developer! Exiting Program!{c.END}")
        with open("log/error.log", "a", encoding="UTF-8") as ef:
            ef.write(f"{datetime.datetime.now()} - {e}\n")
        if app.DEBUG:
            print(f"{c.FG_RED}[!] Error: {e} {c.END}")
            print(f"{c.FG_RED}[!] Traceback: {traceback.format_exc()} {c.END}")
        sys.exit()
