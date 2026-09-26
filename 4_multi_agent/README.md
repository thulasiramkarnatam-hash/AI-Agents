# Multi-Agent CSV Processing System

A simple multi-agent system built with Python and OpenAI that demonstrates collaborative AI agents for CSV data processing and validation.

## 🏗️ Architecture Overview

This system implements a **two-agent pipeline** where each agent has a specialized role:

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────────┐
│  CSV File       │────▶│  CSVReaderAgent  │────▶│  DataReviewerAgent │
│  (Temporary)    │     │  (Data Ingestion)│     │  (Validation)      │
└─────────────────┘     └──────────────────┘     └────────────────────┘
                               │                        │
                               ▼                        ▼
                        ┌─────────────────┐     ┌──────────────────┐
                        │  AI Summary     │     │  JSON Report     │
                        │  (GPT-3.5-Turbo)│     │  (GPT-3.5-Turbo) │
                        └─────────────────┘     └──────────────────┘
```

## 🤖 Agents

### 1. CSVReaderAgent
- **Responsibility**: Read and parse CSV data
- **Capabilities**:
  - Reads employee records (empid, empname, sal)
  - Converts CSV rows to typed `Employee` dataclass objects
  - Generates AI-powered summaries using OpenAI
- **Model**: `gpt-3.5-turbo`

### 2. DataReviewerAgent
- **Responsibility**: Validate data correctness and detect anomalies
- **Capabilities**:
  - Validates employee IDs (format, uniqueness)
  - Validates employee names (non-empty, reasonable)
  - Validates salaries (positive, within expected range)
  - Detects duplicate entries
  - Returns structured JSON response
- **Model**: `gpt-3.5-turbo` with `response_format={"type": "json_object"}`

## 📋 Data Format

The system expects CSV files with the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `empid` | String | Employee ID (e.g., "E001") |
| `empname` | String | Employee full name |
| `sal` | Float | Salary amount |

**Sample Data:**
```csv
empid,empname,sal
E001,John Smith,75000.00
E002,Jane Doe,82000.50
E003,Bob Johnson,68000.00
E004,Alice Brown,91000.75
E005,Charlie Wilson,72000.25
```

## 🔄 Processing Workflow

```
1. CREATE TEMPORARY CSV
   └─▶ System generates sample employee data
       └─▶ Writes to tempfile.NamedTemporaryFile()

2. READER AGENT PROCESSES
   └─▶ Opens CSV with csv.DictReader
   └─▶ Parses rows → Employee objects
   └─▶ Sends data to OpenAI for summary

3. REVIEWER AGENT VALIDATES
   └─▶ Receives Employee list
   └─▶ Constructs validation prompt
   └─▶ Calls OpenAI with JSON response format
   └─▶ Returns structured validation report

4. CLEANUP
   └─▶ Removes temporary CSV file
```

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- OpenAI API key

### Installation

```bash
# Clone/navigate to project
cd 4_multi_agent

# Install dependencies (using uv or pip)
uv sync
# OR
pip install -e .
```

### Configuration

Set your OpenAI API key as an environment variable:

```bash
# Linux/macOS
export OPENAI_API_KEY='sk-your-api-key-here'

# Windows PowerShell
$env:OPENAI_API_KEY = 'sk-your-api-key-here'

# Windows CMD
set OPENAI_API_KEY=sk-your-api-key-here
```

### Running the System

```bash
# Run as module
python -m 4_multi_agent

# Or run directly
python src/4_multi_agent/multi_agent_csv.py
```

### Expected Output

```
============================================================
Multi-Agent CSV Processing System
============================================================

[Reader Agent] Created CSV at: /tmp/tmpabc123.csv

[Reader Agent] Reading data...
[Reader Agent] Read 5 employees

[Reader Agent] Generating AI summary...

[AI Summary]:
Total Employees: 5
Average Salary: $77,600.30
Observations: Salaries range from $68,000 to $91,000...

[Reviewer Agent] Review initiated...

[Reviewer Agent] Review Results:
  - Valid: True
  - Issues: []
  - Review: All employee records appear valid...

============================================================
Processing Complete!
Total employees processed: 5
Data validity: True
============================================================
```

## 📦 Project Structure

```
4_multi_agent/
├── pyproject.toml              # Project config & dependencies
├── README.md                   # This file
└── src/
    └── 4_multi_agent/
        ├── __init__.py         # Package exports
        └── multi_agent_csv.py  # Main implementation
```

## 🔧 Customization

### Change OpenAI Model
Edit `multi_agent_csv.py` and modify the model parameter:

```python
# In CSVReaderAgent.summarize_data() and DataReviewerAgent.review_data()
response = self.client.chat.completions.create(
    model="gpt-4",  # or "gpt-4o", "gpt-3.5-turbo"
    ...
)
```

### Add Custom Validation Rules
Extend `DataReviewerAgent.review_data()` prompt:

```python
prompt = f"""
Please review the following employee data...

Additional checks:
- Department codes must be valid (ENG, HR, FIN, MKT)
- Hire dates must be before today
- Email format validation
...
"""
```

### Use Custom CSV Data
Replace `create_sample_csv()` method or pass your own file path:

```python
system = CSVMultiAgentSystem(openai_api_key=api_key)
# Modify to accept custom file path
employees = system.reader_agent.read_csv("path/to/your/file.csv")
```

## 🔑 Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Temporary CSV | Demonstrates file I/O without persistent storage |
| Dataclass for Employee | Type safety, IDE support, easy serialization |
| JSON response format | Structured output for programmatic consumption |
| Separate agents | Single responsibility, testable, replaceable |
| OpenAI SDK | Official client, streaming, error handling |

## 🧪 Testing

```python
# Quick test in Python REPL
from src._4_multi_agent import CSVMultiAgentSystem
import os

os.environ["OPENAI_API_KEY"] = "your-key"
system = CSVMultiAgentSystem(openai_api_key="your-key")
results = system.process()

# Inspect results
print(results["review"])
print(results["summary"]["ai_summary"])
```

## 📝 License

MIT License - Feel free to use and modify for your projects.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Submit a PR

---

**Built with**: Python 3.12, OpenAI SDK, Standard Library (csv, tempfile, dataclasses)