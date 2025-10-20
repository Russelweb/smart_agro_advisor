# backend/routes/weather.py

from flask import Blueprint, request, jsonify
from backend.utils.weather_api import get_weather
from backend.utils.logger import log_weather_data
from backend.ml_models.weather_predictor import predict_weather, train_weather_model
import os

weather_bp = Blueprint("weather", __name__)

@weather_bp.route("/api/weather/current", methods=["GET"])
def current_weather():
    """Fetch and return live weather info."""
    city = request.args.get("city", "Bamenda")
    country = request.args.get("country", "CM")

    weather = get_weather(city, country)
    if weather:
        log_weather_data(weather)
        return jsonify({
            "status": "success",
            "data": weather
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "Failed to fetch weather data."
        }), 500


@weather_bp.route("/api/weather/forecast", methods=["GET"])
def forecast_weather():
    """Predict temperature trend for the next few days."""
    days = int(request.args.get("days", 7))
    try:
        forecast = predict_weather(days)
        results = forecast.to_dict(orient="records")
        return jsonify({
            "status": "success",
            "days": days,
            "forecast": results
        }), 200
    except FileNotFoundError:
        # Model not yet trained → train first
        if os.path.exists("data/weather_data.csv"):
            train_weather_model()
            forecast = predict_weather(days)
            results = forecast.to_dict(orient="records")
            return jsonify({
                "status": "success",
                "days": days,
                "forecast": results
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "No weather data found. Fetch current weather first!"
            }), 400
