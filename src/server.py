from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Demo", instructions="A simple demo of the MCP framework.")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


@mcp.tool()
def minus(a: int, b: int) -> int:
    """Subtract two numbers."""
    return a - b


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
