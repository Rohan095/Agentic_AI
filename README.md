# Agentic

A small tool-using AI agent built with Python and the Google Gemini API. The agent evaluates a user request, chooses between a direct tool call, a multi-step plan, or a final response, and keeps tool observations in an in-memory state object.

## Features

- Gemini-powered action selection with JSON responses
- Direct tool execution for simple requests
- Planner support for requests that require multiple steps
- Tool registry for registering and exposing tools to the model
- In-memory state for plans, observations, iterations, and status
- Built-in calculator and current-weather tools
- Maximum of 10 agent iterations per run

## Project Structure

```text
.
├── main.py                 # Application entry point and agent loop
├── agent/
│   ├── planner.py          # Gemini-based multi-step plan creation
│   ├── registry.py         # Tool registration and definitions
│   ├── runtime.py          # Tool lookup, validation, and execution
│   ├── state.py            # Request, plan, observation, and status state
│   └── tool.py             # Tool data structure
└── tools/
    ├── calculator.py       # Restricted arithmetic expression tool
    └── weather.py          # Open-Meteo geocoding and current weather tool
```

## Requirements

- Python 3.10 or newer
- A Google Gemini API key
- Internet access for Gemini and Open-Meteo requests

Install the dependencies in an activated virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install google-genai python-dotenv requests
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

## Configuration

Create a local `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

The application loads this value with `python-dotenv`. Keep the file private; it is excluded by `.gitignore`.

## Run

```bash
python main.py
```

The current example request is defined directly in `main.py` and asks the agent to compare temperatures in New York and Los Angeles and calculate the difference. Edit `AgentState(...)` in that file to try another request.

The program prints the model's decisions, created plans, tool observations, and final answer. A run stops when it completes, encounters an error, or reaches the ten-iteration limit.

## How It Works

1. `main.py` loads the API key and creates a Gemini client.
2. The calculator and weather tools are registered with `ToolRegistry`.
3. `AgentState` stores the request and the evolving execution context.
4. Gemini selects one JSON action: `tool_call`, `plan`, or `final`.
5. `AgentRuntime` validates required arguments and executes selected tools.
6. Tool results are added to the state and included in the next model prompt.
7. The loop ends with a final answer or an error status.

## Built-in Tools

### Calculator

Evaluates arithmetic expressions containing numbers, whitespace, parentheses, and the operators `+`, `-`, `*`, and `/`.

Example expression:

```text
(24 * 3) / 2
```

### Weather

Looks up a city through the Open-Meteo geocoding API and returns its current temperature and wind speed in metric units. It does not require a separate weather API key.

## Adding a Tool

1. Create a function in `tools/`.
2. Wrap it in a `Tool` instance with a name, description, JSON-style parameter schema, and function.
3. Import the tool in `main.py`.
4. Register it with `registry.register(...)`.

Once registered, its definition is included in the model prompt and it can be selected by name.

## Current Limitations

- The user request is hard-coded in `main.py`; there is no command-line or interactive input yet.
- The planner creates a plan, but the runtime relies on Gemini to choose each subsequent tool call rather than executing plan steps through a dedicated plan executor.
- Dependency versions are not pinned in a requirements file.
- Calculator failures raised by the tool function are not converted into structured runtime errors.
- The model name is currently hard-coded as `gemini-3.5-flash-lite`.

## Git and Local Files

The repository ignores local secrets and development artifacts, including:

- `.env` and other environment files
- `.venv/` and `venv/`
- Python bytecode and `__pycache__/`
- macOS `.DS_Store` files
- `.github/agents/`, which contains local VS Code custom agents

These files should remain local and should not be committed or pushed.
