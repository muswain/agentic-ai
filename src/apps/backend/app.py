"""FastAPI app exposing a single chat endpoint for the Streamlit UI."""

from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.agents.orchestrator import ConversationMessage, run_chat_turn
from src.mcp.server import mcp

mcp_app = mcp.streamable_http_app()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Run MCP session manager lifecycle in the same backend process.
    async with mcp.session_manager.run():
        yield


app = FastAPI(
    title="Agentic AI",
    description="FastAPI backend with integrated MCP endpoint.",
    lifespan=lifespan,
)
app.mount("/", mcp_app)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


class ChatResponse(BaseModel):
    response: str


@app.get("/api/health")
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    messages: list[ConversationMessage] = [
        {"role": message.role, "content": message.content} for message in request.messages
    ]
    response = run_chat_turn(messages=messages)
    return ChatResponse(response=response)


def main() -> None:
    import uvicorn

    uvicorn.run("src.apps.backend.app:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
