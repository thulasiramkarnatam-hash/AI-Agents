"""
Multi-agent system for CSV data processing with OpenAI models.

This module implements a simple multi-agent pattern where:
- Agent 1 (CSVReaderAgent): Reads data from a CSV file
- Agent 2 (DataReviewerAgent): Reviews data for correctness using OpenAI
"""

import csv
import tempfile
import os
from typing import List, Dict, Any
from dataclasses import dataclass
import openai


@dataclass
class Employee:
    """Represents an employee record."""
    empid: str
    empname: str
    sal: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "empid": self.empid,
            "empname": self.empname,
            "sal": self.sal
        }


class CSVReaderAgent:
    """Agent responsible for reading data from CSV files."""

    def __init__(self, openai_api_key: str):
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.name = "CSVReaderAgent"

    def read_csv(self, file_path: str) -> List[Employee]:
        """Read employee data from CSV file."""
        employees = []

        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                employee = Employee(
                    empid=row['empid'],
                    empname=row['empname'],
                    sal=float(row['sal'])
                )
                employees.append(employee)

        return employees

    def summarize_data(self, employees: List[Employee]) -> Dict[str, Any]:
        """Use OpenAI to summarize the employee data."""
        if not employees:
            return {"summary": "No employee data found"}

        data_str = "\n".join([
            f"Employee ID: {e.empid}, Name: {e.empname}, Salary: ${e.sal:,.2f}"
            for e in employees
        ])

        prompt = f"""
Please summarize the following employee data:
{data_str}

Provide:
1. Total number of employees
2. Average salary (calculate manually from the data)
3. Any observations about the data

Keep the response concise.
"""

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        return {
            "raw_data": employees,
            "ai_summary": response.choices[0].message.content.strip()
        }


class DataReviewerAgent:
    """Agent responsible for reviewing and validating data using OpenAI."""

    def __init__(self, openai_api_key: str):
        self.client = openai.OpenAI(api_key=openai_api_key)
        self.name = "DataReviewerAgent"

    def review_data(self, employees: List[Employee]) -> Dict[str, Any]:
        """Review employee data for correctness and anomalies."""
        if not employees:
            return {"is_valid": True, "issues": [], "review": "No data to review"}

        data_str = "\n".join([
            f"Employee ID: {e.empid}, Name: {e.empname}, Salary: ${e.sal:,.2f}"
            for e in employees
        ])

        prompt = f"""
Please review the following employee data for correctness and potential issues:

{data_str}

Check for:
1. Valid employee IDs (non-empty, reasonable format)
2. Valid employee names (non-empty, not suspicious)
3. Reasonable salary values (positive numbers, within expected range)
4. Any duplicate entries
5. Any anomalies or inconsistencies

Respond with:
- is_valid: true if data is correct, false if issues found
- issues: list of specific issues found
- review: detailed review explanation
"""

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            response_format={"type": "json_object"}
        )

        try:
            import json
            result = json.loads(response.choices[0].message.content)
        except:
            result = {
                "is_valid": True,
                "issues": ["Could not parse AI response"],
                "review": response.choices[0].message.content.strip()
            }

        return result


class CSVMultiAgentSystem:
    """Orchestrates the multi-agent CSV processing workflow."""

    def __init__(self, openai_api_key: str):
        self.reader_agent = CSVReaderAgent(openai_api_key)
        self.reviewer_agent = DataReviewerAgent(openai_api_key)
        self.openai_api_key = openai_api_key

    def create_sample_csv(self) -> str:
        """Create a temporary CSV file with sample employee data."""
        sample_data = [
            {"empid": "E001", "empname": "John Smith", "sal": "75000.00"},
            {"empid": "E002", "empname": "Jane Doe", "sal": "82000.50"},
            {"empid": "E003", "empname": "Bob Johnson", "sal": "68000.00"},
            {"empid": "E004", "empname": "Alice Brown", "sal": "91000.75"},
            {"empid": "E005", "empname": "Charlie Wilson", "sal": "72000.25"},
        ]

        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.csv',
            delete=False,
            newline='',
            encoding='utf-8'
        )

        fieldnames = ['empid', 'empname', 'sal']
        writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample_data)
        temp_file.close()

        print(f"Created temporary CSV file: {temp_file.name}")
        return temp_file.name

    def process(self) -> Dict[str, Any]:
        """Run the complete multi-agent workflow."""
        print("=" * 60)
        print("Multi-Agent CSV Processing System")
        print("=" * 60)

        # Step 1: Create temporary CSV
        csv_path = self.create_sample_csv()
        print(f"\n[Reader Agent] Created CSV at: {csv_path}")

        # Step 2: Reader Agent reads the data
        print(f"\n[Reader Agent] Reading data...")
        employees = self.reader_agent.read_csv(csv_path)
        print(f"[Reader Agent] Read {len(employees)} employees")

        # Step 3: Get AI summary from Reader Agent
        print(f"\n[Reader Agent] Generating AI summary...")
        summary_result = self.reader_agent.summarize_data(employees)
        print(f"\n[AI Summary]:\n{summary_result['ai_summary']}")

        # Step 4: Reviewer Agent reviews the data
        print(f"\n[Reviewer Agent] Review initiated...")
        review_result = self.reviewer_agent.review_data(employees)

        print(f"\n[Reviewer Agent] Review Results:")
        print(f"  - Valid: {review_result.get('is_valid', 'Unknown')}")
        if review_result.get('issues'):
            print(f"  - Issues: {review_result['issues']}")
        print(f"  - Review: {review_result.get('review', 'N/A')[:200]}...")

        # Cleanup
        try:
            os.unlink(csv_path)
            print(f"\n[Cleanup] Temporary file removed: {csv_path}")
        except:
            print(f"\n[Warning] Could not remove temporary file")

        return {
            "csv_path": csv_path,
            "employees": employees,
            "summary": summary_result,
            "review": review_result
        }


def main():
    """Main entry point for the multi-agent CSV system."""
    import os

    # Get OpenAI API key from environment or prompt
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set the API key before running:")
        print("  export OPENAI_API_KEY='your-api-key'")
        print("  # or on Windows:")
        print("  set OPENAI_API_KEY=your-api-key")
        return

    # Initialize and run the multi-agent system
    system = CSVMultiAgentSystem(openai_api_key=api_key)
    results = system.process()

    print("\n" + "=" * 60)
    print("Processing Complete!")
    print(f"Total employees processed: {len(results['employees'])}")
    print(f"Data validity: {results['review'].get('is_valid', 'Unknown')}")
    print("=" * 60)


if __name__ == "__main__":
    main()