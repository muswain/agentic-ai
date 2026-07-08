import asyncio
import os
from pathlib import Path
from typing import Any

import httpx
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.client.streamable_http import streamable_http_client
from strands.tools.mcp import MCPClient as StrandsMCPClient


def _build_local_server_params() -> StdioServerParameters:
    project_root = Path(__file__).resolve().parent.parent
    return StdioServerParameters(
        command="uv",
        args=["run", "mcp", "run", "src/server.py"],
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


class MCPToolClient:
    def __init__(self, server_url: str | None = None) -> None:
        self.server_url = server_url or os.getenv("MCP_PROXY_URL")

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        if self.server_url:
            return await self._call_proxy_tool(tool_name, arguments)
        return await self._call_local_tool(tool_name, arguments)

    def call_tool_sync(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        return asyncio.run(self.call_tool(tool_name, arguments))

    async def _call_local_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        async with stdio_client(_build_local_server_params()) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as client:
                await client.initialize()
                result = await client.call_tool(tool_name, arguments)
                return result.structuredContent

    async def _call_proxy_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        async with httpx.AsyncClient(headers=_proxy_headers() or None) as http_client:
            async with streamable_http_client(self.server_url, http_client=http_client) as (
                read_stream,
                write_stream,
                _,
            ):
                async with ClientSession(read_stream, write_stream) as client:
                    await client.initialize()
                    result = await client.call_tool(tool_name, arguments)
                    return result.structuredContent


def create_strands_mcp_client() -> StrandsMCPClient:
    server_url = os.getenv("MCP_PROXY_URL")

    if server_url:
        def transport() -> Any:
            http_client = httpx.AsyncClient(headers=_proxy_headers() or None)

            async def proxy_context() -> Any:
                async with http_client:
                    async with streamable_http_client(server_url, http_client=http_client) as streams:
                        yield streams

            from contextlib import asynccontextmanager

            return asynccontextmanager(proxy_context)()

        return StrandsMCPClient(transport)

    return StrandsMCPClient(lambda: stdio_client(_build_local_server_params()))


async def _run_local_stdio_client() -> None:
    async with stdio_client(_build_local_server_params()) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as client:
            await client.initialize()
            result = await client.call_tool("add", {"a": 1888, "b": 2})
            print(result.structuredContent)  # {'result': 1890}


async def _run_proxy_client(server_url: str) -> None:
    async with httpx.AsyncClient(headers=_proxy_headers() or None) as http_client:
        async with streamable_http_client(server_url, http_client=http_client) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as client:
                await client.initialize()
                result = await client.call_tool("add", {"a": 1888, "b": 2})
                print(result.structuredContent)  # {'result': 1890}


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


asyncio.run(main())