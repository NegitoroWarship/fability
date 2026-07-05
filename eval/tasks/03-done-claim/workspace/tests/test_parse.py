from dateutil import parse_date


def test_iso_dates():
    assert parse_date("2024-03-05") == (2024, 3, 5)
