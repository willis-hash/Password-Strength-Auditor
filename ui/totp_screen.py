import tkinter as tk
from tkinter import messagebox
from auth.totp import verify_totp_code
from auth.logout import create_session


class TotpScreen(tk.Frame):
    def __init__(self, master, user, on_login_success):
        super().__init__(master)
        self.master = master
        self.user = user
        self.on_login_success = on_login_success

        self.master.title("Password Auditor - 2FA Verification")
        self.master.geometry("400x250")

        tk.Label(self, text="Two-Factor Authentication", font=("Arial", 16, "bold")).pack(pady=20)
        tk.Label(self, text="Enter the 6-digit code from your authenticator app").pack(pady=5)

        self.code_entry = tk.Entry(self, width=20, justify="center", font=("Arial", 14))
        self.code_entry.pack(pady=10)

        tk.Button(self, text="Verify", width=20, command=self.handle_verify).pack(pady=20)

        self.pack(fill="both", expand=True)

    def handle_verify(self):
        code = self.code_entry.get().strip()

        if not code:
            messagebox.showerror("Error", "Please enter the 6-digit code.")
            return

        if verify_totp_code(self.user["totp_secret"], code):
            session = create_session(self.user["id"])
            self.destroy()
            self.on_login_success(self.user, session)
        else:
            messagebox.showerror("Invalid Code", "The code you entered is incorrect.")