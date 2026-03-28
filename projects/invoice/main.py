"""GUI entry point — python projects/invoice/main.py"""
import sys
import os

# sys.path manipulation is only needed when running as a plain Python script.
# PyInstaller's bootloader handles imports automatically in the frozen .exe.
if not getattr(sys, 'frozen', False):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from invoice.gui.app import launch

if __name__ == "__main__":
    launch()
