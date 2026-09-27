"""
Pydantic models for employee data representation and JSON output.
"""

from pydantic import BaseModel, Field


class Employee(BaseModel):
    """Structured model representing a single employee record."""
    empid: int = Field(description="Unique employee identifier", ge=0)
    empname: str = Field(description="Full name of the employee", min_length=1, max_length=200)
    sal: float = Field(description="Employee salary", ge=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "empid": 1,
                "empname": "John Doe",
                "sal": 75000.0
            }
        }
    }

    def to_json(self) -> str:
        """Convert employee to formatted JSON string."""
        return self.model_dump_json(indent=2)


class EmployeeOutput(BaseModel):
    """Output wrapper for a list of employees."""
    employees: list[Employee] = Field(description="List of employee records")
    total_records: int = Field(description="Total number of employees", ge=0)
    generated_at: str = Field(description="Timestamp of generation", default_factory=lambda: __import__("datetime").datetime.now().isoformat())

    model_config = {
        "json_schema_extra": {
            "example": {
                "employees": [
                    {"empid": 1, "empname": "John Doe", "sal": 75000.0}
                ],
                "total_records": 1,
                "generated_at": "2026-09-27T10:30:00"
            }
        }
    }

    def to_json(self) -> str:
        """Convert employee output to formatted JSON string."""
        return self.model_dump_json(indent=2)


class EmployeeSummary(BaseModel):
    """Summary statistics for employee data."""
    total_employees: int = Field(description="Total count of employees", ge=0)
    average_salary: float = Field(description="Average salary across all employees", ge=0)
    min_salary: float = Field(description="Minimum salary", ge=0)
    max_salary: float = Field(description="Maximum salary", ge=0)
    total_payroll: float = Field(description="Total payroll amount", ge=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_employees": 5,
                "average_salary": 77600.0,
                "min_salary": 68000.0,
                "max_salary": 91000.0,
                "total_payroll": 388000.0
            }
        }
    }

    def to_json(self) -> str:
        """Convert summary to formatted JSON string."""
        return self.model_dump_json(indent=2)