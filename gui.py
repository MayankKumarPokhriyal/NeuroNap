import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdfcanvas
import os
import backend
import database
from datetime import datetime, timedelta
import sqlite3
import re
import tempfile

class NeuroNapApp:
    def __init__(self, root):
        # Set up the main window
        self.root = root
        self.root.title("NeuroNap")
        self.root.geometry("800x600")
        self.root.configure(bg="#F5F6F5")
        self.user_id = None
        self.user_name = None
        try:
            self.model, self.scaler = backend.train_ml_model()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize ML model: {str(e)}")
            return

        # Initialize database
        try:
            database.init_db()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database initialization failed: {str(e)}")
            return

        # Main frame for centering
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(expand=True)

        # Sub-frames
        self.auth_frame = ttk.Frame(self.main_frame, padding=20)
        self.log_frame = ttk.Frame(self.main_frame, padding=20)
        self.result_frame = ttk.Frame(self.main_frame, padding=20)

        # Style for black button text and visibility
        self.root.style = ttk.Style()
        self.root.style.configure("TButton", font=("Arial", 12), foreground="black", padding=5)
        self.root.style.configure("TLabel", font=("Arial", 12), background="#F5F6F5")
        self.root.style.configure("TEntry", font=("Arial", 12))
        self.root.style.configure("TCombobox", font=("Arial", 12))

        self.show_auth_frame()

    def center_frame(self, frame):
        # Center a frame in the window
        frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

    def show_auth_frame(self):
        # Display login/registration screen
        self.clear_frames()
        self.center_frame(self.auth_frame)
        ttk.Label(self.auth_frame, text="Welcome to NeuroNap", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(self.auth_frame, text="Name:").grid(row=1, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(self.auth_frame)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(self.auth_frame, text="Email:").grid(row=2, column=0, padx=5, pady=5)
        self.email_entry = ttk.Entry(self.auth_frame)
        self.email_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(self.auth_frame, text="Password:").grid(row=3, column=0, padx=5, pady=5)
        self.pass_entry = ttk.Entry(self.auth_frame, show="*")
        self.pass_entry.grid(row=3, column=1, padx=5, pady=5)
        ttk.Label(self.auth_frame, text="Age (new users):").grid(row=4, column=0, padx=5, pady=5)
        self.age_entry = ttk.Entry(self.auth_frame)
        self.age_entry.grid(row=4, column=1, padx=5, pady=5)
        ttk.Button(self.auth_frame, text="Login", command=self.login).grid(row=5, column=0, pady=10)
        ttk.Button(self.auth_frame, text="Register", command=self.register).grid(row=5, column=1, pady=10)

    def show_log_frame(self):
        # Display sleep log entry screen
        self.clear_frames()
        self.center_frame(self.log_frame)
        ttk.Label(self.log_frame, text=f"Log Your Sleep, {self.user_name}", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=10)
        
        # Generate date and time options
        current_date = datetime.now()
        time_options = [f"{h:02d}:{m:02d}" for h in range(24) for m in range(0, 60, 15)]
        
        # Day, Month, Year options
        days = [f"{d:02d}" for d in range(1, 32)]
        months = [f"{m:02d}" for m in range(1, 13)]
        years = [str(y) for y in range(current_date.year - 100, current_date.year + 101)]
        
        # Sleep Date
        ttk.Label(self.log_frame, text="Sleep Date:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.sleep_day_combo = ttk.Combobox(self.log_frame, values=days, state="readonly", width=5)
        self.sleep_day_combo.grid(row=1, column=1, padx=2, pady=5)
        self.sleep_day_combo.set(current_date.strftime("%d"))
        self.sleep_month_combo = ttk.Combobox(self.log_frame, values=months, state="readonly", width=5)
        self.sleep_month_combo.grid(row=1, column=2, padx=2, pady=5)
        self.sleep_month_combo.set(current_date.strftime("%m"))
        self.sleep_year_combo = ttk.Combobox(self.log_frame, values=years, state="readonly", width=8)
        self.sleep_year_combo.grid(row=1, column=3, padx=2, pady=5)
        self.sleep_year_combo.set(current_date.strftime("%Y"))
        
        # Sleep Time
        ttk.Label(self.log_frame, text="Sleep Time (HH:MM):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.sleep_time_combo = ttk.Combobox(self.log_frame, values=time_options, state="readonly")
        self.sleep_time_combo.grid(row=2, column=1, columnspan=3, padx=5, pady=5)
        self.sleep_time_combo.set("22:00")
        
        # Wake Date
        ttk.Label(self.log_frame, text="Wake Date:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.wake_day_combo = ttk.Combobox(self.log_frame, values=days, state="readonly", width=5)
        self.wake_day_combo.grid(row=3, column=1, padx=2, pady=5)
        self.wake_day_combo.set((current_date + timedelta(days=1)).strftime("%d"))
        self.wake_month_combo = ttk.Combobox(self.log_frame, values=months, state="readonly", width=5)
        self.wake_month_combo.grid(row=3, column=2, padx=2, pady=5)
        self.wake_month_combo.set((current_date + timedelta(days=1)).strftime("%m"))
        self.wake_year_combo = ttk.Combobox(self.log_frame, values=years, state="readonly", width=8)
        self.wake_year_combo.grid(row=3, column=3, padx=2, pady=5)
        self.wake_year_combo.set((current_date + timedelta(days=1)).strftime("%Y"))
        
        # Wake Time
        ttk.Label(self.log_frame, text="Wake Time (HH:MM):").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.wake_time_combo = ttk.Combobox(self.log_frame, values=time_options, state="readonly")
        self.wake_time_combo.grid(row=4, column=1, columnspan=3, padx=5, pady=5)
        self.wake_time_combo.set("06:00")
        
        # Energy Level
        ttk.Label(self.log_frame, text="Energy Level (1-10):").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.energy_entry = ttk.Entry(self.log_frame)
        self.energy_entry.grid(row=5, column=1, columnspan=3, padx=5, pady=5)
        
        ttk.Button(self.log_frame, text="Submit", command=self.log_sleep).grid(row=6, column=0, columnspan=4, pady=10)
        ttk.Button(self.log_frame, text="Back", command=self.show_auth_frame).grid(row=7, column=0, columnspan=4, pady=5)

    def show_result_frame(self, sleep_debt, rhythm, sleep_quality, tips, avg_debt, avg_chronotype, avg_energy, logs):
        # Display sleep report with graph and suggestions
        self.clear_frames()
        self.center_frame(self.result_frame)
        ttk.Label(self.result_frame, text=f"{self.user_name}'s Sleeping Report", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        # Use input times directly (in HH:MM)
        sleep_time = self.sleep_time_combo.get()
        wake_time = self.wake_time_combo.get()
        sleep_date = f"{self.sleep_year_combo.get()}-{self.sleep_month_combo.get()}-{self.sleep_day_combo.get()}"

        # Format past logs to ensure HH:MM
        formatted_logs = []
        for s, w, e in logs:
            try:
                # If s, w are datetimes, extract HH:MM
                if isinstance(s, str) and re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", s):
                    s = datetime.strptime(s, "%Y-%m-%d %H:%M").strftime("%H:%M")
                if isinstance(w, str) and re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", w):
                    w = datetime.strptime(w, "%Y-%m-%d %H:%M").strftime("%H:%M")
                formatted_logs.append((s, w, e))
            except ValueError:
                formatted_logs.append((s, w, e))  # Use as-is if parsing fails

        # Report text
        report_text = f"Latest Sleep Log (Date: {sleep_date}):\nSleep Time: {sleep_time}\nWake Time: {wake_time}\nSleep Debt: {sleep_debt:.2f} hours\nMidpoint: {rhythm['midpoint']}\nChronotype: {rhythm['chronotype']}\nSleep Quality: {sleep_quality:.1f}/10\n\n"
        report_text += f"Average Over {len(formatted_logs)} Logs:\nAvg Sleep Debt: {avg_debt:.2f} hours\nAvg Chronotype: {avg_chronotype}\nAvg Energy: {avg_energy:.1f}/10\n\n"
        report_text += "Past Logs:\n" + "\n".join([f"Log {i+1}: Sleep {s} - Wake {w}, Energy {e}" for i, (s, w, e) in enumerate(formatted_logs)])

        # Suggestions text
        suggestions_text = "Suggestions:\n" + "\n".join(tips)

        # Left panel: Report and Suggestions
        left_frame = ttk.Frame(self.result_frame)
        left_frame.grid(row=1, column=0, padx=10, pady=10)
        report_display = tk.Text(left_frame, height=15, width=50, font=("Arial", 11), wrap="word")
        report_display.pack()
        report_display.insert(tk.END, report_text + "\n\n" + suggestions_text)
        report_display.config(state="disabled")

        # Right panel: Circadian rhythm graph
        try:
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.plot(rhythm["energy"], rhythm["hours"], color="#007BFF")
            for time, label, color in [
                (rhythm["wake_time"], "Wake", "green"), (rhythm["morning_peak"], "Peak", "red"),
                (rhythm["dip_time"], "Dip", "orange"), (rhythm["evening_peak"], "Evening", "purple"),
                (rhythm["bedtime"], "Bed", "blue")
            ]:
                h, m = map(int, time.split(":"))
                y = h + m / 60
                ax.axhline(y, color=color, linestyle="--", alpha=0.5)
                ax.text(2, y, f"{label}: {time}", color=color, fontsize=8)
            ax.set_xlabel("Energy (0-10)")
            ax.set_ylabel("Time (Hours)")
            ax.set_ylim(0, 24)
            ax.set_yticks(range(0, 25, 2))
            ax.grid(True, alpha=0.3)
            canvas = FigureCanvasTkAgg(fig, master=self.result_frame)
            canvas.draw()
            canvas.get_tk_widget().grid(row=1, column=1, padx=10, pady=10)
            plt.close(fig)
        except KeyError as e:
            messagebox.showerror("Error", f"Failed to generate graph: Missing key {str(e)} in rhythm data")

        # Buttons
        ttk.Button(self.result_frame, text="Log Another", command=self.show_log_frame).grid(row=2, column=0, pady=5)
        ttk.Button(self.result_frame, text="Save Report", command=lambda: self.save_report(report_text, suggestions_text, rhythm)).grid(row=2, column=1, pady=5)

    def clear_frames(self):
        # Hide all frames
        for frame in [self.auth_frame, self.log_frame, self.result_frame]:
            frame.grid_forget()

    def login(self):
        # Handle login with database.py
        email = self.email_entry.get()
        password = self.pass_entry.get()
        try:
            result = database.login_user(email, password)
            if result:
                self.user_id, self.user_name = result
                messagebox.showinfo("Success", f"Welcome back, {self.user_name}!")
                # Clear input fields
                self.name_entry.delete(0, tk.END)
                self.email_entry.delete(0, tk.END)
                self.pass_entry.delete(0, tk.END)
                self.age_entry.delete(0, tk.END)
                self.show_log_frame()
            else:
                messagebox.showerror("Error", "Wrong email or password.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error during login: {str(e)}")

    def register(self):
        # Handle registration with database.py
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
                # Clear input fields
                self.name_entry.delete(0, tk.END)
                self.email_entry.delete(0, tk.END)
                self.pass_entry.delete(0, tk.END)
                self.age_entry.delete(0, tk.END)
                self.show_log_frame()
            else:
                messagebox.showerror("Error", "Email already taken.")
        except ValueError:
            messagebox.showerror("Error", "Age must be a number.")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error during registration: {str(e)}")

    def log_sleep(self):
        # Process sleep log and show results
        try:
            # Get date components
            sleep_day = self.sleep_day_combo.get()
            sleep_month = self.sleep_month_combo.get()
            sleep_year = self.sleep_year_combo.get()
            wake_day = self.wake_day_combo.get()
            wake_month = self.wake_month_combo.get()
            wake_year = self.wake_year_combo.get()
            sleep_time = self.sleep_time_combo.get()
            wake_time = self.wake_time_combo.get()
            energy = self.energy_entry.get()

            # Validate inputs
            if not all([sleep_day, sleep_month, sleep_year, wake_day, wake_month, wake_year, sleep_time, wake_time]):
                raise ValueError("All date and time fields must be selected.")
            if not energy:
                raise ValueError("Energy level must be provided.")
            if not re.match(r"\d{2}:\d{2}", sleep_time) or not re.match(r"\d{2}:\d{2}", wake_time):
                raise ValueError("Time must be in HH:MM format.")
            energy = int(energy)
            if not (0 <= energy <= 10):
                raise ValueError("Energy must be between 0 and 10.")

            # Construct date strings
            sleep_date = f"{sleep_year}-{sleep_month}-{sleep_day}"
            wake_date = f"{wake_year}-{wake_month}-{wake_day}"

            # Validate date formats
            try:
                sleep_datetime = datetime.strptime(f"{sleep_date} {sleep_time}", "%Y-%m-%d %H:%M")
                wake_datetime = datetime.strptime(f"{wake_date} {wake_time}", "%Y-%m-%d %H:%M")
            except ValueError:
                raise ValueError("Invalid date format. Please ensure day, month, and year are valid.")

            # Ensure wake time is after sleep time
            if wake_datetime <= sleep_datetime:
                raise ValueError("Wake time must be after sleep time.")

            # Log sleep with full datetime strings
            database.log_sleep(self.user_id, f"{sleep_date} {sleep_time}", f"{wake_date} {wake_time}", energy)
            logs = database.get_user_sleep_logs(self.user_id)

            # Use HH:MM directly for backend calculations
            sleep_debt = backend.calculate_sleep_debt(sleep_time, wake_time)
            rhythm = backend.calculate_circadian_rhythm(sleep_time, wake_time)
            # Assume typical values for missing parameters (replace with actual data if available)
            sleep_quality = backend.predict_sleep_quality(self.model, self.scaler, 8 - sleep_debt, energy, 5)
            tips = backend.generate_recommendations(sleep_debt, rhythm["chronotype"], sleep_quality, rhythm)
            avg_debt, avg_chronotype, avg_energy = backend.analyze_sleep_logs(logs)

            self.show_result_frame(sleep_debt, rhythm, sleep_quality, tips, avg_debt, avg_chronotype, avg_energy, logs)
        except ValueError as e:
            messagebox.showerror("Error", f"Input error: {str(e)}")
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Database error: {str(e)}")
        except (TypeError, KeyError) as e:
            messagebox.showerror("Error", f"Processing error: {str(e)}")

    def save_report(self, report_text, suggestions_text, rhythm):
        # Save report as PDF in local directory with graph and FAQs
        pdf_path = f"neuronap_report_{self.user_name}.pdf"
        c = pdfcanvas.Canvas(pdf_path, pagesize=letter)
        c.setFont("Helvetica", 11)

        # Write report
        y = 750
        c.drawString(50, y, f"{self.user_name}'s Sleeping Report")
        y -= 20
        for line in report_text.split("\n"):
            c.drawString(50, y, line)
            y -= 15
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 11)
                y = 750

        # Write suggestions
        y -= 20
        c.drawString(50, y, "Suggestions")
        y -= 15
        for line in suggestions_text.split("\n")[1:]:  # Skip "Suggestions" header
            c.drawString(50, y, line)
            y -= 15
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 11)
                y = 750

        # Add graph
        c.showPage()
        try:
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.plot(rhythm["energy"], rhythm["hours"], color="#007BFF")
            for time, label, color in [
                (rhythm["wake_time"], "Wake", "green"), (rhythm["morning_peak"], "Peak", "red"),
                (rhythm["dip_time"], "Dip", "orange"), (rhythm["evening_peak"], "Evening", "purple"),
                (rhythm["bedtime"], "Bed", "blue")
            ]:
                h, m = map(int, time.split(":"))
                y_val = h + m / 60
                ax.axhline(y_val, color=color, linestyle="--", alpha=0.5)
                ax.text(2, y_val, f"{label}: {time}", color=color, fontsize=8)
            ax.set_xlabel("Energy (0-10)")
            ax.set_ylabel("Time (Hours)")
            ax.set_ylim(0, 24)
            ax.set_yticks(range(0, 25, 2))
            ax.grid(True, alpha=0.3)
            # Use unique temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                temp_graph = tmp.name
            fig.savefig(temp_graph, bbox_inches="tight")
            plt.close(fig)
            c.drawImage(temp_graph, 50, 400, width=400, height=300)
            os.remove(temp_graph)
        except (KeyError, OSError) as e:
            messagebox.showerror("Error", f"Failed to generate PDF graph: {str(e)}")
            c.save()
            return

        # Add FAQs
        c.showPage()
        y = 750
        c.drawString(50, y, "Frequently Asked Questions")
        y -= 20
        faq_text = """Sleep and Immune Function: Sleep boosts your immune system big time. Studies say missing 7 hours in a week makes you way more likely to catch a cold!
How do Sleep Need and Sleep Debt work? Everyone needs 7-9 hours usually. Sleep debt is what you owe your body over 2 weeks—keep it under 5 hours to feel great.
Circadian Rhythm: Your energy goes up and down daily—peaks in the morning and evening, dips midday. It’s tied to your sleep habits and body clock.
Alcohol and Sleep: Booze might help you nod off, but it messes with deep sleep. Skip it 3-4 hours before bed.
Naps: A quick nap (15-25 min) during your dip can recharge you without ruining night sleep.
How do I change my sleep schedule? Use bright light in the morning, cut caffeine 10 hours before bed, and keep a cozy sleep space."""
        for line in faq_text.split("\n"):
            c.drawString(50, y, line)
            y -= 15
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 11)
                y = 750
        c.save()
        messagebox.showinfo("Success", f"Report saved as {pdf_path}")

def run_app():
    # Launch the application
    try:
        root = tk.Tk()
        app = NeuroNapApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Application failed to start: {str(e)}")

if __name__ == "__main__":
    run_app()