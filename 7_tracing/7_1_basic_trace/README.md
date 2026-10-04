# 7-1 Basic Trace: Agent Tracing Demonstration

A simple example showing how to implement tracing for multiple agents with a calculation tool, writing logs to a separate file.

## Overview

This project demonstrates:

### 🐛 Multiple agents
- **CalculatorAgent** - Performs calculations with tracing (`add`, `multiply`, `calculate_expression`)
- **OrchestratorAgent** - Coordinates other agents and workflows (`register_agent`, `execute_calculation_workflow`)

### 📋 Tracing implementation
- **Tracer** class - Centralized trace collector with configurable trace levels
- **TraceEvent** struct - Events with timestamps, levels, and metadata
- **Trace levels**: DEBUG, INFO, WARNING, ERROR

### 💾 File-based logging
- Trace events automatically written to `logs/trace_logs.json` as JSON Lines
- Each line is one complete trace event
- Easy to parse, filter, and analyze

### 🧮 Calculation tool
- Addition, multiplication, and expression evaluation with full tracing

## Installation

```bash
# 1. Clone or navigate to the project
cd 7_1_basic_trace

# 2. Ensure Python 3.12+ is available
python --version

# 3. Install dependencies (this project has no external deps)
# Just ensure you're in a Python environment

# 4. Run the tracing demonstration
python src/7_1_basic_trace/__init__.py
```

## Architecture

```
Tracer (centralized trace collector)
    ├── CalculatorAgent "calc-agent-001"  (add, multiply, expressions)
    ├── CalculatorAgent "calc-agent-002"  (add, multiply, expressions)
    └── OrchestratorAgent "orchestrator-001" (workflows, agent coordination)
```

## Trace Levels

- **DEBUG** - Detailed calculation steps
- **INFO** - Agent lifecycle, workflow start/end
- **WARNING** - Non-critical issues
- **ERROR** - Errors and failures

## File-Based Logging

The `Tracer` class can write trace events to a separate log file (`logs/trace_logs.json`). Each line is a JSON object representing one trace event, making it easy to parse and analyze.

```bash
# View the last 5 trace events
tail -5 logs/trace_logs.json

# Filter by agent
grep "calc-agent-001" logs/trace_logs.json

# Parse with Python
python -c "import json; [print(json.loads(l)) for l in open('logs/trace_logs.json') if l.strip() and l.strip() != '[]']"
```

Log file format (JSON Lines):
```json
{"trace_id": "6265d498-03a7-...", "agent_id": "calc-agent-001", "timestamp": "2026-10-04T22:51:18", "level": "INFO", "event_type": "agent_init", "message": "Agent calc-agent-001 initialized", "data": {}}
```

## Running the Demo

```bash
python src/7_1_basic_trace/__init__.py
```

## Sample Output

```
============================================================
TRACING DEMONSTRATION WITH MULTIPLE AGENTS
============================================================

1. Creating agents...
[INFO] calc-agent-001: Agent calc-agent-001 initialized
[INFO] calc-agent-002: Agent calc-agent-002 initialized
[INFO] orchestrator-001: Agent orchestrator-001 initialized

2. Registering agents...
[INFO] orchestrator-001: Registered agent: calc-agent-001
[INFO] orchestrator-001: Registered agent: calc-agent-002

3. Performing individual calculations...
[DEBUG] calc-agent-001: Adding 15 + 25
[DEBUG] calc-agent-001: Result: 15 + 25 = 40
   Agent 001: 15 + 25 = 40
[DEBUG] calc-agent-002: Multiplying 6 * 7
[DEBUG] calc-agent-002: Result: 6 * 7 = 42
   Agent 002: 6 * 7 = 42

4. Expression evaluation...
[INFO] calc-agent-001: Evaluating expression: (10 + 5) * 3
[INFO] calc-agent-001: Expression result: (10 + 5) * 3 = 45
   (10 + 5) * 3 = 45

5. Orchestrated workflow...
[INFO] orchestrator-001: Starting calculation workflow with 4 numbers
[DEBUG] orchestrator-001: Processing number 1/4: 2
[DEBUG] calc-agent-001: Adding 0 + 2
[DEBUG] calc-agent-001: Result: 0 + 2 = 2
[DEBUG] calc-agent-001: Multiplying 1 * 2
[DEBUG] calc-agent-001: Result: 1 * 2 = 2
...
[INFO] orchestrator-001: Workflow completed: {'sum': 14, 'product': 120, 'count': 4, 'average': 3.5}

6. Trace summary:
   Total trace events: 33
   calc-agent-001: 21 events
   calc-agent-002: 3 events
   orchestrator-001: 9 events
```

## Key Components

### Tracer
Centralized trace collection with:
- Unique trace IDs per event
- Timestamp precision
- Agent identification
- Configurable trace levels
- Event filtering by agent

### CalculatorAgent
Performs calculations with full tracing:
- `add(a, b)` - Addition with trace
- `multiply(a, b)` - Multiplication with trace
- `calculate_expression(expr)` - Safe expression evaluation

### OrchestratorAgent
Coordinates multiple agents:
- `register_agent(agent)` - Register sub-agents
- `execute_calculation_workflow(numbers)` - Batch operations with tracing

## Extending the Example

To add more agents:
```python
class DataProcessingAgent(Agent):
    def __init__(self, agent_id, tracer):
        super().__init__(agent_id, tracer)

    def process(self, data):
        self.trace(TraceLevel.INFO, "process_start", f"Processing {len(data)} items")
        # ... processing logic
        self.trace(TraceLevel.INFO, "process_end", f"Completed processing")
```

To export traces to JSON:
```python
import json
events = tracer.get_events()
json_output = json.dumps([asdict(e) for e in events], indent=2)
print(json_output)
```