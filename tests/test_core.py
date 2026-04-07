from projects.invoice.core.validators import validateDate, validatePhone, validateID
from projects.invoice.core.services import sanitize_field


def test_validate_date_valid():
    assert validateDate("01-01-2024")
    assert validateDate("31-12-2025")


def test_validate_date_invalid():
    assert not validateDate("1-1-2024")
    assert not validateDate("32-01-2024")
    assert not validateDate("2024-01-01")


def test_validate_phone():
    assert validatePhone("+994123456789")
    assert not validatePhone("0123456789")
    assert not validatePhone("+994abc456789")


def test_validate_id():
    assert validateID("123456")
    assert not validateID("12345")
    assert not validateID("1234567")


def test_sanitize_field_none():
    assert sanitize_field(None) == 0.0


def test_sanitize_field_numbers():
    assert sanitize_field(3.14) == 3.14
    assert sanitize_field(5) == 5.0


def test_sanitize_field_strips_special_chars():
    result = sanitize_field("hello, world")
    assert "," not in result
