import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import httpx
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamable_http_client
from strands.tools.mcp import MCPClient as StrandsMCPClient


def _build_local_server_params() -> StdioServerParameters:
    project_root = Path(__file__).resolve().parent.parent
    return StdioServerParameters(
        command="uv",
        args=["run", "mcp", "run", "src/mcp_server/server.py"],
        cwd=str(project_root),
    )


def _proxy_headers() -> dict[str, str]:
    token = os.getenv("MCP_PROXY_TOKEN")
    api_key = os.getenv("MCP_PROXY_API_KEY")

    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if api_key:
        headers["x-api-key"] = api_key
    return headers


def create_strands_mcp_client(server_url: str | None = None) -> StrandsMCPClient:
    resolved_server_url = server_url or os.getenv("MCP_PROXY_URL")

    if resolved_server_url:

        def transport() -> Any:
            http_client = httpx.AsyncClient(headers=_proxy_headers() or None)

            @asynccontextmanager
            async def proxy_context() -> Any:
                async with http_client:
                    async with streamable_http_client(
                        resolved_server_url,
                        http_client=http_client,
                    ) as streams:
                        yield streams

            return proxy_context()

        return StrandsMCPClient(transport)

    return StrandsMCPClient(lambda: stdio_client(_build_local_server_params()))


def call_tool_sync(
    tool_name: str,
    arguments: dict[str, Any],
    *,
    server_url: str | None = None,
) -> Any:
    with create_strands_mcp_client(server_url=server_url) as mcp_client:
        return mcp_client.call_tool_sync(
            tool_use_id=f"local-{tool_name}",
            name=tool_name,
            arguments=arguments,
        )


async def _run_local_stdio_client() -> None:
    print(call_tool_sync("add", {"a": 1888, "b": 2}))


async def _run_proxy_client(server_url: str) -> None:
    print(call_tool_sync("add", {"a": 1888, "b": 2}, server_url=server_url))


async def main() -> None:
    server_url = os.getenv("MCP_PROXY_URL")

    if not server_url:
        await _run_local_stdio_client()
        return

    try:
        await _run_proxy_client(server_url)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            print("Proxy authentication failed (401). Set MCP_PROXY_TOKEN or MCP_PROXY_API_KEY.")
            return
        print(f"HTTP error from proxy: {exc.response.status_code} {exc.response.reason_phrase}")


if __name__ == "__main__":
    asyncio.run(main())
