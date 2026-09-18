from datetime import date

import pytest

from importlib import import_module

_date_difference = import_module("3_agent_with_tool.date_difference")
calculate_date_difference = _date_difference.calculate_date_difference
calculate_date_difference_tool = _date_difference.calculate_date_difference_tool


def test_same_date_is_zero() -> None:
    result = calculate_date_difference(date(2024, 5, 1), date(2024, 5, 1))
    assert (result.years, result.days, result.total_days) == (0, 0, 0)


def test_reversed_inputs_are_normalized() -> None:
    result = calculate_date_difference(date(2025, 1, 1), date(2020, 1, 1))
    assert result.start_date == date(2020, 1, 1)
    assert result.end_date == date(2025, 1, 1)
    assert (result.years, result.days) == (5, 0)


def test_partial_year() -> None:
    result = calculate_date_difference(date(2020, 1, 1), date(2020, 3, 1))
    assert result.years == 0
    assert result.days == 60
    assert result.total_days == 60


def test_leap_day_uses_february_28_anniversary() -> None:
    result = calculate_date_difference(date(2020, 2, 29), date(2021, 3, 1))
    assert (result.years, result.days, result.total_days) == (1, 1, 366)


def test_tool_accepts_iso_dates() -> None:
    result = calculate_date_difference_tool("2020-01-01", "2021-01-02")
    assert result["years"] == 1
    assert result["days"] == 1
    assert result["total_days"] == 367


def test_tool_rejects_invalid_dates() -> None:
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        calculate_date_difference_tool("01/01/2020", "2021-01-01")
