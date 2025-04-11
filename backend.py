# backend.py: Handles sleep data processing, circadian rhythm calculation, and predictions
from datetime import datetime, timedelta
import numpy as np
from scipy.interpolate import interp1d
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

def calculate_sleep_debt(sleep_time, wake_time):
    # Calculate sleep debt against an 8-hour target
    sleep_dt = datetime.strptime(sleep_time, "%H:%M")
    wake_dt = datetime.strptime(wake_time, "%H:%M")
    if wake_dt < sleep_dt:  # Handle overnight sleep
        wake_dt += timedelta(days=1)
    duration = (wake_dt - sleep_dt).seconds / 3600
    return round(max(8 - duration, 0), 2)

def calculate_circadian_rhythm(sleep_time, wake_time):
    # Compute circadian rhythm details and energy curve
    sleep_dt = datetime.strptime(sleep_time, "%H:%M")
    wake_dt = datetime.strptime(wake_time, "%H:%M")
    if wake_dt < sleep_dt:
        wake_dt += timedelta(days=1)
    duration = (wake_dt - sleep_dt).seconds / 3600
    midpoint_dt = sleep_dt + timedelta(hours=duration / 2)
    midpoint = midpoint_dt.strftime("%H:%M")
    midpoint_hour = midpoint_dt.hour + midpoint_dt.minute / 60
    chronotype = "Early Bird" if midpoint_hour < 3.5 else "Intermediate" if midpoint_hour < 5 else "Night Owl"

    # Define key points for energy curve
    wake_hour = wake_dt.hour + wake_dt.minute / 60
    sleep_hour = sleep_dt.hour + sleep_dt.minute / 60 if sleep_dt > wake_dt else sleep_dt.hour + sleep_dt.minute / 60 + 24
    key_hours = [
        0.0, wake_hour, (wake_hour + 3) % 24, (wake_hour + 7) % 24,
        (wake_hour + 11) % 24, sleep_hour % 24, 24.0
    ]
    key_energy = [2, 2, 10, 3, 7, 2, 2]  # Energy levels at key times

    # Ensure unique, sorted points for interpolation
    unique_hours = sorted(set(key_hours))
    unique_energy = [key_energy[key_hours.index(h)] for h in unique_hours if h in key_hours]

    # Generate 100-point energy curve
    hours = np.linspace(0, 24, 100)
    f = interp1d(unique_hours, unique_energy, kind="cubic", bounds_error=False, fill_value=2)
    energy = np.clip(f(hours), 0, 10)

    return {
        "midpoint": midpoint,
        "chronotype": chronotype,
        "wake_time": wake_dt.strftime("%H:%M"),
        "morning_peak": (wake_dt + timedelta(hours=3)).strftime("%H:%M"),
        "dip_time": (wake_dt + timedelta(hours=7)).strftime("%H:%M"),
        "evening_peak": (wake_dt + timedelta(hours=11)).strftime("%H:%M"),
        "bedtime": sleep_time,
        "hours": hours,
        "energy": energy
    }

def analyze_sleep_logs(logs):
    # Calculate averages from sleep logs
    if not logs:
        return 0, "N/A", 0
    total_debt = 0
    midpoints = []
    energy_levels = []
    for sleep_time, wake_time, energy in logs:
        debt = calculate_sleep_debt(sleep_time, wake_time)
        total_debt += debt
        rhythm = calculate_circadian_rhythm(sleep_time, wake_time)
        midpoints.append(datetime.strptime(rhythm["midpoint"], "%H:%M").hour +
                         datetime.strptime(rhythm["midpoint"], "%H:%M").minute / 60)
        energy_levels.append(energy)
    avg_debt = round(total_debt / len(logs), 2)
    avg_midpoint = sum(midpoints) / len(midpoints)
    avg_chronotype = "Early Bird" if avg_midpoint < 3.5 else "Intermediate" if avg_midpoint < 5 else "Night Owl"
    avg_energy = round(sum(energy_levels) / len(energy_levels), 1)
    return avg_debt, avg_chronotype, avg_energy

def train_ml_model():
    # Train a logistic regression model for sleep quality (placeholder)
    try:
        data = pd.read_csv("data/sleep_health.csv")
        X = data[["Sleep Duration", "Physical Activity Level", "Stress Level"]]
        y = data["Quality of Sleep"]
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        model = LogisticRegression(max_iter=1000)
        model.fit(X_scaled, y)
        return model, scaler
    except FileNotFoundError:
        return None, None

def predict_sleep_quality(model, scaler, sleep_duration, activity_level, stress_level):
    # Predict sleep quality or return default if model unavailable
    if model is None or scaler is None:
        return 6
    input_data = scaler.transform([[sleep_duration, activity_level, stress_level]])
    return model.predict(input_data)[0]

def generate_recommendations(sleep_debt, chronotype, sleep_quality, rhythm):
    # Provide personalized sleep tips
    tips = []
    if sleep_debt > 1:
        tips.append(f"You’re missing {sleep_debt} hours of sleep. Aim for 8+ hours tonight!")
    if chronotype == "Night Owl":
        tips.append(f"Wind down with calm music an hour before {rhythm['bedtime']}.")
    elif chronotype == "Early Bird":
        tips.append(f"Avoid late naps to stick to {rhythm['bedtime']}.")
    if sleep_quality < 6:
        tips.append(f"Try a 10-minute calm-down routine before {rhythm['bedtime']}.")
    tips.extend([
        f"Wake Up Time ({rhythm['wake_time']}): Start your day here.",
        f"Peak Performance ({rhythm['morning_peak']}): Tackle tough tasks now.",
        f"Afternoon Dip ({rhythm['dip_time']}): Take a short break or nap.",
        f"Evening Boost ({rhythm['evening_peak']}): Good for exercise or projects.",
        f"Bedtime ({rhythm['bedtime']}): Get to bed to reset your rhythm."
    ])
    return tips