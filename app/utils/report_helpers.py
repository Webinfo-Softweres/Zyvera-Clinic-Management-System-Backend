"""
report_helpers.py
=================
Utility functions shared across reporting modules.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, Generator, List, Tuple


def date_range(start: date, end: date) -> Generator[date, None, None]:
    """Yield every date from start to end inclusive."""
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def fill_daily_gaps(
    breakdown: List[Dict[str, Any]],
    start: date,
    end: date,
    date_key: str = "report_date",
    value_key: str = "registrations",
) -> List[Dict[str, Any]]:
    """
    Given a sparse breakdown list, fill in missing dates with a zero value.
    Useful for charting / consistent monthly breakdowns.
    """
    existing = {str(row[date_key]): row[value_key] for row in breakdown}
    result = []
    for d in date_range(start, end):
        result.append({date_key: d, value_key: existing.get(str(d), 0)})
    return result


def format_hospital_no(seq: int) -> str:
    """Format an integer sequence into HSP-padded hospital number."""
    return f"HSP{seq:06d}"


def month_boundaries(month: int, year: int) -> Tuple[date, date]:
    """Return (first_day, last_day) for the given month and year."""
    import calendar
    first = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    last = date(year, month, last_day)
    return first, last


def safe_str(value: Any, default: str = "N/A") -> str:
    """Convert value to string safely, returning default for None."""
    if value is None:
        return default
    return str(value)


def paginate(query, page: int, size: int):
    """Apply offset/limit pagination to a SQLAlchemy query."""
    skip = (page - 1) * size
    total = query.count()
    items = query.offset(skip).limit(size).all()
    return items, total
