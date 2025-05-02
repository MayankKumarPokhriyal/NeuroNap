# database.py: Manages SQLite database operations for NeuroNap
# Author: Bright and Mayank
# Date: April 09, 2025
# Description: Handles user registration, authentication, and sleep log storage

import sqlite3
import hashlib

class User:
    def __init__(self, user_id, name, email, password, age):
        """Initialize a user object with provided details."""
        self.user_id = user_id      # Unique identifier for the user
        self.name = name            # User's full name
        self.email = email          # User's email address
        self.password = password    # Hashed password
        self.age = age              # User's age

def init_db():
    """Initialize the SQLite database with users and sleep_logs tables."""
    conn = sqlite3.connect("neuronap.db")
    c = conn.cursor()
    # Create users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 email TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL,
                 age INTEGER NOT NULL)''')
    # Create sleep_logs table with constraints
    c.execute('''CREATE TABLE IF NOT EXISTS sleep_logs (
                 log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER NOT NULL,
                 sleep_time TEXT NOT NULL,
                 wake_time TEXT NOT NULL,
                 energy_level INTEGER CHECK(energy_level >= 1 AND energy_level <= 10),
                 stress_level INTEGER CHECK(stress_level >= 1 AND stress_level <= 10),
                 activity_level INTEGER CHECK(activity_level >= 0),
                 FOREIGN KEY (user_id) REFERENCES users(user_id))''')
    conn.commit()
    conn.close()

def register_user(name, email, password, age):
    """Register a new user with hashed password.

    Args:
        name (str): User's full name.
        email (str): User's email address.
        password (str): User's password.
        age (int): User's age.

    Returns:
        int: User ID if successful, None if email is taken.
    """
    conn = sqlite3.connect("neuronap.db")
    c = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    try:
        c.execute("INSERT INTO users (name, email, password, age) VALUES (?, ?, ?, ?)",
                  (name, email, hashed_pw, age))
        user_id = c.lastrowid
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def login_user(email, password):
    """Authenticate a user and return user details.

    Args:
        email (str): User's email address.
        password (str): User's password.

    Returns:
        tuple: (user_id, name) if authenticated, None otherwise.
    """
    conn = sqlite3.connect("neuronap.db")
    c = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT user_id, name FROM users WHERE email = ? AND password = ?",
              (email, hashed_pw))
    result = c.fetchone()
    conn.close()
    return result if result else None

def log_sleep(user_id, sleep_time, wake_time, energy_level, stress_level, activity_level):
    """Log a sleep entry for a user.

    Args:
        user_id (int): User's ID.
        sleep_time (str): Sleep start time in HH:MM.
        wake_time (str): Wake time in HH:MM.
        energy_level (int): Energy level (1-10).
        stress_level (int): Stress level (1-10).
        activity_level (int): Physical activity in minutes.
    """
    conn = sqlite3.connect("neuronap.db")
    c = conn.cursor()
    c.execute("INSERT INTO sleep_logs (user_id, sleep_time, wake_time, energy_level, stress_level, activity_level) VALUES (?, ?, ?, ?, ?, ?)",
              (user_id, sleep_time, wake_time, energy_level, stress_level, activity_level))
    conn.commit()
    conn.close()