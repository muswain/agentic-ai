"""Streamlit chat UI that forwards chat turns to the FastAPI backend."""

from __future__ import annotations

import os

import httpx
import streamlit as st

API_URL = os.getenv("AGENT_API_URL", "http://127.0.0.1:8000/chat")
ASSISTANT_GREETING = "Ask a question and I will route it through the agent and its tools."


def _ensure_session_state() -> None:
    st.session_state.setdefault(
        "messages",
        [{"role": "assistant", "content": ASSISTANT_GREETING}],
    )


def _render_messages() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])


def _call_chat_api() -> str:
    response = httpx.post(
        API_URL,
        json={"messages": st.session_state.messages},
        timeout=90.0,
    )
    response.raise_for_status()
    return response.json()["response"]


def _run_turn(user_message: str) -> None:
    st.session_state.messages.append({"role": "user", "content": user_message})
    with st.chat_message("user"):
        st.write(user_message)

    with st.chat_message("assistant"):
        with st.spinner("Agent is thinking..."):
            try:
                reply = _call_chat_api()
            except Exception as exc:
                reply = f"Error: {exc}"
            st.write(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})


def main() -> None:
    st.set_page_config(page_title="Agentic AI", page_icon="AI", layout="wide")
    _ensure_session_state()

    st.title("Agentic AI")
    st.caption("Streamlit chat UI backed by a single FastAPI chat endpoint.")

    with st.sidebar:
        st.header("Backend")
        st.write(f"API endpoint: {API_URL}")
        if st.button("Clear chat", use_container_width=True):
            st.session_state.messages = [{"role": "assistant", "content": ASSISTANT_GREETING}]
            st.rerun()

    _render_messages()

    user_message = st.chat_input("Ask the agent anything")
    if user_message:
        _run_turn(user_message)


if __name__ == "__main__":
    main()
