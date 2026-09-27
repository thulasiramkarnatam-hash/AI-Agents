# Employee Data Processing System - JSON Format

A simple multi-agent system that reads employee data from a CSV file, validates it using Pydantic models, and outputs structured JSON.

## Architecture Overview

```
employees.csv → CSV Reader Agent → Review Agent → Structured JSON Output
```

## Components

### 1. CSV File (`employees.csv`)

Source data file containing employee records with columns:
- **empid**: Unique employee identifier (integer)
- **empname**: Full name of the employee (string)
- **sal**: Employee salary (float)

### 2. Pydantic Models (`src/5_1_json_format/models.py`)

Defines three structured data models:

- **`Employee`**: Core model for a single employee record with validation rules:
  - `empid`: Must be a positive integer (≥ 0)
  - `empname`: String between 1-200 characters
  - `sal`: Salary as float (must be ≥ 0)

- **`EmployeeOutput`**: Wrapper model containing a list of employees plus metadata:
  - `employees`: List of `Employee` objects
  - `total_records`: Count of employees
  - `generated_at`: ISO timestamp of generation

- **`EmployeeSummary`**: Statistical summary of employee data:
  - `total_employees`: Total count
  - `average_salary`: Mean salary
  - `min_salary`: Minimum salary
  - `max_salary`: Maximum salary
  - `total_payroll`: Sum of all salaries

### 3. CSV Reader Agent (`src/5_1_json_format/csv_reader_agent.py`)

**Purpose**: Reads employee data from CSV and formats it as structured JSON.

**Key Methods**:
- `read_csv()`: Parses the CSV file and returns a list of `Employee` Pydantic objects
- `process_csv_to_json()`: Converts CSV data to `EmployeeOutput` model
- `get_detailed_output()`: Returns formatted JSON string of all employees
- `get_summary_output()`: Returns JSON string with salary statistics
- `run_agent()`: Executes the full pipeline and returns a result dictionary

**Features**:
- Validates CSV structure and data types
- Handles missing files and invalid data gracefully
- Returns both detailed employee list and summary statistics

### 4. Review Agent (`src/5_1_json_format/review_agent.py`)

**Purpose**: Validates and reviews employee data before it is sent to output.

**Key Components**:

- **`EmployeeDataReviewAgent`**: Main validation agent
  - Validates individual employee records (name length, salary thresholds)
  - Checks for duplicate employee IDs
  - Generates human-readable validation reports
  - Returns approval/rejection status

- **`DataQualityChecker`**: Additional quality analysis
  - Salary distribution analysis (mean, median, quartiles)
  - Name uniqueness verification

**Validation Rules**:
- Employee IDs must be positive and unique
- Employee names must be 2-200 characters
- Salaries are checked against thresholds (min: $20,000, max: $200,000)
- Warnings are generated for out-of-range values

**Functions**:
- `validate_employee()`: Validates a single employee record
- `validate_employee_list()`: Validates all employees and checks for duplicates
- `run_review_pipeline()`: Runs both validation and quality checks

## Usage

### Run the Full Pipeline

```bash
python -m 5_1_json_format
```

Or import and run directly:

```python
from src._1_json_format import main
main()
```

### Run CSV Reader Agent Only

```python
from src._1_json_format import run_csv_reader_only
run_csv_reader_only()
```

### Run Review Agent Only

```python
from src._1_json_format import run_review_agent_only
run_review_agent_only()
```

### Programmatic Usage

```python
from src._1_json_format.csv_reader_agent import CSVEmployeeReaderAgent
from src._1_json_format.review_agent import EmployeeDataReviewAgent

# Step 1: Read CSV data
reader = CSVEmployeeReaderAgent("employees.csv")
employees = reader.read_csv()

# Step 2: Review data
review_agent = EmployeeDataReviewAgent()
result = review_agent.run_review(employees)
print(review_agent.get_validation_report(result["validation_result"]))

# Step 3: Get JSON output
if result["status"] == "approved":
    json_output = reader.get_detailed_output()
    print(json_output)
```

## Example Output

### Employee Records (JSON Format)

```json
{
  "employees": [
    {
      "empid": 1,
      "empname": "John Doe",
      "sal": 75000.0
    },
    {
      "empid": 2,
      "empname": "Jane Smith",
      "sal": 82000.0
    }
  ],
  "total_records": 5,
  "generated_at": "2026-09-27T10:30:00.000000"
}
```

### Summary Statistics (JSON Format)

```json
{
  "total_employees": 5,
  "average_salary": 77600.0,
  "min_salary": 68000.0,
  "max_salary": 91000.0,
  "total_payroll": 388000.0
}
```

### Validation Report

```
=== Data Validation Report ===

✓ All validations passed

No issues found.

Status: APPROVED
Message: Data review passed - ready for output
```

## Project Structure

```
5_1_json_format/
├── employees.csv                    # Source data file
├── pyproject.toml                   # Project configuration
├── README.md                        # This file
└── src/
    └── _1_json_format/
        ├── __init__.py              # Main entry point and pipeline
        ├── models.py                # Pydantic data models
        ├── csv_reader_agent.py      # CSV reader agent
        └── review_agent.py          # Data review agent
```

## Dependencies

- Python ≥ 3.12
- pydantic (for data validation and JSON serialization)

## How It Works

1. **CSV Reader Agent** reads `employees.csv` and converts each row to a Pydantic `Employee` object, enforcing type and validation rules
2. **Review Agent** validates all employee records (checking for duplicates, invalid values, data quality issues)
3. If validation passes, the system outputs structured JSON containing both detailed employee records and summary statistics
4. All output is validated through Pydantic models ensuring consistent, type-safe data structure

## Validation Features

- **Type Safety**: All data validated through Pydantic models
- **Duplicate Detection**: Checks for duplicate employee IDs
- **Range Validation**: Salary thresholds and name length constraints
- **Quality Analysis**: Statistical analysis of salary distribution
- **Error Reporting**: Human-readable validation reports with specific issues
