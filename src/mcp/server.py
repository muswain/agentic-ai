from mcp.server.fastmcp import FastMCP

from src.tools import geocode_place, get_weather, get_weather_for_place

mcp = FastMCP("Demo", instructions="A simple demo of the MCP framework.")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@mcp.tool()
def minus(a: int, b: int) -> int:
    """Subtract two numbers."""
    return a - b


@mcp.tool()
def geocode_place_tool(name: str) -> dict:
    """Convert a place name into likely latitude/longitude matches."""
    return geocode_place(name)


@mcp.tool()
def get_weather_tool(latitude: float, longitude: float) -> dict:
    """Get current weather for a latitude and longitude."""
    return get_weather(latitude, longitude)


@mcp.tool()
def get_weather_for_place_tool(name: str) -> dict:
    """Get current weather for a place name without needing coordinates first."""
    return get_weather_for_place(name)


@mcp.resource(
    "greeting://{name}",
    title="Greeting Resource",
    description="A resource that greets someone by name.",
)
def greeting(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"


@mcp.prompt("greet", title="Greet", description="Greet someone by name.")
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"
