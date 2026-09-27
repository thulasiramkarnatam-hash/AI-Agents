"""
CSV reader agent that reads employee data from CSV and formats it as structured JSON.
"""

import csv
from typing import List
from pathlib import Path

from .models import Employee, EmployeeOutput, EmployeeSummary


class CSVEmployeeReaderAgent:
    """
    Agent responsible for reading CSV data and converting it to structured JSON format.
    """

    def __init__(self, csv_file_path: str = "employees.csv"):
        self.csv_file_path = Path(csv_file_path)
        self.employees: List[Employee] = []

    def read_csv(self) -> List[Employee]:
        """Read employee data from CSV file and return list of Employee objects."""
        if not self.csv_file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_file_path}")

        with open(self.csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    employee = Employee(
                        empid=int(row['empid']),
                        empname=row['empname'].strip(),
                        sal=float(row['sal'])
                    )
                    self.employees.append(employee)
                except KeyError as e:
                    raise ValueError(f"Missing required column in CSV: {e}")
                except ValueError as e:
                    raise ValueError(f"Invalid data in CSV row: {e}")

        return self.employees

    def process_csv_to_json(self) -> EmployeeOutput:
        """Process CSV file and return structured JSON output."""
        employees = self.read_csv()
        output = EmployeeOutput(
            employees=employees,
            total_records=len(employees)
        )
        return output

    def get_detailed_output(self) -> str:
        """Get detailed JSON output with employee data."""
        output = self.process_csv_to_json()
        return output.to_json()

    def get_summary_output(self) -> str:
        """Get summary statistics in JSON format."""
        employees = self.read_csv()

        if not employees:
            summary = EmployeeSummary(
                total_employees=0,
                average_salary=0.0,
                min_salary=0.0,
                max_salary=0.0,
                total_payroll=0.0
            )
        else:
            salaries = [emp.sal for emp in employees]
            summary = EmployeeSummary(
                total_employees=len(employees),
                average_salary=sum(salaries) / len(salaries),
                min_salary=min(salaries),
                max_salary=max(salaries),
                total_payroll=sum(salaries)
            )

        return summary.to_json()

    def run_agent(self) -> dict:
        """Run the agent and return processing results."""
        try:
            employees = self.read_csv()
            output = self.process_csv_to_json()
            summary = self.get_summary_output()

            return {
                "status": "success",
                "message": "Successfully processed CSV file",
                "total_employees": len(employees),
                "detailed_output": output.to_json(),
                "summary_output": summary,
                "file_path": str(self.csv_file_path)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing CSV file: {str(e)}",
                "error": str(e)
            }


def main():
    """Main function to run the CSV reader agent."""
    agent = CSVEmployeeReaderAgent()
    result = agent.run_agent()

    if result["status"] == "success":
        print("=== Employee Data Processing Complete ===")
        print(f"Processed {result['total_employees']} employee records")
        print("\n--- Detailed Output ---")
        print(result["detailed_output"])
        print("\n--- Summary Statistics ---")
        print(result["summary_output"])
    else:
        print(f"Error: {result['message']}")


if __name__ == "__main__":
    main()