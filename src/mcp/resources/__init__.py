"""Resource definitions exposed by the MCP server."""

from src.mcp.resources.greeting import greeting
from src.mcp.resources.weather import weather_code_descriptions, weather_sources

__all__ = ["greeting", "weather_code_descriptions", "weather_sources"]
