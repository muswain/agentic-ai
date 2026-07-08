"""Run a Strands agent backed by local MCP tools."""

import logging
import os
import sys
from typing import Any

from dotenv import load_dotenv
from strands import Agent
from strands.models import BedrockModel

from src.strands_mcp import create_strands_mcp_client

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

DEFAULT_PROMPT = "Use the add tool to calculate 1888 + 2 and explain the result briefly."
DEFAULT_REGION = "ap-southeast-2"
DEFAULT_MODEL_ID = "amazon.nova-micro-v1:0"


def build_agent(
    tools: list[Any],
    *,
    region: str | None = None,
    model_id: str | None = None,
) -> Agent:
    resolved_region = region or os.getenv("AWS_REGION", DEFAULT_REGION)
    resolved_model_id = model_id or os.getenv("BEDROCK_MODEL_ID", DEFAULT_MODEL_ID)

    model = BedrockModel(region_name=resolved_region, model_id=resolved_model_id)
    return Agent(
        model=model,
        tools=tools,
        system_prompt=(
            "You are an AWS Strands agent that should use MCP tools when they are relevant. "
            "Prefer tool use for arithmetic requests."
        ),
    )


def run_agent_prompt(
    prompt: str,
    *,
    region: str | None = None,
    model_id: str | None = None,
) -> str:
    with create_strands_mcp_client() as mcp_client:
        tools = mcp_client.list_tools_sync()
        agent = build_agent(tools, region=region, model_id=model_id)
        result = agent(prompt)
        return str(result)


def main() -> None:
    prompt = " ".join(sys.argv[1:]).strip() or DEFAULT_PROMPT
    print(run_agent_prompt(prompt))


if __name__ == "__main__":
    main()
