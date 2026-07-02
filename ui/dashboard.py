import tkinter as tk
from tkinter import messagebox
import threading
from auth.logout import logout_session
from auditor.scoring_engine import full_audit

# ── Colour palette ──
BG = "#1e1e2e"
PANEL = "#2a2a3e"
ACCENT = "#7c3aed"
ACCENT2 = "#a78bfa"
TEXT = "#e2e8f0"
SUBTEXT = "#94a3b8"
RED = "#f87171"
ORANGE = "#fb923c"
GREEN = "#4ade80"
WHITE = "#ffffff"


class Dashboard(tk.Frame):
    def __init__(self, master, user, session, on_logout):
        super().__init__(master, bg=BG)
        self.master = master
        self.user = user
        self.session = session
        self.on_logout = on_logout

        self.master.title("Password Auditor - Dashboard")
        self.master.geometry("700x720")
        self.master.configure(bg=BG)
        self.master.resizable(True, True)

        # Remove default icon
        try:
            import os
            icon_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "assets", "app_icon.ico"
            )
            if os.path.exists(icon_path):
                self.master.iconbitmap(icon_path)
        except Exception:
            pass

        self._build_ui()
        self.pack(fill="both", expand=True)

    def _build_ui(self):
        # ── Header ──
        header = tk.Frame(self, bg=ACCENT, pady=12)
        header.pack(fill="x")

        tk.Label(
            header, text="🔐  Password Strength Auditing System",
            font=("Arial", 16, "bold"), bg=ACCENT, fg=WHITE
        ).pack()

        tk.Label(
            header, text=f"Logged in as: {self.user['username']}",
            font=("Arial", 10), bg=ACCENT, fg=ACCENT2
        ).pack()

        # ── Input Section ──
        input_frame = tk.Frame(self, bg=BG, pady=20)
        input_frame.pack(fill="x", padx=40)

        tk.Label(
            input_frame, text="Enter a password to audit:",
            font=("Arial", 12), bg=BG, fg=TEXT
        ).pack(anchor="w")

        entry_frame = tk.Frame(
            input_frame, bg=PANEL, bd=0,
            highlightthickness=2, highlightbackground=ACCENT
        )
        entry_frame.pack(fill="x", pady=(5, 0))

        self.password_entry = tk.Entry(
            entry_frame, font=("Arial", 13), show="*",
            bg=PANEL, fg=WHITE, insertbackground=WHITE,
            relief="flat", bd=8
        )
        self.password_entry.pack(fill="x")

        # Show/hide checkbox
        self.show_var = tk.BooleanVar()
        tk.Checkbutton(
            input_frame, text="Show password", variable=self.show_var,
            command=self.toggle_show, bg=BG, fg=SUBTEXT,
            selectcolor=PANEL, activebackground=BG,
            activeforeground=TEXT, font=("Arial", 10)
        ).pack(anchor="w", pady=(5, 0))

        # Analyze button
        self.analyze_btn = tk.Button(
            input_frame, text="Analyze Password",
            font=("Arial", 12, "bold"), bg=ACCENT, fg=WHITE,
            activebackground=ACCENT2, activeforeground=WHITE,
            relief="flat", bd=0, padx=20, pady=8,
            cursor="hand2", command=self.handle_analyze
        )
        self.analyze_btn.pack(pady=(15, 0))

        # Status label
        self.status_label = tk.Label(
            input_frame, text="",
            font=("Arial", 10, "italic"), bg=BG, fg=SUBTEXT
        )
        self.status_label.pack(pady=(5, 0))

        # ── Results Panel ──
        results_outer = tk.Frame(
            self, bg=PANEL, bd=0,
            highlightthickness=1, highlightbackground=ACCENT
        )
        results_outer.pack(fill="both", expand=True, padx=40, pady=(0, 10))

        # Classification label
        self.result_title = tk.Label(
            results_outer, text="Results will appear here",
            font=("Arial", 15, "bold"), bg=PANEL, fg=SUBTEXT, pady=10
        )
        self.result_title.pack()

        # Stats row
        stats_frame = tk.Frame(results_outer, bg=PANEL)
        stats_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.score_label = tk.Label(
            stats_frame, text="Score: —",
            font=("Arial", 10), bg=PANEL, fg=SUBTEXT
        )
        self.score_label.pack(side="left", padx=10)

        self.crack_time_label = tk.Label(
            stats_frame, text="Time to Crack: —",
            font=("Arial", 10), bg=PANEL, fg=SUBTEXT
        )
        self.crack_time_label.pack(side="left", padx=10)

        self.jtr_label = tk.Label(
            stats_frame, text="JtR Attack: —",
            font=("Arial", 10), bg=PANEL, fg=SUBTEXT
        )
        self.jtr_label.pack(side="left", padx=10)

        # Divider
        tk.Frame(results_outer, bg=ACCENT, height=1).pack(fill="x", padx=20)

        # Recommendations text
        self.result_text = tk.Text(
            results_outer, font=("Arial", 11), bg=PANEL, fg=TEXT,
            relief="flat", bd=10, wrap="word", state="disabled",
            height=10, insertbackground=WHITE
        )
        self.result_text.pack(fill="both", expand=True, padx=10, pady=10)

        # ── Footer ──
        footer = tk.Frame(self, bg=BG, pady=10)
        footer.pack(fill="x")

        tk.Button(
            footer, text="Logout",
            font=("Arial", 11), bg=PANEL, fg=RED,
            activebackground=RED, activeforeground=WHITE,
            relief="flat", bd=0, padx=20, pady=6,
            cursor="hand2", command=self.handle_logout
        ).pack()

    def toggle_show(self):
        self.password_entry.config(show="" if self.show_var.get() else "*")

    def handle_analyze(self):
        password = self.password_entry.get().strip()
        if not password:
            messagebox.showerror("Error", "Please enter a password to audit.")
            return

        self.analyze_btn.config(state="disabled")
        self.status_label.config(
            text="Analyzing... please wait (running dictionary attack)"
        )
        self.result_title.config(text="Analyzing...", fg=SUBTEXT)
        self.update_idletasks()

        thread = threading.Thread(target=self.run_audit, args=(password,))
        thread.start()

    def run_audit(self, password):
        result = full_audit(password)
        self.after(0, self.display_results, result)

    def display_results(self, result):
        self.analyze_btn.config(state="normal")
        self.status_label.config(text="Analysis complete.")

        color_map = {
            "Weak": RED,
            "Vulnerable": RED,
            "Moderate": ORANGE,
            "Strong": GREEN,
        }
        label = result["final_label"]
        color = color_map.get(label, WHITE)

        self.result_title.config(text=f"Classification:  {label}", fg=color)

        self.score_label.config(
            text=f"Rule Score: {result['rule_score']}/6", fg=ACCENT2
        )

        # Crack time from JtR
        crack_time = result.get("crack_time")
        if crack_time and result["cracked_by_jtr"]:
            self.crack_time_label.config(
                text=f"Time to Crack: {crack_time}", fg=ACCENT2
            )
        elif result["cracked_by_jtr"]:
            self.crack_time_label.config(
                text="Time to Crack: < 1 second", fg=ACCENT2
            )
        else:
            self.crack_time_label.config(
                text="Time to Crack: N/A (not cracked)", fg=SUBTEXT
            )

        self.jtr_label.config(
            text=f"JtR Cracked: {'Yes ⚠' if result['cracked_by_jtr'] else 'No ✓'}",
            fg=RED if result['cracked_by_jtr'] else GREEN
        )

        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.insert("end", "Recommendations:\n\n")
        for rec in result["recommendations"]:
            self.result_text.insert("end", f"  •  {rec}\n\n")
        self.result_text.config(state="disabled")

    def handle_logout(self):
        logout_session(self.session["token"])
        self.destroy()
        self.on_logout()