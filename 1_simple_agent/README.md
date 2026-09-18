# Simple Agent

A small Python example that demonstrates three ways to run an AI assistant with the
[OpenAI Agents SDK](https://openai.github.io/openai-agents-python/): synchronous,
asynchronous, and streamed execution.

The implementation is in [`src/1_simple_agent/chat_ui.py`](src/1_simple_agent/chat_ui.py).
It creates one reusable personal-assistant agent and exposes one function for each
execution style.

## Features

- Defines a `Personal Assistant Agent` with clear behavioral instructions.
- Encourages concise, accurate, friendly, and practical responses.
- Demonstrates synchronous execution with `Runner.run_sync`.
- Demonstrates asynchronous execution with `Runner.run`.
- Demonstrates streamed execution with `Runner.run_streamed`.
- Returns the assistant's final text from each example function.

## Requirements

- Python 3.12 or newer
- An API key configured for the provider used by the OpenAI Agents SDK
- The OpenAI Agents SDK package

The project currently declares no runtime dependencies in `pyproject.toml`, so install
the SDK explicitly before using this module:

```bash
uv add openai-agents
```

Alternatively, with `pip`:

```bash
python -m pip install openai-agents
```

Configure credentials according to the SDK documentation. For the default OpenAI
provider, this is commonly done with an environment variable:

### Windows PowerShell

```powershell
$env:OPENAI_API_KEY = "your-api-key"
```

### macOS/Linux

```bash
export OPENAI_API_KEY="your-api-key"
```

Do not commit API keys to the repository.

## Project layout

```text
.
├── pyproject.toml
├── README.md
└── src/
    └── 1_simple_agent/
        ├── __init__.py
        └── chat_ui.py
```

## Agent configuration

`chat_ui.py` creates a module-level agent:

```python
root_agent = Agent(
    name="Personal Assistant Agent",
    instructions="...",
)
```

The instructions define the assistant's expected behavior:

- Answer questions clearly and concisely.
- Provide helpful information and advice.
- Explain complex topics in simple terms.
- Offer practical solutions.
- Remain friendly, professional, positive, and supportive.
- Suggest useful follow-up steps when appropriate.

To customize the assistant, edit the `instructions` string or replace the agent's
name. The same `root_agent` is used by all three execution examples.

## Usage

Because the package directory contains an underscore-prefixed-style numeric name
(`1_simple_agent`), importing it with a regular `import 1_simple_agent` statement is
not valid Python syntax. Run the module by loading the file directly, or rename the
package to a conventional Python identifier if you plan to build a larger application.

For example, from a Python script in the repository root:

```python
import asyncio
import importlib.util
from pathlib import Path

module_path = Path("src/1_simple_agent/chat_ui.py")
spec = importlib.util.spec_from_file_location("chat_ui", module_path)
chat_ui = importlib.util.module_from_spec(spec)
spec.loader.exec_module(chat_ui)

# Synchronous execution
print(chat_ui.sync_example())

# Asynchronous execution
print(asyncio.run(chat_ui.async_example()))

# Streaming execution
print(asyncio.run(chat_ui.streaming_example()))
```

If the package is renamed to a valid import identifier, the examples can be imported
normally:

```python
from simple_agent.chat_ui import async_example, streaming_example, sync_example
```

## Execution methods

### Synchronous

```python
result = Runner.run_sync(root_agent, "Hello, how does sync execution work?")
return result.final_output
```

`sync_example()` blocks until the complete response is available and returns the
response text. Use it from ordinary, non-async Python code.

### Asynchronous

```python
result = await Runner.run(root_agent, "Hello, how does async execution work?")
return result.final_output
```

`async_example()` is suitable for applications that already use an asyncio event
loop, such as web servers or interactive applications. At the top level, call it
with `asyncio.run(async_example())`.

### Streaming

```python
response_text = ""
async for event in Runner.run_streamed(root_agent, "Tell me about streaming execution"):
    if hasattr(event, "content") and event.content:
        response_text += event.content
return response_text
```

`streaming_example()` consumes events as they arrive and accumulates content into a
single string before returning it. This demonstrates event-driven consumption, but
it does not print partial tokens immediately. A live chat UI could render each
non-empty `event.content` as it arrives instead of appending it only to a local
buffer.

## Running a quick check

From the repository root, run a Python command that imports the module and executes
one example after installing the SDK and configuring credentials. For example:

```bash
uv run python your_test_script.py
```

The current file is an example library module; it does not define a command-line
loop or a graphical chat window by itself.

## Extending the example

Possible next steps include:

1. Add a command-line input loop that repeatedly sends user messages to the agent.
2. Render streamed content immediately for a responsive chat experience.
3. Add conversation history so later turns include earlier context.
4. Add error handling for missing credentials, network failures, and failed runs.
5. Add tests using mocked runner results so tests do not require live API calls.
6. Add the SDK to `pyproject.toml` dependencies so a fresh environment installs it
   automatically.

## License

No license has been specified for this project yet.
