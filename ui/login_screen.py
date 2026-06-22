import tkinter as tk
from tkinter import messagebox
from auth.login import authenticate_user
from auth.logout import create_session


class LoginScreen(tk.Frame):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.master = master
        self.on_login_success = on_login_success  # callback(user, session)

        self.master.title("Password Auditor - Login")
        self.master.geometry("400x300")

        tk.Label(self, text="Login", font=("Arial", 18, "bold")).pack(pady=20)

        tk.Label(self, text="Username").pack(anchor="w", padx=40)
        self.username_entry = tk.Entry(self, width=30)
        self.username_entry.pack(padx=40, pady=5)

        tk.Label(self, text="Password").pack(anchor="w", padx=40)
        self.password_entry = tk.Entry(self, width=30, show="*")
        self.password_entry.pack(padx=40, pady=5)

        tk.Button(
            self, text="Login", width=20, command=self.handle_login
        ).pack(pady=20)

        self.pack(fill="both", expand=True)

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        success, result = authenticate_user(username, password)

        if not success:
            messagebox.showerror("Login Failed", result)
            return

        user = result

        # If 2FA is enabled, move to TOTP screen instead of logging in directly
        if user["is_2fa_enabled"]:
            from ui.totp_screen import TotpScreen
            self.destroy()
            TotpScreen(self.master, user, self.on_login_success)
        else:
            session = create_session(user["id"])
            self.destroy()
            self.on_login_success(user, session)