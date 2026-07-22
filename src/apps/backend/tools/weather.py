from typing import Any

import httpx

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT_SECONDS = 10.0

WEATHER_CODE_DESCRIPTIONS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def _client() -> httpx.Client:
    return httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS)


def _weather_description(code: int | None) -> str:
    if code is None:
        return "Unknown"
    return WEATHER_CODE_DESCRIPTIONS.get(code, "Unknown")


def geocode_place(name: str, *, count: int = 5) -> dict[str, Any]:
    """Resolve a place name into latitude and longitude using Open-Meteo geocoding."""
    with _client() as client:
        response = client.get(
            GEOCODING_URL,
            params={
                "name": name,
                "count": count,
                "language": "en",
                "format": "json",
            },
        )
        response.raise_for_status()
        payload = response.json()

    results = payload.get("results") or []
    if not results:
        return {"query": name, "matches": [], "selected": None}

    matches = [
        {
            "name": item.get("name"),
            "country": item.get("country"),
            "admin1": item.get("admin1"),
            "latitude": item.get("latitude"),
            "longitude": item.get("longitude"),
            "timezone": item.get("timezone"),
        }
        for item in results
    ]

    return {"query": name, "matches": matches, "selected": matches[0]}


def get_weather(latitude: float, longitude: float) -> dict[str, Any]:
    """Get current weather for a latitude and longitude using Open-Meteo."""
    with _client() as client:
        response = client.get(
            FORECAST_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": [
                    "temperature_2m",
                    "apparent_temperature",
                    "relative_humidity_2m",
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "weather_code",
                    "is_day",
                ],
                "timezone": "auto",
                "forecast_days": 1,
            },
        )
        response.raise_for_status()
        payload = response.json()

    current = payload.get("current", {})
    current_units = payload.get("current_units", {})
    weather_code = current.get("weather_code")

    return {
        "location": {
            "latitude": payload.get("latitude"),
            "longitude": payload.get("longitude"),
            "timezone": payload.get("timezone"),
            "timezone_abbreviation": payload.get("timezone_abbreviation"),
        },
        "current": {
            "time": current.get("time"),
            "temperature": current.get("temperature_2m"),
            "temperature_unit": current_units.get("temperature_2m"),
            "apparent_temperature": current.get("apparent_temperature"),
            "humidity": current.get("relative_humidity_2m"),
            "humidity_unit": current_units.get("relative_humidity_2m"),
            "wind_speed": current.get("wind_speed_10m"),
            "wind_speed_unit": current_units.get("wind_speed_10m"),
            "wind_direction": current.get("wind_direction_10m"),
            "weather_code": weather_code,
            "weather_description": _weather_description(weather_code),
            "is_day": current.get("is_day"),
        },
    }


def get_weather_for_place(name: str) -> dict[str, Any]:
    """Geocode a place name and return current weather for the best match."""
    geocode_result = geocode_place(name, count=1)
    selected = geocode_result.get("selected")
    if not selected:
        return {"query": name, "location": None, "weather": None}

    weather = get_weather(
        latitude=float(selected["latitude"]),
        longitude=float(selected["longitude"]),
    )
    return {"query": name, "location": selected, "weather": weather}
