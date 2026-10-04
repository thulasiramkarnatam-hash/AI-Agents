"""
Basic tracing example with multiple agents and calculation tool.
"""

import time
import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import uuid


class TraceLevel(Enum):
    """Trace levels for different verbosity."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class TraceEvent:
    """Represents a single trace event."""
    trace_id: str
    agent_id: str
    timestamp: float
    level: TraceLevel
    event_type: str
    message: str
    data: Dict[str, Any]


class Tracer:
    """Simple tracer implementation for collecting trace events."""

    def __init__(self, log_file: Optional[str] = None):
        self.events: List[TraceEvent] = []
        self.enabled = True
        self.log_file = log_file
        if self.log_file:
            # Ensure the log directory exists
            log_dir = os.path.dirname(os.path.abspath(self.log_file))
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            # Start a fresh log file
            with open(self.log_file, "w") as f:
                f.write("[]\n")  # Initialize empty JSON array

    def trace(self, agent_id: str, level: TraceLevel, event_type: str,
              message: str, data: Dict[str, Any] = None):
        """Record a trace event."""
        if not self.enabled:
            return

        event = TraceEvent(
            trace_id=str(uuid.uuid4()),
            agent_id=agent_id,
            timestamp=time.time(),
            level=level,
            event_type=event_type,
            message=message,
            data=data or {}
        )
        self.events.append(event)
        # Also print to console for demo
        print(f"[{event.level.value}] {event.agent_id}: {event.message}")
        # Write to log file if configured
        if self.log_file:
            self._write_to_log_file(event)

    def _write_to_log_file(self, event: TraceEvent):
        """Append a single trace event to the log file as JSON."""
        event_data = asdict(event)
        # Convert TraceLevel enum to string for JSON serialization
        event_data["level"] = event.level.value
        # Convert timestamp to ISO format for readability
        event_data["timestamp"] = time.strftime(
            "%Y-%m-%dT%H:%M:%S", time.localtime(event.timestamp)
        )
        with open(self.log_file, "a") as f:
            f.write(json.dumps(event_data) + "\n")

    def clear_log_file(self):
        """Clear the log file while keeping the in-memory events."""
        if self.log_file:
            # Keep the header [] line for JSON array compatibility
            with open(self.log_file, "w") as f:
                f.write("[]\n")

    def get_events(self, agent_id: str = None) -> List[TraceEvent]:
        """Get trace events, optionally filtered by agent."""
        if agent_id:
            return [e for e in self.events if e.agent_id == agent_id]
        return self.events.copy()

    def clear(self):
        """Clear all trace events."""
        self.events.clear()


class Agent:
    """Base agent class with tracing capabilities."""

    def __init__(self, agent_id: str, tracer: Tracer = None):
        self.agent_id = agent_id
        self.tracer = tracer or Tracer()
        self.tracer.trace(
            self.agent_id,
            TraceLevel.INFO,
            "agent_init",
            f"Agent {self.agent_id} initialized"
        )

    def trace(self, level: TraceLevel, event_type: str, message: str,
              data: Dict[str, Any] = None):
        """Convenience method for tracing."""
        self.tracer.trace(self.agent_id, level, event_type, message, data)


class CalculatorAgent(Agent):
    """Agent that performs calculations with tracing."""

    def __init__(self, agent_id: str, tracer: Tracer = None):
        super().__init__(agent_id, tracer)

    def add(self, a: float, b: float) -> float:
        """Add two numbers with tracing."""
        self.trace(
            TraceLevel.DEBUG,
            "calculation_start",
            f"Adding {a} + {b}",
            {"operation": "add", "operands": [a, b]}
        )

        # Simulate some processing time
        time.sleep(0.01)

        result = a + b

        self.trace(
            TraceLevel.DEBUG,
            "calculation_end",
            f"Result: {a} + {b} = {result}",
            {"operation": "add", "operands": [a, b], "result": result}
        )

        return result

    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers with tracing."""
        self.trace(
            TraceLevel.DEBUG,
            "calculation_start",
            f"Multiplying {a} * {b}",
            {"operation": "multiply", "operands": [a, b]}
        )

        time.sleep(0.01)

        result = a * b

        self.trace(
            TraceLevel.DEBUG,
            "calculation_end",
            f"Result: {a} * {b} = {result}",
            {"operation": "multiply", "operands": [a, b], "result": result}
        )

        return result

    def calculate_expression(self, expression: str) -> float:
        """Calculate a simple expression with tracing."""
        self.trace(
            TraceLevel.INFO,
            "expression_start",
            f"Evaluating expression: {expression}",
            {"expression": expression}
        )

        try:
            # Simple safe evaluation for demo - in real code, use proper parser
            # Only allow basic arithmetic for safety
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                raise ValueError("Invalid characters in expression")

            result = eval(expression)  # nosec - controlled input for demo

            self.trace(
                TraceLevel.INFO,
                "expression_end",
                f"Expression result: {expression} = {result}",
                {"expression": expression, "result": result}
            )

            return result
        except Exception as e:
            self.trace(
                TraceLevel.ERROR,
                "expression_error",
                f"Error evaluating expression: {str(e)}",
                {"expression": expression, "error": str(e)}
            )
            raise


class OrchestratorAgent(Agent):
    """Agent that orchestrates other agents with tracing."""

    def __init__(self, agent_id: str, tracer: Tracer = None):
        super().__init__(agent_id, tracer)
        self.sub_agents: Dict[str, Agent] = {}

    def register_agent(self, agent: Agent):
        """Register a sub-agent."""
        self.sub_agents[agent.agent_id] = agent
        self.trace(
            TraceLevel.INFO,
            "agent_registered",
            f"Registered agent: {agent.agent_id}",
            {"agent_id": agent.agent_id, "total_agents": len(self.sub_agents)}
        )

    def execute_calculation_workflow(self, numbers: List[float]) -> Dict[str, Any]:
        """Execute a calculation workflow using registered agents."""
        self.trace(
            TraceLevel.INFO,
            "workflow_start",
            f"Starting calculation workflow with {len(numbers)} numbers",
            {"numbers": numbers, "agent_count": len(self.sub_agents)}
        )

        results = {}

        # Use first available calculator agent
        calc_agent = None
        for agent in self.sub_agents.values():
            if isinstance(agent, CalculatorAgent):
                calc_agent = agent
                break

        if not calc_agent:
            self.trace(
                TraceLevel.ERROR,
                "workflow_error",
                "No calculator agent available",
                {}
            )
            return {"error": "No calculator agent available"}

        # Perform calculations
        total_sum = 0
        total_product = 1

        for i, num in enumerate(numbers):
            self.trace(
                TraceLevel.DEBUG,
                "workflow_step",
                f"Processing number {i+1}/{len(numbers)}: {num}",
                {"step": i+1, "number": num}
            )

            # Add to sum
            total_sum = calc_agent.add(total_sum, num)

            # Multiply for product
            total_product = calc_agent.multiply(total_product, num)

        results = {
            "sum": total_sum,
            "product": total_product,
            "count": len(numbers),
            "average": total_sum / len(numbers) if numbers else 0
        }

        self.trace(
            TraceLevel.INFO,
            "workflow_complete",
            f"Workflow completed: {results}",
            results
        )

        return results


def demonstrate_tracing():
    """Demonstrate tracing with multiple agents."""
    print("=" * 60)
    print("TRACING DEMONSTRATION WITH MULTIPLE AGENTS")
    print("=" * 60)

    # Create a shared tracer with log file
    log_file = os.path.join(os.getcwd(), "logs", "trace_logs.json")
    tracer = Tracer(log_file=log_file)

    # Create agents
    print("\n1. Creating agents...")
    calc_agent1 = CalculatorAgent("calc-agent-001", tracer)
    calc_agent2 = CalculatorAgent("calc-agent-002", tracer)
    orchestrator = OrchestratorAgent("orchestrator-001", tracer)

    # Register agents with orchestrator
    print("\n2. Registering agents...")
    orchestrator.register_agent(calc_agent1)
    orchestrator.register_agent(calc_agent2)

    # Individual calculations
    print("\n3. Performing individual calculations...")
    print("   Agent 001: 15 + 25 =", calc_agent1.add(15, 25))
    print("   Agent 002: 6 * 7 =", calc_agent2.multiply(6, 7))

    # Expression evaluation
    print("\n4. Expression evaluation...")
    result = calc_agent1.calculate_expression("(10 + 5) * 3")
    print(f"   (10 + 5) * 3 = {result}")

    # Orchestrated workflow
    print("\n5. Orchestrated workflow...")
    numbers = [2, 3, 4, 5]
    workflow_result = orchestrator.execute_calculation_workflow(numbers)
    print(f"   Workflow result for {numbers}: {workflow_result}")

    # Show trace summary
    print("\n6. Trace summary:")
    all_events = tracer.get_events()
    print(f"   Total trace events: {len(all_events)}")

    # Group by agent
    agent_events = {}
    for event in all_events:
        if event.agent_id not in agent_events:
            agent_events[event.agent_id] = []
        agent_events[event.agent_id].append(event)

    for agent_id, events in agent_events.items():
        print(f"   {agent_id}: {len(events)} events")
        # Show last few events for each agent
        for event in events[-3:]:  # Last 3 events
            print(f"     [{event.level.value}] {event.event_type}: {event.message}")

    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)

    # Show log file contents
    if tracer.log_file and os.path.exists(tracer.log_file):
        print(f"\n7. Trace log file: {tracer.log_file}")
        print("   First 5 lines of log file:")
        with open(tracer.log_file, "r") as f:
            count = 0
            for line in f:
                line = line.strip()
                if not line or line == "[]":
                    continue
                if count >= 5:
                    print("   ...")
                    break
                # Parse and pretty print
                event = json.loads(line)
                print(f"   {event['timestamp']} [{event['level']}] {event['agent_id']}: {event['message']}")
                count += 1

    print(f"\nTotal events written to log file: {len(tracer.events)}")

    return tracer


if __name__ == "__main__":
    demonstrate_tracing()