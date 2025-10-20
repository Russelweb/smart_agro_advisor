# tests/test_weather_logger.py
from backend.utils.weather_api import get_weather
from backend.utils.logger import log_weather_data
from backend.ml_models.weather_predictor import train_weather_model, predict_weather

# 1️⃣ Fetch live weather
weather = get_weather("Bamenda", "CM")
print("Fetched weather:", weather)

# 2️⃣ Log to CSV
log_weather_data(weather)
print("Weather logged successfully!")

# 3️⃣ Train Prophet model
train_weather_model()

# 4️⃣ Predict next 7 days
forecast = predict_weather(days=7)
print(forecast)
