from .multi_agent_csv import (
    Employee,
    CSVReaderAgent,
    DataReviewerAgent,
    CSVMultiAgentSystem,
)

__all__ = [
    "Employee",
    "CSVReaderAgent",
    "DataReviewerAgent",
    "CSVMultiAgentSystem",
]


def main() -> None:
    """Main entry point for the multi-agent CSV system."""
    from .multi_agent_csv import main as csv_main
    csv_main()