# backend/utils/logger.py
import pandas as pd
import os


def log_weather_data(weather, filepath="data/weather_data.csv"):
    """Append a single weather record to CSV."""
    if weather is None:
        return False

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    df = pd.DataFrame([weather])
    if not os.path.exists(filepath):
        df.to_csv(filepath, index=False)
    else:
        df.to_csv(filepath, mode="a", header=False, index=False)

    return True
