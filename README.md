# Agentic AI - AWS Bedrock Agents Project

This project uses **AWS Bedrock Agents** (Strands Agent) with Python, with **mise** for toolchain management and **uv** for dependencies.

## Setup

### Prerequisites
- AWS credentials configured
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
# Edit .env with your AWS configuration
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
│   ├── agents/           # Agent configurations and logic
│   ├── mcp/              # MCP server package
│   ├── tools/            # Tool definitions for agents
│   ├── utils/            # Utility functions
│   ├── strands_mcp.py    # Strands MCP bridge
│   ├── main.py           # CLI entry point
│   └── ui.py             # Streamlit entry point
├── tests/                # Test files
├── pyproject.toml        # Project configuration (uv)
└── README.md
```

## Usage

Run the Strands agent with MCP-backed local tools:
```bash
mise run agent
```

Run the Streamlit UI:
```bash
mise run ui
```

Run with a custom prompt:
```bash
mise exec -- uv run python -m src.main "Use the add tool to calculate 12 + 30"
```

Environment notes:
- Configure AWS credentials for Bedrock access.
- Defaults are `AWS_REGION=ap-southeast-2` and `BEDROCK_MODEL_ID=amazon.nova-micro-v1:0`.
- Amazon Bedrock does not provide a free always-on model tier here; usage is billed.
- Optionally override `BEDROCK_MODEL_ID` and `AWS_REGION`.
- By default the agent loads tools from `src/mcp/server.py` over MCP stdio.
- The Streamlit app also includes a direct MCP tool playground for local tool checks.
- Launch the CLI and UI through `mise run ...` or `mise exec -- uv run ...` so the project environment is used.
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

## AWS Bedrock Agent Documentation

- [AWS Bedrock Agents](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [Boto3 Bedrock Agents](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agent-runtime.html)

## License

MIT
