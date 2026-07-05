from dateutil import format_date


def test_legacy_display_format():
    assert format_date(2024, 3, 5) == "2024/03/05"
