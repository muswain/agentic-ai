# Agentic AI - AWS Bedrock Agents Project

This project uses **AWS Bedrock Agents** (Strands Agent) with Python and managed by **uv** package manager.

## Setup

### Prerequisites
- Python 3.14.6+
- AWS credentials configured
- [uv](https://github.com/astral-sh/uv) installed
- [mise](https://mise.jdx.dev/) installed

### Installation

1. Install dependencies:
```bash
uv sync
```

Or use mise to provision the local toolchain first:
```bash
mise install
mise exec -- uv sync
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your AWS configuration
```

3. Install development dependencies:
```bash
uv sync --extra dev
```

4. Install pre-commit hooks:
```bash
uv run pre-commit install
```

## Project Structure

```
agentic-ai/
├── src/
│   ├── agents/           # Agent configurations and logic
│   ├── tools/            # Tool definitions for agents
│   ├── utils/            # Utility functions
│   └── main.py           # Entry point
├── tests/                # Test files
├── pyproject.toml        # Project configuration (uv)
└── README.md
```

## Usage

Run the agent:
```bash
python -m src.main
```

Run the Strands agent with MCP-backed local tools:
```bash
uv run python src/main.py
```

Run with a custom prompt:
```bash
uv run python src/main.py "Use the add tool to calculate 12 + 30"
```

Environment notes:
- Configure AWS credentials for Bedrock access.
- Defaults are `AWS_REGION=ap-southeast-2` and `BEDROCK_MODEL_ID=amazon.nova-micro-v1:0`.
- Amazon Bedrock does not provide a free always-on model tier here; usage is billed.
- Optionally override `BEDROCK_MODEL_ID` and `AWS_REGION`.
- By default the agent loads tools from `src/server.py` over MCP stdio.

## Development

Using mise for the project environment:
```bash
mise install
mise exec -- uv sync --extra dev
```

Format code:
```bash
uv run black src/
```

Run linter:
```bash
uv run ruff check src/
```

Run Ruff auto-fixes:
```bash
uv run ruff check --fix src/
```

Run pre-commit manually:
```bash
uv run pre-commit run --all-files
```

Run tests:
```bash
uv run pytest
```

Type checking:
```bash
uv run mypy src/
```

## AWS Bedrock Agent Documentation

- [AWS Bedrock Agents](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [Boto3 Bedrock Agents](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-agent-runtime.html)

## License

MIT
