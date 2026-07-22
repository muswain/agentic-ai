"""FastAPI app exposing a single chat endpoint for the Streamlit UI."""

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.agents.orchestrator import run_chat_turn

app = FastAPI(title="Agentic AI", description="A chat endpoint for the Agentic AI Streamlit UI.")


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


class ChatResponse(BaseModel):
    response: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    response = run_chat_turn(messages=[message.model_dump() for message in request.messages])
    return ChatResponse(response=response)


def main() -> None:
    import uvicorn

    uvicorn.run("src.apps.backend.app:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
