"""Deterministic date-difference calculation used by the agent and UI."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date


@dataclass(frozen=True)
class DateDifference:
    """A normalized calendar and absolute-day difference between two dates."""

    start_date: date
    end_date: date
    years: int
    days: int
    total_days: int

    def as_dict(self) -> dict[str, int | str]:
        """Return a JSON-friendly representation for an agent tool result."""
        values = asdict(self)
        values["start_date"] = self.start_date.isoformat()
        values["end_date"] = self.end_date.isoformat()
        return values


def _anniversary(start_date: date, years: int) -> date:
    """Return an anniversary, using February 28 for a non-leap Feb 29 year."""
    try:
        return start_date.replace(year=start_date.year + years)
    except ValueError:
        return date(start_date.year + years, 2, 28)


def calculate_date_difference(date1: date, date2: date) -> DateDifference:
    """Calculate complete calendar years, remaining days, and total days.

    The interval is absolute: the earlier input becomes ``start_date`` and the
    later input becomes ``end_date``. A year means a completed anniversary,
    rather than a fixed 365-day period.
    """
    start_date, end_date = sorted((date1, date2))
    years = end_date.year - start_date.year
    if _anniversary(start_date, years) > end_date:
        years -= 1
    anniversary = _anniversary(start_date, years)
    return DateDifference(
        start_date=start_date,
        end_date=end_date,
        years=years,
        days=(end_date - anniversary).days,
        total_days=(end_date - start_date).days,
    )


def calculate_date_difference_tool(date1: str, date2: str) -> dict[str, int | str]:
    """Tool entrypoint: calculate the difference between two ISO dates.

    Args:
        date1: First date in YYYY-MM-DD format.
        date2: Second date in YYYY-MM-DD format.
    """
    try:
        parsed_date1 = date.fromisoformat(date1)
        parsed_date2 = date.fromisoformat(date2)
    except ValueError as error:
        raise ValueError("Dates must use the YYYY-MM-DD format.") from error
    return calculate_date_difference(parsed_date1, parsed_date2).as_dict()
