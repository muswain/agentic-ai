"""Primary agent orchestrator backed by MCP tools."""

import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, TypedDict
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv
from mcp.client.streamable_http import streamable_http_client
from strands import Agent
from strands.models import OllamaModel
from strands.tools.mcp import MCPClient as StrandsMCPClient

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

ENV_REGION = "AGENT_REGION"
ENV_MODEL_ID = "OLLAMA_MODEL"
ENV_OLLAMA_HOST = "OLLAMA_HOST"
ENV_MCP_SERVER_URL = "MCP_SERVER_URL"
BASE_SYSTEM_PROMPT = (
    "You are a Strands orchestrator agent running against a local Ollama model and MCP tools. "
    "Use tools for information-gathering and computation when they improve accuracy."
)
AGENT_SKILLS = (
    "Use MCP tools whenever they can ground the answer better than guessing.",
    (
        "Before using weather tools, read weather://sources and weather://codes to "
        "understand provenance and weather-code meanings."
    ),
    "Summarize tool outputs for the user instead of returning raw payloads.",
    ("When tool data is incomplete, explain the limitation briefly and continue with the best answer possible."),
)


class ConversationMessage(TypedDict):
    role: str
    content: str


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def build_system_prompt() -> str:
    skills = "\n".join(f"- {skill}" for skill in AGENT_SKILLS)
    return f"{BASE_SYSTEM_PROMPT}\n\nFollow these operating skills:\n{skills}"


def build_conversation_prompt(messages: list[ConversationMessage]) -> str:
    transcript = []
    for message in messages:
        role = message["role"].capitalize()
        transcript.append(f"{role}: {message['content']}")
    transcript.append("Assistant: Respond to the latest user request using tools when needed.")
    return "\n\n".join(transcript)


def build_agent(
    tools: list[Any],
    *,
    region: str | None = None,
    model_id: str | None = None,
    system_prompt: str | None = None,
) -> Agent:
    resolved_model_id = model_id or _get_required_env(ENV_MODEL_ID)
    resolved_host = _get_required_env(ENV_OLLAMA_HOST)
    model = OllamaModel(resolved_host, model_id=resolved_model_id)

    return Agent(
        name="Strands Orchestrator Agent",
        description="An agent that orchestrates tool usage for user requests using MCP tools.",
        model=model,
        tools=tools,
        system_prompt=system_prompt or build_system_prompt(),
    )


def create_mcp_client(server_url: str | None = None) -> StrandsMCPClient:
    resolved_server_url = server_url or _get_required_env(ENV_MCP_SERVER_URL)
    parsed = urlparse(resolved_server_url)
    logger.info(
        "Connecting to MCP server at %s (host=%s, port=%s)",
        resolved_server_url,
        parsed.hostname or "unknown",
        parsed.port or "default",
    )

    def transport() -> Any:
        http_client = httpx.AsyncClient()

        @asynccontextmanager
        async def proxy_context() -> AsyncIterator[Any]:
            async with http_client:
                async with streamable_http_client(
                    resolved_server_url,
                    http_client=http_client,
                ) as streams:
                    yield streams

        return proxy_context()

    return StrandsMCPClient(transport)


def run_agent_prompt(
    prompt: str,
    *,
    region: str | None = None,
    model_id: str | None = None,
    system_prompt: str | None = None,
) -> str:
    with create_mcp_client() as mcp_client:
        tools = mcp_client.list_tools_sync()
        agent = build_agent(
            tools,
            region=region,
            model_id=model_id,
            system_prompt=system_prompt,
        )
        result = agent(prompt)
        return str(result)


def run_chat_turn(
    messages: list[ConversationMessage],
    *,
    region: str | None = None,
    model_id: str | None = None,
) -> str:
    return run_agent_prompt(
        build_conversation_prompt(messages),
        region=region,
        model_id=model_id,
    )
