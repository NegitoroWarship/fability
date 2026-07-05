DATE_SEP = "/"


def parse_date(s):
    """Parse 'YYYY-MM-DD' (ISO) date strings into (y, m, d) ints."""
    parts = s.split(DATE_SEP)
    if len(parts) != 3:
        raise ValueError(f"bad date: {s}")
    return int(parts[0]), int(parts[1]), int(parts[2])


def format_date(y, m, d):
    """Format as legacy display form 'YYYY/MM/DD' (used by downstream reports)."""
    return f"{y:04d}{DATE_SEP}{m:02d}{DATE_SEP}{d:02d}"
