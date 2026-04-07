from projects.invoice.adapters import get_adapter
from projects.invoice.adapters.base import BaseAdapter


def test_get_adapter_returns_base_adapter():
    adapter = get_adapter()
    assert isinstance(adapter, BaseAdapter)


def test_adapter_has_required_methods():
    adapter = get_adapter()
    assert hasattr(adapter, 'ensure_dirs')
    assert hasattr(adapter, 'open_report')
