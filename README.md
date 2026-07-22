# Agentic AI

This project uses **Strands Agents** with a local **Ollama** model, with **mise** for toolchain management and **uv** for dependencies.

## Setup

### Prerequisites
- Ollama running locally with `qwen3.5:4b` available
- [mise](https://mise.jdx.dev/) installed

`mise` will provision the pinned Python and `uv` versions for this repo.

### Installation

1. Install the toolchain:
```bash
mise install
```

2. Install dependencies:
```bash
mise run sync
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your local/runtime configuration
```

4. Install development dependencies:
```bash
mise run sync-dev
```

5. Install pre-commit hooks:
```bash
mise exec -- uv run pre-commit install
```

## Project Structure

```
agentic-ai/
├── src/
│   ├── agents/               # Agent orchestration and agent-owned utilities
│   │   └── orchestrator.py   # Primary agent orchestrator
│   ├── apps/
│   │   ├── backend/          # FastAPI app, MCP server/client, and backend tools
│   │   │   ├── app.py
│   │   │   ├── mcp/
│   │   │   └── tools/
│   │   └── frontend/         # Streamlit chat UI
│   │       └── chat_ui.py
│   └── utils/                # Shared utility functions
├── tests/                # Test files
├── pyproject.toml        # Project configuration (uv)
└── README.md
```

## Usage

Run the agent orchestrator with MCP-backed local tools:
```bash
mise run agent
```

Run the FastAPI backend:
```bash
mise run api
```

Run the Streamlit chat UI:
```bash
mise run ui
```

Run with a custom prompt:
```bash
mise exec -- uv run python -m src.agents.orchestrator "Use the add tool to calculate 12 + 30"
```

Environment notes:
- Defaults are `OLLAMA_HOST=http://localhost:11434` and `OLLAMA_MODEL=qwen3.5:4b`.
- Optionally override `OLLAMA_HOST` and `OLLAMA_MODEL`.
- By default the agent loads tools from `src/apps/backend/mcp/server.py` over MCP stdio.
- The Streamlit chat calls a single FastAPI endpoint, which initializes the orchestrator and lets the agent decide when to use MCP tools.
- The request flow is: Streamlit chat UI -> FastAPI -> agent -> MCP tools -> response.
- Launch the CLI and UI through `mise run ...` or `mise exec -- uv run ...` so the project environment is used.
- Start the backend before using the UI, or the chat app will not be able to reach the API endpoint.
- Do not run plain `python` or plain `streamlit` from outside the project environment, or imports like `mcp.client` may fail.
- `.python-version` remains only as compatibility metadata for tools like pyenv; `mise` is the intended workflow.

## Development

Recommended development workflow:
```bash
mise install
mise run sync-dev
```

Format code:
```bash
mise run format
```

Run linter:
```bash
mise run lint
```

Run pre-commit manually:
```bash
mise run precommit
```

Run tests:
```bash
mise run test
```

Type checking:
```bash
mise exec -- uv run mypy src/
```

## Strands And Ollama References

- [Strands Agents Documentation](https://strandsagents.com/latest/)
- [Strands Models API](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/models/overview/)
- [Ollama Documentation](https://ollama.com/docs)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)

## License

MIT
