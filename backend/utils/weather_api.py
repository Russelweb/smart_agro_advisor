# backend/utils/weather_api.py
import requests
import os
from datetime import datetime


API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_weather(city="Bamenda", country="CM"):
    """Fetch current weather data for a given city."""
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": f"{city},{country}",
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        weather = {
            "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "city": city,
            "temp": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "condition": data["weather"][0]["main"]
        }
        return weather
    except Exception as e:
        print("Error fetching weather:", e)
        return None
BASE_URL = "https://api.openweathermap.org/data/2.5"
def get_forecast(city="Bamenda", country_code="CM", days=7):
    """
    Fetch 7-day weather forecast.
    Note: You must use the One Call API 3.0 for daily forecasts.
    """
    # First, get lat/lon
    geo_url = f"{BASE_URL}/weather?q={city},{country_code}&appid={API_KEY}"
    geo_data = requests.get(geo_url).json()
    lat, lon = geo_data["coord"]["lat"], geo_data["coord"]["lon"]

    # Call One Call API for daily forecast
    forecast_url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=hourly,minutely&appid={API_KEY}&units=metric"
    res = requests.get(forecast_url)

    if res.status_code != 200:
        return {"error": f"Failed to fetch forecast: {res.status_code}"}

    data = res.json()["daily"][:days]
    forecast = [
        {
            "date": day["dt"],
            "temp_day": day["temp"]["day"],
            "temp_night": day["temp"]["night"],
            "humidity": day["humidity"],
            "weather": day["weather"][0]["description"],
        }
        for day in data
    ]
    return forecast
