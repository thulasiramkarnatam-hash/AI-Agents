"""OpenAI Agents SDK wrapper for the date-difference tool."""

from agents import Agent, function_tool

from .date_difference import calculate_date_difference_tool


@function_tool
def date_difference_tool(date1: str, date2: str) -> dict[str, int | str]:
    """Calculate complete years, remaining days, and total days between dates."""
    return calculate_date_difference_tool(date1, date2)


root_agent = Agent(
    name="Date Difference Agent",
    instructions=(
        "You calculate differences between two dates. Always use the "
        "date_difference_tool for date arithmetic. Explain the result using "
        "complete calendar years, remaining days, and total days."
    ),
    tools=[date_difference_tool],
)
