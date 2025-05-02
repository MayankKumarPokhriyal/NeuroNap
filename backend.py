# backend.py: Handles sleep data processing and circadian rhythm calculations
# Author: Mayank Kumar Pokhriyal
# Date: April 09, 2025
# Description: Contains logic for sleep debt, circadian rhythm calculations, log analysis, and recommendations

from datetime import datetime, timedelta
import numpy as np
from scipy.interpolate import interp1d

class SleepData:
    def __init__(self, sleep_time, wake_time, energy, stress, activity):
        """Initialize a sleep data entry with user inputs."""
        self.sleep_time = sleep_time  # Sleep start time in HH:MM
        self.wake_time = wake_time    # Wake time in HH:MM
        self.energy = energy          # Energy level (1-10)
        self.stress = stress          # Stress level (1-10)
        self.activity = activity      # Physical activity in minutes

def calculate_sleep_debt(sleep_time, wake_time):
    """Calculate sleep debt based on an 8-hour target.

    Args:
        sleep_time (str): Sleep start time in HH:MM format.
        wake_time (str): Wake time in HH:MM format.

    Returns:
        float: Sleep debt in hours (rounded to 2 decimals).
    """
    sleep_dt = datetime.strptime(sleep_time, "%H:%M")
    wake_dt = datetime.strptime(wake_time, "%H:%M")
    if wake_dt < sleep_dt:
        wake_dt += timedelta(days=1)  # Handle overnight sleep
    duration = (wake_dt - sleep_dt).seconds / 3600
    return round(max(8 - duration, 0), 2)

def calculate_circadian_rhythm(sleep_time, wake_time, energy):
    """Calculate circadian rhythm with energy-based adjustments.

    Args:
        sleep_time (str): Sleep start time in HH:MM format.
        wake_time (str): Wake time in HH:MM format.
        energy (int): Energy level (1-10).

    Returns:
        dict: Circadian rhythm details (midpoint, chronotype, key times, energy curve).
    """
    sleep_dt = datetime.strptime(sleep_time, "%H:%M")
    wake_dt = datetime.strptime(wake_time, "%H:%M")
    if wake_dt < sleep_dt:
        wake_dt += timedelta(days=1)
    duration = (wake_dt - sleep_dt).seconds / 3600
    midpoint_dt = sleep_dt + timedelta(hours=duration / 2)
    midpoint = midpoint_dt.strftime("%H:%M")
    midpoint_hour = midpoint_dt.hour + midpoint_dt.minute / 60
    # Determine chronotype based on sleep midpoint
    chronotype = "Early Bird" if midpoint_hour < 3.5 else "Intermediate" if midpoint_hour < 5 else "Night Owl"

    # Calculate key circadian times
    wake_hour = wake_dt.hour + wake_dt.minute / 60
    sleep_hour = sleep_dt.hour + sleep_dt.minute / 60 if sleep_dt > wake_dt else sleep_dt.hour + sleep_dt.minute / 60 + 24
    key_hours = [0.0, wake_hour, (wake_hour + 3) % 24, (wake_hour + 7) % 24, (wake_hour + 11) % 24, sleep_hour % 24, 24.0]
    # Base energy levels adjusted by user-reported energy
    base_energy = [2, 2, 10, 3, 7, 2, 2]
    adjusted_energy = [e * (energy / 10) for e in base_energy]  # Scale by reported energy

    # Interpolate energy curve for visualization
    unique_hours = sorted(set(key_hours))
    unique_energy = [adjusted_energy[key_hours.index(h)] for h in unique_hours if h in key_hours]
    hours = np.linspace(0, 24, 100)
    f = interp1d(unique_hours, unique_energy, kind="cubic", bounds_error=False, fill_value=2 * (energy / 10))
    energy_curve = np.clip(f(hours), 0, 10)

    return {
        "midpoint": midpoint,
        "chronotype": chronotype,
        "wake_time": wake_dt.strftime("%H:%M"),
        "morning_peak": (wake_dt + timedelta(hours=3)).strftime("%H:%M"),
        "dip_time": (wake_dt + timedelta(hours=7)).strftime("%H:%M"),
        "evening_peak": (wake_dt + timedelta(hours=11)).strftime("%H:%M"),
        "bedtime": sleep_time,
        "hours": hours,
        "energy": energy_curve
    }

def analyze_sleep_logs(logs):
    """Analyze sleep logs to compute averages.

    Args:
        logs (list): List of tuples (sleep_time, wake_time, energy, stress, activity).

    Returns:
        tuple: Average sleep debt, chronotype, and energy level.
    """
    if not logs:
        return 0, "N/A", 0
    total_debt = 0
    midpoints = []
    energy_levels = []
    for sleep_time, wake_time, energy, _, _ in logs:
        debt = calculate_sleep_debt(sleep_time, wake_time)
        total_debt += debt
        rhythm = calculate_circadian_rhythm(sleep_time, wake_time, energy)
        midpoints.append(datetime.strptime(rhythm["midpoint"], "%H:%M").hour +
                         datetime.strptime(rhythm["midpoint"], "%H:%M").minute / 60)
        energy_levels.append(energy)
    avg_debt = round(total_debt / len(logs), 2)
    avg_midpoint = sum(midpoints) / len(midpoints)
    avg_chronotype = "Early Bird" if avg_midpoint < 3.5 else "Intermediate" if avg_midpoint < 5 else "Night Owl"
    avg_energy = round(sum(energy_levels) / len(energy_levels), 1)
    return avg_debt, avg_chronotype, avg_energy

def generate_recommendations(sleep_debt, chronotype, sleep_quality, rhythm):
    """Generate personalized sleep recommendations.

    Args:
        sleep_debt (float): Hours of sleep debt.
        chronotype (str): User's chronotype (Early Bird, Intermediate, Night Owl).
        sleep_quality (int): Predicted sleep quality (1-10).
        rhythm (dict): Circadian rhythm details.

    Returns:
        list: List of recommendation strings.
    """
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