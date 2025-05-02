# ml.py: Machine learning module for sleep quality prediction
# Author: Bright
# Date: April 03, 2025
# ml.py: Trains a RandomForestClassifier on sleep_health.csv to predict sleep quality

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

def train_model():
    """Train a RandomForestClassifier using sleep_health.csv data.

    Returns:
        tuple: Trained model and scaler, or (None, None) if training fails.
    """
    try:
        data = pd.read_csv("data/sleep_health_and_lifestyle_dataset.csv")
        # Select features for prediction
        X = data[["Sleep Duration", "Physical Activity Level", "Stress Level", "Heart Rate", "Daily Steps"]]
        y = data["Quality of Sleep"]
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_scaled, y)
        return model, scaler
    except FileNotFoundError:
        print("Warning: sleep_health.csv not found. Using default sleep quality prediction.")
        return None, None
    except Exception as e:
        print(f"Error training model: {e}")
        return None, None

def predict_sleep_quality(model, scaler, sleep_duration, activity_level, stress_level):
    """Predict sleep quality based on user input features.

    Args:
        model: Trained RandomForestClassifier model.
        scaler: StandardScaler for feature scaling.
        sleep_duration (float): Sleep duration in hours.
        activity_level (int): Physical activity in minutes.
        stress_level (int): Stress level (1-10).

    Returns:
        int: Predicted sleep quality (1-10).
    """
    if model is None or scaler is None:
        return 6  # Default quality if model unavailable
    # Use average values for unavailable features
    heart_rate = 70  # Average heart rate
    daily_steps = 8000  # Average daily steps
    input_data = [[sleep_duration, activity_level, stress_level, heart_rate, daily_steps]]
    input_scaled = scaler.transform(input_data)
    quality = model.predict(input_scaled)[0]
    return quality