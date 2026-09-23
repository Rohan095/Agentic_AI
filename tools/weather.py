import requests
from agent.tool import Tool

def get_weather(city: str):
    try:
        # Step 1: Convert city name → latitude/longitude
        geo_response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json"
            },
            timeout=5
        )

        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if "results" not in geo_data or not geo_data["results"]:
            raise ValueError(f"Location not found: {city}")

        location = geo_data["results"][0]

        latitude = location["latitude"]
        longitude = location["longitude"]

        # Step 2: Get current weather
        weather_response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m ,wind_speed_10m",
                "temperature_unit": "celsius"

            },
            timeout=5
        )

        weather_response.raise_for_status()
        weather_data = weather_response.json()

        current = weather_data["current"]

        return {
            "city": location["name"],
            "temperature": current["temperature_2m"],
            "temperature_unit": "celsius",
            "wind_speed": current["wind_speed_10m"]
        }

    except requests.exceptions.Timeout:
        raise RuntimeError("Weather service timed out.")

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Weather service request failed: {str(e)}")

    except (KeyError, TypeError):
        raise RuntimeError("Weather service returned an unexpected response.")

weather_tool = Tool(
    name="weather",
    description="Get the current weather for a given city.",
    parameters={
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "Name of the city to get the weather for"
            }
        },
        "required": ["city"]
    },
    function=get_weather
)