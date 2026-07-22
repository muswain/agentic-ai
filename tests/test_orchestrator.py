from src.agents.orchestrator import build_conversation_prompt, build_system_prompt


def test_build_conversation_prompt_appends_agent_instruction() -> None:
    prompt = build_conversation_prompt([
        {"role": "assistant", "content": "Hello"},
        {"role": "user", "content": "What is the weather in Sydney?"},
    ])

    assert "Assistant: Hello" in prompt
    assert "User: What is the weather in Sydney?" in prompt
    assert prompt.endswith("Assistant: Respond to the latest user request using tools when needed.")


def test_build_system_prompt_includes_agent_skills() -> None:
    prompt = build_system_prompt()

    assert "Follow these operating skills:" in prompt
    assert "Summarize tool outputs for the user" in prompt
