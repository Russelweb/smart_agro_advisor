# backend/ml_models/weather_predictor.py
import pandas as pd
import os
import pickle
from prophet import Prophet
from datetime import timedelta

MODEL_PATH = "models/weather_model.pkl"
DATA_PATH = "data/weather_data.csv"

def train_weather_model():
    """Train Prophet model on logged weather data."""
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError("No weather data available for training!")

    df = pd.read_csv(DATA_PATH)
    df.rename(columns={"date": "ds", "temp": "y"}, inplace=True)

    model = Prophet(daily_seasonality=True)
    model.fit(df)

    os.makedirs("models", exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    print("✅ Weather model trained and saved.")

def predict_weather(days=7):
    """Predict temperature for the next given days."""
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)

    last_date = pd.read_csv(DATA_PATH)["date"].iloc[-1]
    future = model.make_future_dataframe(periods=days)
    forecast = model.predict(future)

    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(days)
