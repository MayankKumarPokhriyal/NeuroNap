# test_neuronap.py: Unit tests for NeuroNap functionality
# Author: Karthikeya
# Date: April 11, 2025
# Description: Contains pytest tests for key functions to ensure reliability

import pytest
import backend
import database
import ml
import os

def test_calculate_sleep_debt():
    """Test sleep debt calculation for various sleep durations."""
    assert backend.calculate_sleep_debt("23:00", "07:00") == 0  # 8 hours, no debt
    assert backend.calculate_sleep_debt("01:00", "05:00") == 4  # 4 hours, 4-hour debt

def test_circadian_rhythm_chronotype():
    """Test chronotype assignment in circadian rhythm calculation."""
    rhythm = backend.calculate_circadian_rhythm("22:00", "06:00", 8)
    assert rhythm["chronotype"] == "Early Bird"  # Early sleep midpoint
    rhythm = backend.calculate_circadian_rhythm("02:00", "10:00", 6)
    assert rhythm["chronotype"] == "Night Owl"  # Late sleep midpoint

def test_database_user_registration():
    """Test user registration and login functionality."""
    database.init_db()
    user_id = database.register_user("TestUser", "test@example.com", "pass123", 25)
    assert user_id is not None  # Successful registration
    result = database.login_user("test@example.com", "pass123")
    assert result == (user_id, "TestUser")  # Successful login
    os.remove("neuronap.db")  # Clean up test database

