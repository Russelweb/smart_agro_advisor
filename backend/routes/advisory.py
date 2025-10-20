"""
advisory.py
Combines disease detection and weather prediction to give actionable advice.
"""

from flask import Blueprint, request, jsonify
from backend.ml_models.disease_model import predict_disease
from backend.utils.weather_api import get_weather
from backend.utils.advisory_rules import get_disease_advice
from backend.utils.ai_advisor import generate_ai_advice
import os
from dotenv import load_dotenv

load_dotenv()


import requests


advisory_bp = Blueprint("advisory_bp", __name__, url_prefix="/api/advice")
API_KEY = os.getenv("OPENWEATHER_API_KEY")
@advisory_bp.route("/", methods=["POST"])
def give_advice():
    """
    POST request with an image + city name
    Returns disease prediction + weather info + expert advice.
    Each section (weather, disease, advice) is independent.
    """
    try:
        if 'image' not in request.files or 'city' not in request.form:
            return jsonify({"error": "Image and city are required"}), 400

        file = request.files['image']
        city = request.form['city']
        file.save("temp.jpg")

        # -----------------------------
        # 1️⃣ DISEASE PREDICTION
        # -----------------------------
        disease_result = {}
        try:
            disease_result = predict_disease("temp.jpg")
        except Exception as e:
            print("❌ Disease prediction failed:", e)
            disease_result = {"predicted_label": "Unknown", "confidence": 0.0, "error": str(e)}

        # -----------------------------
        # 2️⃣ WEATHER DATA
        # -----------------------------
        weather = {}
        try:
            res = requests.get(
                f"https://api.openweathermap.org/data/2.5/weather?q={city},CM&appid={API_KEY}&units=metric",
                timeout=10
            )
            if res.status_code == 200:
                weather = res.json()
            else:
                weather = {"error": f"Weather API returned {res.status_code}"}
        except Exception as e:
            print("🌩️ Error fetching weather:", e)
            weather = {"error": "Weather data unavailable due to connection issue"}

        # Safe weather summary extraction
        if weather and "weather" in weather:
            weather_summary = weather.get("weather", [{}])[0].get("main", "Unknown")
        else:
            weather_summary = "Unknown"


        advice_list = []
        try:
            if "predicted_label" in disease_result and disease_result["predicted_label"] != "Unknown":
                crop_type = disease_result["predicted_label"].split("_")[0]
                disease_name = disease_result["predicted_label"]

                # Use AI to generate dynamic advice
                ai_advice = generate_ai_advice(crop_type, disease_name, weather_summary)
                advice_list = [ai_advice]
            else:
                advice_list = ["Unable to generate advice due to missing disease information."]
        except Exception as e:
            print("⚠️ Advice generation failed:", e)
            advice_list = [f"Advice generation failed: {str(e)}"]

        # -----------------------------
        # 4️⃣ FINAL RESPONSE
        # -----------------------------
        crop_type = disease_result["predicted_label"].split("_")[0]
        response = {
            "status": "success",
            "crop": crop_type,
            "city": city,
            "weather": weather,
            "disease": disease_result,
            "advice": advice_list
        }

        return jsonify(response), 200

    except Exception as e:
        print("💥 Critical Error:", e)
        return jsonify({"error": str(e)}), 500
