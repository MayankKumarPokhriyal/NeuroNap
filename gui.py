# gui.py: Manages the graphical user interface for NeuroNap
# Author: Mayank and Kartikeya
# Date: March 25, 2025
# Description: Implements a Tkinter-based GUI with dropdowns, sliders, and interactive features for sleep logging and reporting

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdfcanvas
import os
from datetime import datetime
import backend
import database
import ml

class NeuroNapApp:
    def __init__(self, root):
        """Initialize the GUI application with Tkinter root window."""
        self.root = root
        self.root.title("NeuroNap")  # Set window title
        self.root.geometry("900x700")  # Set window size
        self.root.configure(bg="#F5F6F5")  # Light background color
        self.user_id = None  # Current user ID
        self.user_name = None  # Current user name
        self.ml_model, self.ml_scaler = ml.train_model()  # Load ML model and scaler
        self.tooltip = None  # Tooltip for hover help

        database.init_db()  # Initialize SQLite database

        # Main frame to hold sub-frames
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(expand=True)

        # Sub-frames for authentication, logging, and results
        self.auth_frame = ttk.Frame(self.main_frame, padding=20)
        self.log_frame = ttk.Frame(self.main_frame, padding=20)
        self.result_frame = ttk.Frame(self.main_frame, padding=20)

        # Configure styles for consistent look
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 12), foreground="black", padding=5)
        self.style.configure("TLabel", font=("Arial", 12), background="#F5F6F5")
        self.style.configure("TCombobox", font=("Arial", 12))
        self.style.configure("TEntry", font=("Arial", 12))

        # Time options for dropdowns (15-minute intervals)
        self.times = [f"{h:02d}:{m:02d}" for h in range(24) for m in [0, 15, 30, 45]]
        # Store last used inputs for Quick Fill
        self.last_inputs = {"sleep_time": "23:00", "wake_time": "07:00", "energy": 7, "stress": 5, "activity": 60}

        self.show_auth_frame()  # Start with authentication screen

    def center_frame(self, frame):
        """Center a frame within the main window."""
        frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

    def clear_frames(self):
        """Hide all sub-frames."""
        for frame in [self.auth_frame, self.log_frame, self.result_frame]:
            frame.grid_forget()

    def show_tooltip(self, widget, text, x_offset=10, y_offset=10):
        """Show a tooltip on hover with given text."""
        if self.tooltip:
            self.tooltip.destroy()
        self.tooltip = tk.Label(self.root, text=text, bg="lightyellow", relief="solid", borderwidth=1, font=("Arial", 10))
        x, y = widget.winfo_rootx() + x_offset, widget.winfo_rooty() + y_offset
        self.tooltip.place(x=x, y=y)

    def hide_tooltip(self):
        """Hide the tooltip."""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    def show_auth_frame(self):
        """Display login/registration screen."""
        self.clear_frames()
        self.center_frame(self.auth_frame)

        # Title label
        ttk.Label(self.auth_frame, text="Welcome to NeuroNap", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        # Name input
        ttk.Label(self.auth_frame, text="Name:").grid(row=1, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(self.auth_frame)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)
        self.name_entry.bind("<Enter>", lambda e: self.show_tooltip(self.name_entry, "Enter your full name"))
        self.name_entry.bind("<Leave>", lambda e: self.hide_tooltip())

        # Email input
        ttk.Label(self.auth_frame, text="Email:").grid(row=2, column=0, padx=5, pady=5)
        self.email_entry = ttk.Entry(self.auth_frame)
        self.email_entry.grid(row=2, column=1, padx=5, pady=5)
        self.email_entry.bind("<Enter>", lambda e: self.show_tooltip(self.email_entry, "Enter your email"))
        self.email_entry.bind("<Leave>", lambda e: self.hide_tooltip())

        # Password input
        ttk.Label(self.auth_frame, text="Password:").grid(row=3, column=0, padx=5, pady=5)
        self.pass_entry = ttk.Entry(self.auth_frame, show="*")
        self.pass_entry.grid(row=3, column=1, padx=5, pady=5)
        self.pass_entry.bind("<Enter>", lambda e: self.show_tooltip(self.pass_entry, "Enter your password"))
        self.pass_entry.bind("<Leave>", lambda e: self.hide_tooltip())

        # Age input for new users
        ttk.Label(self.auth_frame, text="Age (new users):").grid(row=4, column=0, padx=5, pady=5)
        self.age_entry = ttk.Entry(self.auth_frame)
        self.age_entry.grid(row=4, column=1, padx=5, pady=5)
        self.age_entry.bind("<Enter>", lambda e: self.show_tooltip(self.age_entry, "Enter your age (numbers only)"))
        self.age_entry.bind("<Leave>", lambda e: self.hide_tooltip())

        # Login and Register buttons
        ttk.Button(self.auth_frame, text="Login", command=self.login).grid(row=5, column=0, pady=10)
        ttk.Button(self.auth_frame, text="Register", command=self.register).grid(row=5, column=1, pady=10)

    def show_log_frame(self):
        """Display sleep log entry screen with dropdowns and sliders."""
        self.clear_frames()
        self.center_frame(self.log_frame)

        # Title with user name
        ttk.Label(self.log_frame, text=f"Log Sleep for {self.user_name}", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        # Sleep time dropdown
        ttk.Label(self.log_frame, text="Sleep Time:").grid(row=1, column=0, padx=5, pady=5)
        self.sleep_combo = ttk.Combobox(self.log_frame, values=self.times, state="readonly")
        self.sleep_combo.set(self.last_inputs["sleep_time"])
        self.sleep_combo.grid(row=1, column=1, padx=5, pady=5)
        self.sleep_combo.bind("<Enter>", lambda e: self.show_tooltip(self.sleep_combo, "Select sleep start time"))
        self.sleep_combo.bind("<Leave>", lambda e: self.hide_tooltip())

        # Wake time dropdown
        ttk.Label(self.log_frame, text="Wake Time:").grid(row=2, column=0, padx=5, pady=5)
        self.wake_combo = ttk.Combobox(self.log_frame, values=self.times, state="readonly")
        self.wake_combo.set(self.last_inputs["wake_time"])
        self.wake_combo.grid(row=2, column=1, padx=5, pady=5)
        self.wake_combo.bind("<Enter>", lambda e: self.show_tooltip(self.wake_combo, "Select wake time"))
        self.wake_combo.bind("<Leave>", lambda e: self.hide_tooltip())

        # Energy level slider
        ttk.Label(self.log_frame, text="Energy Level (1-10):").grid(row=3, column=0, padx=5, pady=5)
        energy_frame = ttk.Frame(self.log_frame)
        energy_frame.grid(row=3, column=1, padx=5, pady=5)
        self.energy_var = tk.IntVar(value=self.last_inputs["energy"])
        self.energy_slider = ttk.Scale(energy_frame, from_=1, to=10, orient="horizontal", variable=self.energy_var,
                                      command=lambda x: self.energy_var.set(int(float(x) + 0.5)))
        self.energy_slider.grid(row=0, column=0)
        # Add tick marks for 1-10
        canvas = tk.Canvas(energy_frame, width=150, height=20, bg="#F5F6F5", highlightthickness=0)
        canvas.grid(row=1, column=0)
        for i in range(1, 11):
            x = (i - 1) * 15
            canvas.create_line(x, 0, x, 10, fill="black")
            canvas.create_text(x, 15, text=str(i), font=("Arial", 8))
        self.energy_slider.bind("<Enter>", lambda e: self.show_tooltip(self.energy_slider, "Slide to set energy level"))
        self.energy_slider.bind("<Leave>", lambda e: self.hide_tooltip())

        # Stress level slider
        ttk.Label(self.log_frame, text="Stress Level (1-10):").grid(row=4, column=0, padx=5, pady=5)
        stress_frame = ttk.Frame(self.log_frame)
        stress_frame.grid(row=4, column=1, padx=5, pady=5)
        self.stress_var = tk.IntVar(value=self.last_inputs["stress"])
        self.stress_slider = ttk.Scale(stress_frame, from_=1, to=10, orient="horizontal", variable=self.stress_var,
                                      command=lambda x: self.stress_var.set(int(float(x) + 0.5)))
        self.stress_slider.grid(row=0, column=0)
        # Add tick marks for 1-10
        canvas = tk.Canvas(stress_frame, width=150, height=20, bg="#F5F6F5", highlightthickness=0)
        canvas.grid(row=1, column=0)
        for i in range(1, 11):
            x = (i - 1) * 15
            canvas.create_line(x, 0, x, 10, fill="black")
            canvas.create_text(x, 15, text=str(i), font=("Arial", 8))
        self.stress_slider.bind("<Enter>", lambda e: self.show_tooltip(self.stress_slider, "Slide to set stress level"))
        self.stress_slider.bind("<Leave>", lambda e: self.hide_tooltip())

        # Activity level input
        ttk.Label(self.log_frame, text="Activity Level (min):").grid(row=5, column=0, padx=5, pady=5)
        self.activity_entry = ttk.Entry(self.log_frame)
        self.activity_entry.insert(0, str(self.last_inputs["activity"]))
        self.activity_entry.grid(row=5, column=1, padx=5, pady=5)
        self.activity_entry.bind("<Enter>", lambda e: self.show_tooltip(self.activity_entry, "Enter minutes of physical activity"))
        self.activity_entry.bind("<Leave>", lambda e: self.hide_tooltip())
        self.activity_entry.bind("<FocusIn>", lambda e: self.activity_entry.delete(0, tk.END) if self.activity_entry.get() == str(self.last_inputs["activity"]) else None)

        # Buttons: Submit, Clear, Quick Fill
        button_frame = ttk.Frame(self.log_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Submit", command=self.log_sleep).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_log).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Quick Fill", command=self.quick_fill).grid(row=0, column=2, padx=5)
        ttk.Button(self.log_frame, text="Back", command=self.show_auth_frame).grid(row=7, column=0, columnspan=2, pady=5)

        # Bind Enter key to submit
        self.log_frame.bind_all("<Return>", lambda e: self.log_sleep())

    def clear_log(self):
        """Clear all input fields in the sleep log screen."""
        self.sleep_combo.set(self.times[0])  # Reset to first time
        self.wake_combo.set(self.times[0])   # Reset to first time
        self.energy_var.set(1)               # Reset slider
        self.stress_var.set(1)               # Reset slider
        self.activity_entry.delete(0, tk.END)
        self.activity_entry.insert(0, "0")   # Reset to 0

    def quick_fill(self):
        """Fill fields with last used or default values."""
        self.sleep_combo.set(self.last_inputs["sleep_time"])
        self.wake_combo.set(self.last_inputs["wake_time"])
        self.energy_var.set(self.last_inputs["energy"])
        self.stress_var.set(self.last_inputs["stress"])
        self.activity_entry.delete(0, tk.END)
        self.activity_entry.insert(0, str(self.last_inputs["activity"]))

    def show_result_frame(self, sleep_debt, rhythm, sleep_quality, tips, avg_debt, avg_chronotype, avg_energy, logs):
        """Display sleep report with symmetrical layout and enhanced insights."""
        self.clear_frames()
        self.center_frame(self.result_frame)

        # Title centered at the top
        title_label = ttk.Label(self.result_frame, text=f"{self.user_name}'s Sleeping Report", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Two-column layout for symmetry
        left_column = ttk.Frame(self.result_frame)
        right_column = ttk.Frame(self.result_frame)
        left_column.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        right_column.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        self.result_frame.grid_columnconfigure(0, weight=1)
        self.result_frame.grid_columnconfigure(1, weight=1)

        # Left column: Report text
        report_text = f"Latest Sleep Log:\nSleep Debt: {sleep_debt} hours\nMidpoint: {rhythm['midpoint']}\nChronotype: {rhythm['chronotype']}\nSleep Quality: {sleep_quality}/10\n\n"
        report_text += f"Average Over {len(logs)} Logs:\nAvg Sleep Debt: {avg_debt} hours\nAvg Chronotype: {avg_chronotype}\nAvg Energy: {avg_energy}/10\n\n"
        report_text += "Past Logs:\n" + "\n".join([f"Log {i+1}: Sleep {s} - Wake {w}, Energy {e}" for i, (s, w, e, _, _) in enumerate(logs[:3])]) + "\n\n"
        suggestions_text = "Suggestions:\n" + "\n".join(tips[:5]) + "\n\n"

        # Add benefits and techniques
        benefits_text = "✅ Benefits of Following Circadian Rhythm\n" \
                       "1. Improved Sleep Quality\n" \
                       "   • Fall asleep faster and wake up refreshed.\n" \
                       "   • Better REM and deep sleep phases.\n" \
                       "2. Higher Energy & Focus\n" \
                       "   • Peak alertness during the day.\n" \
                       "   • Reduced brain fog and midday slumps.\n" \
                       "3. Balanced Hormones\n" \
                       "   • Optimized cortisol, melatonin, and testosterone cycles.\n" \
                       "   • Supports muscle growth, libido, and mental stability.\n" \
                       "4. Enhanced Metabolism & Weight Loss\n" \
                       "   • Better insulin sensitivity and digestion.\n" \
                       "   • Aligns eating with natural digestive efficiency.\n" \
                       "5. Better Mental Health\n" \
                       "   • Reduced risk of depression and anxiety.\n" \
                       "   • Stable mood regulation.\n" \
                       "6. Stronger Immune Function\n" \
                       "   • Reduced inflammation.\n" \
                       "   • Optimized cellular repair during sleep.\n\n"

        techniques_text = "🧠 Techniques to Align with Circadian Rhythm\n" \
                         "🌞 Morning (6 AM – 10 AM)\n" \
                         "   • Wake up at the same time daily, preferably at sunrise.\n" \
                         "   • Get sunlight exposure within 30 minutes of waking (20+ minutes outdoors).\n" \
                         "   • Avoid screens for the first 30 minutes.\n" \
                         "   • Hydrate and eat a high-protein breakfast to jumpstart metabolism.\n" \
                         "🕑 Daytime (10 AM – 6 PM)\n" \
                         "   • Do focused mental tasks and workouts in the first half of the day (peak alertness).\n" \
                         "   • Eat largest meal around midday, aligning with peak digestion.\n" \
                         "   • Avoid caffeine after 2 PM.\n" \
                         "🌇 Evening (6 PM – 10 PM)\n" \
                         "   • Dim lights after sunset (use warm or red lights).\n" \
                         "   • Limit screen use or use blue light blockers.\n" \
                         "   • Eat a light dinner, ideally 2-3 hours before bedtime.\n" \
                         "   • Start winding down rituals (reading, journaling, stretching).\n" \
                         "🌙 Night (10 PM – 6 AM)\n" \
                         "   • Sleep between 10 PM – 6 AM for best recovery.\n" \
                         "   • Maintain a cool, dark, quiet bedroom.\n" \
                         "   • Avoid eating, exercising, or stressing late at night.\n" \
                         "   • Consistent sleep and wake time is key—even on weekends.\n" \
                         "🔁 Optional Add-ons\n" \
                         "   • Circadian Fasting (Time-Restricted Eating): Eat only between 8 AM and 6 PM.\n" \
                         "   • Sun-mimicking lamps if living in low-sunlight areas.\n"

        full_text = report_text + suggestions_text + benefits_text + techniques_text
        report_display = tk.Text(left_column, height=30, width=50, font=("Arial", 10), wrap="word")
        report_display.pack(expand=True, fill="both", padx=10, pady=10)
        report_display.insert(tk.END, full_text)
        report_display.config(state="disabled")

        # Right column: Circadian rhythm graph
        fig, ax = plt.subplots(figsize=(4, 4))  # Reduced size for symmetry
        ax.plot(rhythm["energy"], rhythm["hours"], color="#007BFF", linewidth=2)
        for time, label, color in [
            (rhythm["wake_time"], "Wake", "green"), (rhythm["morning_peak"], "Peak", "red"),
            (rhythm["dip_time"], "Dip", "orange"), (rhythm["evening_peak"], "Evening", "purple"),
            (rhythm["bedtime"], "Bed", "blue")
        ]:
            h, m = map(int, time.split(":"))
            y = h + m / 60
            ax.axhline(y, color=color, linestyle="--", alpha=0.5, linewidth=1)
            ax.text(0.5, y, f"{label}: {time}", color=color, fontsize=8, va="center")
        ax.set_xlabel("Energy (0-10)", fontsize=10)
        ax.set_ylabel("Time (Hours)", fontsize=10)
        ax.set_ylim(0, 24)
        ax.set_yticks(range(0, 25, 2))
        ax.grid(True, alpha=0.3)
        ax.set_title(f"{self.user_name}'s Circadian Rhythm", fontsize=12, pad=10)
        canvas = FigureCanvasTkAgg(fig, master=right_column)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)

        # Buttons centered at the bottom
        button_frame = ttk.Frame(self.result_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="Log Another", command=self.show_log_frame).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Save Report", command=lambda: self.save_report(report_text, suggestions_text + benefits_text + techniques_text, rhythm)).grid(row=0, column=1, padx=5)

    def login(self):
        """Authenticate user and switch to log frame."""
        email = self.email_entry.get()
        password = self.pass_entry.get()
        result = database.login_user(email, password)
        if result:
            self.user_id, self.user_name = result
            # Load last log for Quick Fill
            logs = database.get_user_sleep_logs(self.user_id)
            if logs:
                last_log = logs[-1]
                self.last_inputs = {
                    "sleep_time": last_log[0],
                    "wake_time": last_log[1],
                    "energy": last_log[2],
                    "stress": last_log[3],
                    "activity": last_log[4]
                }
            messagebox.showinfo("Success", f"Welcome back, {self.user_name}!")
            self.show_log_frame()
        else:
            messagebox.showerror("Error", "Invalid email or password.")

    def register(self):
        """Register a new user and switch to log frame."""
        name = self.name_entry.get()
        email = self.email_entry.get()
        password = self.pass_entry.get()
        try:
            age = int(self.age_entry.get())
            user_id = database.register_user(name, email, password, age)
            if user_id:
                self.user_id = user_id
                self.user_name = name
                messagebox.showinfo("Success", f"Registered as {self.user_name}!")
                self.show_log_frame()
            else:
                messagebox.showerror("Error", "Email already taken.")
        except ValueError:
            messagebox.showerror("Error", "Age must be a number.")

    def log_sleep(self):
        """Log sleep data and display results."""
        try:
            sleep_time = self.sleep_combo.get()
            wake_time = self.wake_combo.get()
            if not sleep_time or not wake_time:
                raise ValueError("Please select sleep and wake times.")
            energy = self.energy_var.get()
            stress = self.stress_var.get()
            activity = self.activity_entry.get()
            activity = int(activity) if activity else 0
            if not (0 <= energy <= 10 and 0 <= stress <= 10 and activity >= 0):
                raise ValueError("Energy and Stress must be 1-10, Activity must be non-negative.")
            datetime.strptime(sleep_time, "%H:%M")
            datetime.strptime(wake_time, "%H:%M")

            # Update last inputs for Quick Fill
            self.last_inputs = {
                "sleep_time": sleep_time,
                "wake_time": wake_time,
                "energy": energy,
                "stress": stress,
                "activity": activity
            }
            database.log_sleep(self.user_id, sleep_time, wake_time, energy, stress, activity)
            logs = database.get_user_sleep_logs(self.user_id)

            # Calculate sleep metrics
            sleep_debt = backend.calculate_sleep_debt(sleep_time, wake_time)
            duration = 8 - sleep_debt if sleep_debt <= 8 else 0
            rhythm = backend.calculate_circadian_rhythm(sleep_time, wake_time, energy)
            sleep_quality = ml.predict_sleep_quality(self.ml_model, self.ml_scaler, duration, activity, stress)
            tips = backend.generate_recommendations(sleep_debt, rhythm["chronotype"], sleep_quality, rhythm)
            avg_debt, avg_chronotype, avg_energy = backend.analyze_sleep_logs(logs)

            self.show_result_frame(sleep_debt, rhythm, sleep_quality, tips, avg_debt, avg_chronotype, avg_energy, logs)
        except ValueError as e:
            messagebox.showerror("Error", str(e) or "Invalid time format (use HH:MM).")

    def save_report(self, report_text, suggestions_text, rhythm):
        """Save sleep report as PDF with graph and FAQs."""
        pdf_path = f"neuronap_report_{self.user_name}.pdf"
        c = pdfcanvas.Canvas(pdf_path, pagesize=letter)
        c.setFont("Helvetica", 10)

        # Write report text
        y = 750
        c.drawString(50, y, f"{self.user_name}'s Sleeping Report")
        y -= 20
        for line in report_text.split("\n"):
            c.drawString(50, y, line)
            y -= 12
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = 750

        # Write suggestions, benefits, and techniques
        y -= 20
        c.drawString(50, y, "Suggestions, Benefits, and Techniques")
        y -= 12
        for line in suggestions_text.split("\n"):
            c.drawString(50, y, line)
            y -= 12
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = 750

        # Add circadian rhythm graph
        c.showPage()
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.plot(rhythm["energy"], rhythm["hours"], color="#007BFF", linewidth=2)
        for time, label, color in [
            (rhythm["wake_time"], "Wake", "green"), (rhythm["morning_peak"], "Peak", "red"),
            (rhythm["dip_time"], "Dip", "orange"), (rhythm["evening_peak"], "Evening", "purple"),
            (rhythm["bedtime"], "Bed", "blue")
        ]:
            h, m = map(int, time.split(":"))
            y_val = h + m / 60
            ax.axhline(y_val, color=color, linestyle="--", alpha=0.5, linewidth=1)
            ax.text(0.5, y_val, f"{label}: {time}", color=color, fontsize=8, va="center")
        ax.set_xlabel("Energy (0-10)", fontsize=10)
        ax.set_ylabel("Time (Hours)", fontsize=10)
        ax.set_ylim(0, 24)
        ax.set_yticks(range(0, 25, 2))
        ax.grid(True, alpha=0.3)
        ax.set_title(f"{self.user_name}'s Circadian Rhythm", fontsize=12, pad=10)
        fig.savefig("temp_graph.png", bbox_inches="tight")
        plt.close(fig)
        c.drawImage("temp_graph.png", 100, 400, width=350, height=300)
        os.remove("temp_graph.png")

        # Add FAQs
        c.showPage()
        y = 750
        c.drawString(50, y, "Frequently Asked Questions")
        y -= 12
        faq_text = """Sleep and Immune Function: Sleep boosts immunity. Missing 7 hours weekly ups cold risk!
Sleep Need & Debt: Most need 7-9 hours. Debt accumulates over 2 weeks—keep under 5 hours.
Circadian Rhythm: Energy peaks morning/evening, dips midday, tied to sleep habits.
Alcohol and Sleep: May aid sleep onset but disrupts deep sleep. Avoid 3-4 hours pre-bed.
Naps: 15-25 min naps during dips recharge without affecting night sleep.
Sleep Schedule Tips: Morning light, no caffeine 10 hours before bed, cozy sleep space."""
        for line in faq_text.split("\n"):
            c.drawString(50, y, line)
            y -= 12
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = 750
        c.save()
        messagebox.showinfo("Success", f"Report saved as {pdf_path}")

def run_app():
    """Launch the NeuroNap application."""
    root = tk.Tk()
    app = NeuroNapApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_app()