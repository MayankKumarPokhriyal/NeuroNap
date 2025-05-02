# NeuroNap Instructions

## Overview
NeuroNap tracks sleep patterns, calculates sleep debt, predicts sleep quality using machine learning, and visualizes circadian rhythms via a Tkinter GUI.

## Setup
1. Install Python 3.12+.
2. Install dependencies: `pip install numpy scipy pandas scikit-learn matplotlib reportlab pytest`
3. Save all files (`main.py`, `gui.py`, `backend.py`, `database.py`, `ml.py`, `test_neuronap.py`, `sleep_health.csv`) in a folder.
4. Run tests: `pytest test_neuronap.py`

## Usage
1. **Run**: `cd /path/to/NeuroNap; python main.py`
2. **Register**: Enter name, email, password, age; click "Register".
3. **Login**: Enter email, password; click "Login".
4. **Log Sleep**: Input sleep/wake times (HH:MM), energy (1-10), stress (slider); click "Submit".
5. **View Report**: See sleep debt, quality, chronotype, suggestions (e.g., Wake Up Time, Peak Performance), and graph.
6. **Save Report**: Click "Save Report" to generate a PDF locally with report, suggestions, graph, and FAQs.

## Features
- Calculates sleep debt and circadian rhythm.
- Predicts sleep quality with `scikit-learn` using `sleep_health.csv`.
- Stores data in SQLite (`neuronap.db`).
- GUI with 5 interactive elements: Login, Register, Submit, Stress Slider, Save Report.

## Notes
- Requires `sleep_health.csv` for ML; defaults to quality 6 if missing.
- Tested with Python 3.12+.