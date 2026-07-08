"""Streamlit UI for the Strands + MCP demo."""

from __future__ import annotations

import json
import os
from typing import Any

import streamlit as st

from src.main import DEFAULT_MODEL_ID, DEFAULT_PROMPT, DEFAULT_REGION, run_agent_prompt
from src.strands_mcp import call_tool_sync


def _extract_mcp_payload(result: object) -> Any:
    if not isinstance(result, dict):
        return result

    structured_content = result.get("structuredContent")
    if structured_content is not None:
        return structured_content

    content = result.get("content")
    if isinstance(content, list) and len(content) == 1:
        item = content[0]
        if isinstance(item, dict) and isinstance(item.get("text"), str):
            try:
                return json.loads(item["text"])
            except json.JSONDecodeError:
                return item["text"]

    return content if content is not None else result


def _render_key_value_block(data: dict[str, Any]) -> None:
    rows = []
    for key, value in data.items():
        if isinstance(value, (dict, list)):
            continue
        rows.append({"Field": key.replace("_", " ").title(), "Value": value})

    if rows:
        st.table(rows)


def _render_geocode_payload(payload: dict[str, Any]) -> bool:
    matches = payload.get("matches")
    selected = payload.get("selected")

    if not isinstance(matches, list) or not isinstance(selected, dict):
        return False

    st.success(
        f"Best match: {selected.get('name', 'Unknown')} ({selected.get('country', 'Unknown')})"
    )

    summary_cols = st.columns(4)
    summary_cols[0].metric("Latitude", selected.get("latitude", "-"))
    summary_cols[1].metric("Longitude", selected.get("longitude", "-"))
    summary_cols[2].metric("Region", selected.get("admin1", "-"))
    summary_cols[3].metric("Timezone", selected.get("timezone", "-"))

    st.caption(f"Query: {payload.get('query', '')}")
    st.subheader("Candidate Matches")
    st.dataframe(matches, use_container_width=True, hide_index=True)
    return True


def _render_weather_payload(payload: dict[str, Any]) -> bool:
    current = payload.get("current")
    location = payload.get("location")

    if not isinstance(current, dict):
        return False

    if isinstance(location, dict):
        location_name = location.get("name") or "Selected location"
        detail_parts = [location.get("country"), location.get("admin1")]
        location_detail = ", ".join(part for part in detail_parts if part)
        st.success(location_name if not location_detail else f"{location_name}, {location_detail}")

    metric_cols = st.columns(4)
    metric_cols[0].metric("Temperature", f"{current.get('temperature_c', '-')} C")
    metric_cols[1].metric("Wind Speed", f"{current.get('wind_speed_kph', '-')} km/h")
    metric_cols[2].metric("Wind Direction", f"{current.get('wind_direction_degrees', '-')} deg")
    metric_cols[3].metric("Weather", current.get("description", current.get("weather_code", "-")))

    extras = {
        "Observed At": current.get("time"),
        "Is Day": current.get("is_day"),
        "Weather Code": current.get("weather_code"),
    }
    _render_key_value_block(extras)
    return True


def render_mcp_result(result: object) -> None:
    payload = _extract_mcp_payload(result)

    if isinstance(payload, dict):
        if _render_geocode_payload(payload):
            return
        if _render_weather_payload(payload):
            return

        _render_key_value_block(payload)
        remaining_nested_values = {
            key: value for key, value in payload.items() if isinstance(value, (dict, list))
        }
        if remaining_nested_values:
            st.json(remaining_nested_values)
        return

    if isinstance(payload, list):
        st.dataframe(payload, use_container_width=True, hide_index=True)
        return

    st.write(payload)


def render_tool_playground() -> None:
    st.subheader("MCP Tool Playground")
    left_col, right_col = st.columns(2)

    with left_col:
        add_a = st.number_input("Add: a", value=12, step=1)
        add_b = st.number_input("Add: b", value=30, step=1)
        if st.button("Run add", use_container_width=True):
            result = call_tool_sync(
                "add",
                {"a": int(add_a), "b": int(add_b)},
                server_url=os.getenv("MCP_PROXY_URL"),
            )
            render_mcp_result(result)

    with right_col:
        minus_a = st.number_input("Minus: a", value=50, step=1)
        minus_b = st.number_input("Minus: b", value=8, step=1)
        if st.button("Run minus", use_container_width=True):
            result = call_tool_sync(
                "minus",
                {"a": int(minus_a), "b": int(minus_b)},
                server_url=os.getenv("MCP_PROXY_URL"),
            )
            render_mcp_result(result)


def render_public_api_tools() -> None:
    st.subheader("Weather And Geocoding")

    geocode_col, place_weather_col, coord_weather_col = st.columns(3)

    with geocode_col:
        st.markdown("**Geocode Place**")
        geocode_query = st.text_input("Place name", value="Sydney", key="geocode_query")
        if st.button("Geocode", use_container_width=True):
            result = call_tool_sync(
                "geocode_place_tool",
                {"name": geocode_query},
                server_url=os.getenv("MCP_PROXY_URL"),
            )
            render_mcp_result(result)

    with place_weather_col:
        st.markdown("**Weather By Place**")
        weather_place = st.text_input("Weather place", value="Sydney", key="weather_place")
        if st.button("Get weather for place", use_container_width=True):
            result = call_tool_sync(
                "get_weather_for_place_tool",
                {"name": weather_place},
                server_url=os.getenv("MCP_PROXY_URL"),
            )
            render_mcp_result(result)

    with coord_weather_col:
        st.markdown("**Weather By Coordinates**")
        latitude = st.number_input(
            "Latitude",
            value=-33.86785,
            format="%.5f",
            key="weather_latitude",
        )
        longitude = st.number_input(
            "Longitude",
            value=151.20732,
            format="%.5f",
            key="weather_longitude",
        )
        if st.button("Get weather for coordinates", use_container_width=True):
            result = call_tool_sync(
                "get_weather_tool",
                {"latitude": float(latitude), "longitude": float(longitude)},
                server_url=os.getenv("MCP_PROXY_URL"),
            )
            render_mcp_result(result)


def main() -> None:
    st.set_page_config(page_title="Agentic AI", page_icon="AI", layout="wide")

    st.title("Agentic AI")
    st.caption("Strands agent with MCP-backed tools running locally or through an MCP proxy.")

    with st.sidebar:
        st.header("Runtime")
        region = st.text_input("AWS Region", value=os.getenv("AWS_REGION", DEFAULT_REGION))
        model_id = st.text_input(
            "Bedrock Model ID",
            value=os.getenv("BEDROCK_MODEL_ID", DEFAULT_MODEL_ID),
        )
        st.markdown(
            "Default model is the lower-cost `amazon.nova-micro-v1:0`. "
            "Set `MCP_PROXY_URL` only if you want to route tool calls through a proxy."
        )

    prompt = st.text_area("Prompt", value=DEFAULT_PROMPT, height=140)
    run_agent = st.button("Run agent", type="primary", use_container_width=True)

    if run_agent:
        with st.spinner("Running Strands agent..."):
            try:
                result = run_agent_prompt(prompt, region=region, model_id=model_id)
            except Exception as exc:
                st.error(str(exc))
            else:
                st.subheader("Agent Response")
                st.write(result)

    st.divider()
    render_tool_playground()
    st.divider()
    render_public_api_tools()


if __name__ == "__main__":
    main()
