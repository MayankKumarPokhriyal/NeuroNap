# database.py: Handles SQLite database operations for users and sleep logs
import sqlite3
import hashlib

def init_db():
    """Initialize the SQLite database with users and sleep_logs tables."""
    conn = sqlite3.connect("neuronap.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 email TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL,
                 age INTEGER NOT NULL,
                 chronotype TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sleep_logs (
                 log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER NOT NULL,
                 sleep_time TEXT NOT NULL,
                 wake_time TEXT NOT NULL,
                 energy_level INTEGER CHECK(energy_level >= 1 AND energy_level <= 10),
                 FOREIGN KEY (user_id) REFERENCES users(user_id))''')
    conn.commit()
    conn.close()

def register_user(name, email, password, age):
    """Register a new user with hashed password."""
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
    """Authenticate a user and return user_id and name."""
    conn = sqlite3.connect("neuronap.db")
    c = conn.cursor()
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT user_id, name FROM users WHERE email = ? AND password = ?",
              (email, hashed_pw))
    result = c.fetchone()
    conn.close()
    return result if result else None

def log_sleep(user_id, sleep_time, wake_time, energy_level):
    """Log a sleep entry for a user."""
    conn = sqlite3.connect("neuronap.db")
    c = conn.cursor()
    c.execute("INSERT INTO sleep_logs (user_id, sleep_time, wake_time, energy_level) VALUES (?, ?, ?, ?)",
              (user_id, sleep_time, wake_time, energy_level))
    conn.commit()
    conn.close()

def get_user_sleep_logs(user_id):
    """Retrieve all sleep logs for a user."""
    conn = sqlite3.connect("neuronap.db")
    c = conn.cursor()
    c.execute("SELECT sleep_time, wake_time, energy_level FROM sleep_logs WHERE user_id = ?",
              (user_id,))
    logs = c.fetchall()
    conn.close()
    return logs