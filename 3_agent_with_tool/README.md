# Date Difference Agent

A small OpenAI Agents SDK project with a deterministic date-difference tool and a Streamlit UI.

## Features

- Accepts two dates through `st.date_input`.
- Calculates complete calendar years, remaining days, and total elapsed days.
- Normalizes reversed inputs automatically.
- Uses February 28 as the anniversary for a February 29 date in a non-leap year.
- Exposes the same calculation as `date_difference_tool` for the agent.

## Setup

From this directory, sync the project with `uv`:

```powershell
uv sync
```

The Streamlit calculator works locally without an API key. To run the OpenAI Agents SDK agent, configure the credentials required by your installed SDK, typically `OPENAI_API_KEY`.

## Run the UI

```powershell
uv run streamlit run src/3_agent_with_tool/streamlit_app.py
```

Then open the local URL shown by Streamlit and choose Date 1 and Date 2.

## Date semantics

The result reports calendar anniversaries rather than treating every year as exactly 365 days. For example, `2020-01-01` to `2021-01-02` is **1 year and 1 day**, with **367 total days**.

## Tests

```powershell
uv run pytest tests
```
