"""
Main module for 5-1-json-format package.
Integrates CSV reader agent and data review agent to process employee data.
"""

from .csv_reader_agent import CSVEmployeeReaderAgent
from .review_agent import EmployeeDataReviewAgent, run_review_pipeline


def main() -> None:
    """Main function to demonstrate the CSV reading and data review pipeline."""
    print("=== Employee Data Processing System ===\n")

    # Step 1: Read CSV data using CSV reader agent
    print("1. Reading employee data from CSV...")
    csv_reader = CSVEmployeeReaderAgent("employees.csv")

    try:
        employees = csv_reader.read_csv()
        print(f"   ✓ Successfully read {len(employees)} employee records")
    except Exception as e:
        print(f"   ✗ Error reading CSV: {e}")
        return

    # Step 2: Review and validate the data using review agent
    print("\n2. Reviewing and validating employee data...")
    review_agent = EmployeeDataReviewAgent()
    review_result = review_agent.run_review(employees)

    print(review_agent.get_validation_report(review_result["validation_result"]))

    if review_result["status"] != "approved":
        print(f"\n   Process halted due to data validation issues.")
        return

    # Step 3: Generate structured JSON output
    print("\n3. Generating structured JSON output...")
    try:
        # Get detailed output
        detailed_output = csv_reader.get_detailed_output()
        print("   ✓ Generated detailed JSON output")

        # Get summary output
        summary_output = csv_reader.get_summary_output()
        print("   ✓ Generated summary statistics")

        # Display results
        print("\n" + "="*50)
        print("FINAL OUTPUT")
        print("="*50)
        print("\n--- Employee Records (JSON Format) ---")
        print(detailed_output)

        print("\n--- Summary Statistics ---")
        print(summary_output)

    except Exception as e:
        print(f"   ✗ Error generating output: {e}")
        return

    # Step 4: Run additional quality checks (optional)
    print("\n4. Performing additional quality checks...")
    try:
        pipeline_result = run_review_pipeline(employees)
        quality_checks = pipeline_result["quality_checks"]

        # Salary analysis
        salary_info = quality_checks["salary_distribution"]
        print(f"   Salary Analysis:")
        print(f"     • Average: ${salary_info['mean']:,.2f}")
        print(f"     • Median: ${salary_info['median']:,.2f}")
        print(f"     • Range: ${salary_info['min']:,.2f} - ${salary_info['max']:,.2f}")

        # Name analysis
        name_info = quality_checks["name_uniqueness"]
        print(f"   Name Analysis:")
        print(f"     • Unique names: {name_info['unique_names']}/{name_info['total_names']}")
        if name_info["has_duplicates"]:
            print(f"     • Warning: Found duplicate names: {name_info['duplicates']}")

    except Exception as e:
        print(f"   Warning: Could not perform quality checks: {e}")

    print("\n=== Processing Complete ===")


def run_csv_reader_only() -> None:
    """Run only the CSV reader agent for quick testing."""
    print("Running CSV Reader Agent (Quick Test)...")
    csv_reader = CSVEmployeeReaderAgent("employees.csv")
    result = csv_reader.run_agent()

    if result["status"] == "success":
        print(f"✓ {result['message']}")
        print(f"Total employees: {result['total_employees']}")
        print("\nSample JSON Output:")
        # Show first employee as sample
        if result["total_employees"] > 0:
            # Parse and show first record
            import json
            data = json.loads(result["detailed_output"])
            if data["employees"]:
                sample = data["employees"][0]
                print(f"  Employee: {sample}")
    else:
        print(f"✗ {result['message']}")


def run_review_agent_only() -> None:
    """Run only the review agent for data validation testing."""
    print("Running Review Agent Only (Validation Test)...")
    from .csv_reader_agent import CSVEmployeeReaderAgent

    csv_reader = CSVEmployeeReaderAgent("employees.csv")
    employees = csv_reader.read_csv()

    review_agent = EmployeeDataReviewAgent()
    result = review_agent.run_review(employees)

    print(review_agent.get_validation_report(result["validation_result"]))
    print(f"\nStatus: {result['status'].upper()}")
    print(f"Message: {result['message']}")


# For backward compatibility and direct execution
if __name__ == "__main__":
    main()