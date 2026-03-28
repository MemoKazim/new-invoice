import sys
from invoice.adapters.base import BaseAdapter


def get_adapter() -> BaseAdapter:
    if sys.platform == 'win32':
        from invoice.adapters.windows import WindowsAdapter
        return WindowsAdapter()
    elif sys.platform == 'darwin':
        from invoice.adapters.macos import MacOSAdapter
        return MacOSAdapter()
    else:
        from invoice.adapters.linux import LinuxAdapter
        return LinuxAdapter()
