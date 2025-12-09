import requests
from datetime import datetime
from config import WESTMEATH_LAT, WESTMEATH_LON

def fetch_weather_data():
    """Fetch real-time weather from Open-Meteo API"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": WESTMEATH_LAT,
        "longitude": WESTMEATH_LON,
        "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,wind_direction_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "Europe/Dublin"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return {
            "current": {
                "temperature": data["current"]["temperature_2m"],
                "humidity": data["current"]["relative_humidity_2m"],
                "precipitation": data["current"]["precipitation"],
                "weather_code": data["current"]["weather_code"],
                "wind_speed": data["current"]["wind_speed_10m"],
                "wind_direction": data["current"]["wind_direction_10m"],
                "time": data["current"]["time"]
            },
            "forecast": [
                {
                    "date": data["daily"]["time"][i],
                    "weather_code": data["daily"]["weather_code"][i],
                    "temp_max": data["daily"]["temperature_2m_max"][i],
                    "temp_min": data["daily"]["temperature_2m_min"][i],
                    "precipitation": data["daily"]["precipitation_sum"][i]
                }
                for i in range(len(data["daily"]["time"]))
            ]
        }
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None

def get_weather_description(code: int) -> str:
    """Convert WMO weather code to description"""
    weather_codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
        55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow", 80: "Slight showers",
        81: "Moderate showers", 82: "Violent showers", 95: "Thunderstorm"
    }
    return weather_codes.get(code, "Unknown")

def get_weather_icon(code: int) -> str:
    """Get emoji for weather code"""
    if code in [0, 1]: return "☀️"
    if code in [2, 3]: return "⛅"
    if code in [45, 48]: return "🌫️"
    if code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: return "🌧️"
    if code in [71, 73, 75]: return "❄️"
    if code == 95: return "⛈️"
    return "🌤️"
