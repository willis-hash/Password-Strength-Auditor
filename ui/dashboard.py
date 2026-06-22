import tkinter as tk
from tkinter import messagebox
import threading
from auth.logout import logout_session
from auditor.scoring_engine import full_audit


class Dashboard(tk.Frame):
    def __init__(self, master, user, session, on_logout):
        super().__init__(master)
        self.master = master
        self.user = user
        self.session = session
        self.on_logout = on_logout

        self.master.title("Password Auditor - Dashboard")
        self.master.geometry("600x550")

        tk.Label(
            self, text=f"Welcome, {user['username']}!", font=("Arial", 16, "bold")
        ).pack(pady=15)

        tk.Label(
            self, text="Password Strength Auditing System", font=("Arial", 11)
        ).pack(pady=2)

        # Password input
        tk.Label(self, text="Enter a password to audit:", font=("Arial", 11)).pack(pady=(20, 5))
        self.password_entry = tk.Entry(self, width=35, font=("Arial", 12), show="*")
        self.password_entry.pack(pady=5)

        self.show_var = tk.BooleanVar()
        tk.Checkbutton(
            self, text="Show password", variable=self.show_var, command=self.toggle_show
        ).pack()

        self.analyze_btn = tk.Button(
            self, text="Analyze Password", width=20, command=self.handle_analyze
        )
        self.analyze_btn.pack(pady=15)

        self.status_label = tk.Label(self, text="", font=("Arial", 10, "italic"), fg="gray")
        self.status_label.pack()

        # Results area
        self.results_frame = tk.Frame(self, bd=2, relief="groove")
        self.results_frame.pack(pady=15, padx=20, fill="both", expand=True)

        self.result_title = tk.Label(self.results_frame, text="", font=("Arial", 14, "bold"))
        self.result_title.pack(pady=10)

        self.result_text = tk.Text(self.results_frame, height=12, width=60, wrap="word", state="disabled")
        self.result_text.pack(padx=10, pady=5)

        tk.Button(
            self, text="Logout", width=20, command=self.handle_logout
        ).pack(pady=10)

        self.pack(fill="both", expand=True)

    def toggle_show(self):
        self.password_entry.config(show="" if self.show_var.get() else "*")

    def handle_analyze(self):
        password = self.password_entry.get().strip()
        if not password:
            messagebox.showerror("Error", "Please enter a password to audit.")
            return

        self.analyze_btn.config(state="disabled")
        self.status_label.config(text="Analyzing... this may take a few seconds (running dictionary attack)")
        self.update_idletasks()

        # Run in background thread so the GUI doesn't freeze
        thread = threading.Thread(target=self.run_audit, args=(password,))
        thread.start()

    def run_audit(self, password):
        result = full_audit(password)
        self.after(0, self.display_results, result)

    def display_results(self, result):
        self.analyze_btn.config(state="normal")
        self.status_label.config(text="Analysis complete.")

        color_map = {
            "Weak": "red",
            "Vulnerable": "red",
            "Moderate": "orange",
            "Strong": "green",
        }
        label = result["final_label"]
        color = color_map.get(label, "black")

        self.result_title.config(text=f"Result: {label}", fg=color)

        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")

        self.result_text.insert("end", f"Password length: {result['password_length']}\n")
        self.result_text.insert("end", f"Rule-based score: {result['rule_score']} ({result['rule_label']})\n")
        self.result_text.insert("end", f"Cracked by John the Ripper: {'Yes' if result['cracked_by_jtr'] else 'No'}\n\n")
        self.result_text.insert("end", "Recommendations:\n")
        for rec in result["recommendations"]:
            self.result_text.insert("end", f"  • {rec}\n")

        self.result_text.config(state="disabled")

    def handle_logout(self):
        logout_session(self.session["token"])
        self.destroy()
        self.on_logout()