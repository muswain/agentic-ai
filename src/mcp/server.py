from mcp.server.fastmcp import FastMCP

from src.mcp.resources import greeting, weather_code_descriptions, weather_sources
from src.mcp.tools import geocode_place, get_weather, get_weather_for_place

mcp = FastMCP(
    "MCP Server",
    port=9000,
    log_level="INFO",
    instructions=(
        "MCP Server instructions. This server provides tools for geocoding and "
        "weather information. Read relevant resources before first tool use when "
        "they provide constraints, provenance, or code mappings."
    ),
)


@mcp.tool(
    name="geocode_place",
    description="Resolve a place name into likely latitude/longitude matches.",
)
def geocode_place_tool(name: str) -> dict:
    """Convert a place name into likely latitude/longitude matches."""
    return geocode_place(name)


@mcp.tool(
    name="get_weather",
    description="Get current weather for a latitude and longitude.",
)
def get_weather_tool(latitude: float, longitude: float) -> dict:
    """Get current weather for a latitude and longitude."""
    return get_weather(latitude, longitude)


@mcp.tool(
    name="get_weather_for_place",
    description="Get current weather for a place name without coordinates.",
)
def get_weather_for_place_tool(name: str) -> dict:
    """Get current weather for a place name without needing coordinates first."""
    return get_weather_for_place(name)


@mcp.resource(
    "greeting://{name}",
    title="Greeting Resource",
    description="A resource that greets someone by name.",
)
def greeting_resource(name: str) -> str:
    """Greet someone by name."""
    return greeting(name)


@mcp.resource(
    "weather://codes",
    title="Weather Code Descriptions",
    description="Descriptions for Open-Meteo weather codes used by weather tools.",
)
def weather_codes_resource() -> str:
    """Expose weather code descriptions for tool interpretation."""
    return weather_code_descriptions()


@mcp.resource(
    "weather://sources",
    title="Weather Data Sources",
    description="Source endpoints and provider details for weather tools.",
)
def weather_sources_resource() -> str:
    """Expose source endpoints and provider metadata."""
    return weather_sources()


@mcp.prompt("greet", title="Greet", description="Greet someone by name.")
def greet(name: str) -> str:
    """Greet someone by name."""
    return greeting(name)
