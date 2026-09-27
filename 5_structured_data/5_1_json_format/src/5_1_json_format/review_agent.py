"""
Data review agent that validates and reviews employee data before final output.
"""

from typing import List, Optional
from dataclasses import dataclass
from .models import Employee, EmployeeOutput, EmployeeSummary


@dataclass
class ValidationResult:
    """Result of data validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]


class EmployeeDataReviewAgent:
    """
    Agent responsible for reviewing and validating employee data before output.
    """

    # Validation rules
    MIN_SALARY = 20000.0
    MAX_SALARY = 200000.0
    MIN_NAME_LENGTH = 2
    MAX_NAME_LENGTH = 200

    def __init__(self):
        self.validation_results: List[ValidationResult] = []

    def validate_employee(self, employee: Employee) -> ValidationResult:
        """Validate a single employee record."""
        errors = []
        warnings = []

        # Validate empid
        if employee.empid <= 0:
            errors.append(f"empid {employee.empid}: must be positive")

        # Validate empname
        if len(employee.empname) < self.MIN_NAME_LENGTH:
            errors.append(f"empname '{employee.empname}': too short (min {self.MIN_NAME_LENGTH} chars)")
        if len(employee.empname) > self.MAX_NAME_LENGTH:
            errors.append(f"empname '{employee.empname}': too long (max {self.MAX_NAME_LENGTH} chars)")
        if not employee.empname.strip():
            errors.append(f"empname: cannot be empty or whitespace")

        # Validate sal
        if employee.sal < self.MIN_SALARY:
            warnings.append(f"sal {employee.sal}: below minimum threshold ({self.MIN_SALARY})")
        if employee.sal > self.MAX_SALARY:
            warnings.append(f"sal {employee.sal}: above maximum threshold ({self.MAX_SALARY})")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def validate_employee_list(self, employees: List[Employee]) -> ValidationResult:
        """Validate a list of employees."""
        all_errors = []
        all_warnings = []

        # Check for duplicate empids
        empids = [emp.empid for emp in employees]
        duplicates = set([eid for eid in empids if empids.count(eid) > 1])
        if duplicates:
            all_errors.append(f"Duplicate empids found: {sorted(duplicates)}")

        # Validate each employee
        for emp in employees:
            result = self.validate_employee(emp)
            all_errors.extend(result.errors)
            all_warnings.extend(result.warnings)

        return ValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings
        )

    def review_employee_output(self, employee_output: EmployeeOutput) -> ValidationResult:
        """Review the complete employee output structure."""
        return self.validate_employee_list(employee_output.employees)

    def get_validation_report(self, result: ValidationResult) -> str:
        """Generate a human-readable validation report."""
        report = ["=== Data Validation Report ===\n"]

        if result.is_valid:
            report.append("✓ All validations passed")
        else:
            report.append("✗ Validation failed")

        if result.errors:
            report.append(f"\nErrors ({len(result.errors)}):")
            for error in result.errors:
                report.append(f"  - {error}")

        if result.warnings:
            report.append(f"\nWarnings ({len(result.warnings)}):")
            for warning in result.warnings:
                report.append(f"  - {warning}")

        if not result.errors and not result.warnings:
            report.append("\nNo issues found.")

        return "\n".join(report)

    def run_review(self, employees: List[Employee]) -> dict:
        """Run the complete review process."""
        validation_result = self.validate_employee_list(employees)
        report = self.get_validation_report(validation_result)

        if validation_result.is_valid:
            status = "approved"
            message = "Data review passed - ready for output"
        else:
            status = "rejected"
            message = "Data review failed - output blocked"

        return {
            "status": status,
            "message": message,
            "validation_result": validation_result,
            "report": report,
            "total_reviewed": len(employees),
            "error_count": len(validation_result.errors),
            "warning_count": len(validation_result.warnings)
        }


class DataQualityChecker:
    """Additional data quality checks for employee data."""

    @staticmethod
    def check_salary_distribution(employees: List[Employee]) -> dict:
        """Analyze salary distribution."""
        if not employees:
            return {"status": "no_data"}

        salaries = [emp.sal for emp in employees]
        sorted_salaries = sorted(salaries)
        n = len(sorted_salaries)

        return {
            "count": n,
            "mean": sum(salaries) / n,
            "median": sorted_salaries[n // 2] if n % 2 == 1 else (sorted_salaries[n // 2 - 1] + sorted_salaries[n // 2]) / 2,
            "min": min(salaries),
            "max": max(salaries),
            "range": max(salaries) - min(salaries),
            "quartiles": {
                "q1": sorted_salaries[n // 4] if n >= 4 else sorted_salaries[0],
                "q3": sorted_salaries[3 * n // 4] if n >= 4 else sorted_salaries[-1]
            }
        }

    @staticmethod
    def check_name_uniqueness(employees: List[Employee]) -> dict:
        """Check for duplicate or similar names."""
        names = [emp.empname.lower().strip() for emp in employees]
        duplicates = [name for name in names if names.count(name) > 1]

        return {
            "total_names": len(names),
            "unique_names": len(set(names)),
            "duplicates": list(set(duplicates)),
            "has_duplicates": len(duplicates) > 0
        }


def run_review_pipeline(employees: List[Employee]) -> dict:
    """Run the complete review pipeline on employee data."""
    review_agent = EmployeeDataReviewAgent()
    quality_checker = DataQualityChecker()

    # Run validation
    review_result = review_agent.run_review(employees)

    # Run quality checks
    salary_analysis = quality_checker.check_salary_distribution(employees)
    name_analysis = quality_checker.check_name_uniqueness(employees)

    return {
        "review_result": review_result,
        "quality_checks": {
            "salary_distribution": salary_analysis,
            "name_uniqueness": name_analysis
        }
    }


def main():
    """Main function to demonstrate the review agent."""
    from .csv_reader_agent import CSVEmployeeReaderAgent

    # Read data
    reader = CSVEmployeeReaderAgent()
    employees = reader.read_csv()

    # Run review
    review_agent = EmployeeDataReviewAgent()
    result = review_agent.run_review(employees)

    print(result["report"])
    print(f"\nStatus: {result['status'].upper()}")
    print(f"Message: {result['message']}")


if __name__ == "__main__":
    main()