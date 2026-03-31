"""CLI entry point — python projects/invoice/cli.py"""
import sys
import os

if not getattr(sys, 'frozen', False):
    _here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(_here))                   # projects/ → import invoice
    sys.path.insert(0, os.path.dirname(os.path.dirname(_here)))  # root/    → import core, config

from invoice.cli.commands import run
from core.logger import logger
from core.exceptions import NETWORK_ERRORS

if __name__ == "__main__":
    try:
        if sys.platform == 'nt': os.system('cls')
        else: os.system('clear')
        run()
    except KeyboardInterrupt:
        logger.info("Exiting via keyboard interrupt")
        sys.exit()
    except NETWORK_ERRORS:
        logger.error("Network error — check internet connection")
        sys.exit()
    except Exception:
        logger.exception("Unexpected error — please contact the developer")
        sys.exit()
