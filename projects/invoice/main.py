"""GUI entry point — python projects/invoice/main.py"""
import sys
import os

# Must be called before ANY other code when frozen, so the multiprocessing
# worker process (spawned by loguru's enqueue=True) is intercepted before
# it re-imports core.logger and spawns yet another worker → infinite loop.
if getattr(sys, 'frozen', False):
    import multiprocessing
    multiprocessing.freeze_support()

if not getattr(sys, 'frozen', False):
    _here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(_here))                   # projects/ → import invoice
    sys.path.insert(0, os.path.dirname(os.path.dirname(_here)))  # root/    → import core

from invoice.gui.app import launch

if __name__ == "__main__":
    launch()
