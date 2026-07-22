"""Weather-related resource helpers for MCP."""

from src.mcp.tools.weather import FORECAST_URL, GEOCODING_URL, WEATHER_CODE_DESCRIPTIONS


def weather_code_descriptions() -> str:
    """Return weather code descriptions in a compact, readable format."""
    lines = ["Open-Meteo Weather Code Descriptions:"]
    for code, description in sorted(WEATHER_CODE_DESCRIPTIONS.items()):
        lines.append(f"- {code}: {description}")
    return "\n".join(lines)


def weather_sources() -> str:
    """Return source endpoints and context for weather tooling."""
    return "\n".join([
        "Weather Tool Sources:",
        f"- Geocoding endpoint: {GEOCODING_URL}",
        f"- Forecast endpoint: {FORECAST_URL}",
        "- Provider: Open-Meteo APIs",
        "- Note: Weather code text follows Open-Meteo weather code mapping.",
    ])
