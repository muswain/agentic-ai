"""Primary agent orchestrator backed by MCP tools."""

import logging
import os
import sys
from typing import Any, TypedDict

from dotenv import load_dotenv
from strands import Agent
from strands.models import OllamaModel

from src.apps.backend.mcp.client import create_strands_mcp_client

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

DEFAULT_PROMPT = "Use the add tool to calculate 1888 + 2 and explain the result briefly."
DEFAULT_REGION = "local"
DEFAULT_MODEL_ID = "qwen3.5:4b"
DEFAULT_OLLAMA_HOST = "http://localhost:11434"
BASE_SYSTEM_PROMPT = (
    "You are a Strands orchestrator agent running against a local Ollama model and MCP tools. "
    "Use tools for information-gathering and computation when they improve accuracy."
)
AGENT_SKILLS = (
    "Use MCP tools whenever they can ground the answer better than guessing.",
    "Summarize tool outputs for the user instead of returning raw payloads.",
    "When tool data is incomplete, explain the limitation briefly and continue with the best answer possible.",
)


class ConversationMessage(TypedDict):
    role: str
    content: str


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
    resolved_model_id = model_id or os.getenv("OLLAMA_MODEL", DEFAULT_MODEL_ID)
    resolved_host = os.getenv("OLLAMA_HOST", DEFAULT_OLLAMA_HOST)
    model = OllamaModel(resolved_host, model_id=resolved_model_id)

    return Agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt or build_system_prompt(),
    )


def run_agent_prompt(
    prompt: str,
    *,
    region: str | None = None,
    model_id: str | None = None,
    system_prompt: str | None = None,
) -> str:
    with create_strands_mcp_client() as mcp_client:
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


def main() -> None:
    prompt = " ".join(sys.argv[1:]).strip() or DEFAULT_PROMPT
    print(run_chat_turn([{"role": "user", "content": prompt}]))


if __name__ == "__main__":
    main()
