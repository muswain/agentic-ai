"""Run a Strands agent backed by local MCP tools."""

import logging
import os
import sys

from dotenv import load_dotenv
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient

try:
    from .client import create_strands_mcp_client
except ImportError:
    from client import create_strands_mcp_client

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

DEFAULT_PROMPT = "Use the add tool to calculate 1888 + 2 and explain the result briefly."


def build_agent() -> tuple[Agent, MCPClient]:
    region = os.getenv("AWS_REGION", "ap-southeast-2")
    model_id = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-micro-v1:0")
    mcp_client = create_strands_mcp_client()

    mcp_client.start()
    tools = mcp_client.list_tools_sync()

    model = BedrockModel(region_name=region, model_id=model_id)
    agent = Agent(
        model=model,
        tools=tools,
        system_prompt=(
            "You are an AWS Strands agent that should use MCP tools when they are relevant. "
            "Prefer tool use for arithmetic requests."
        ),
    )
    return agent, mcp_client


def main() -> None:
    prompt = " ".join(sys.argv[1:]).strip() or DEFAULT_PROMPT
    agent, mcp_client = build_agent()

    try:
        result = agent(prompt)
        print(result)
    finally:
        mcp_client.stop()


if __name__ == "__main__":
    main()
