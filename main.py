import tkinter as tk
from ui.login_screen import LoginScreen


def start_app():
    root = tk.Tk()

    def on_login_success(user, session):
        from ui.dashboard import Dashboard
        for widget in root.winfo_children():
            widget.destroy()
        Dashboard(root, user, session, on_logout=lambda: restart_login(root))

    def restart_login(root):
        for widget in root.winfo_children():
            widget.destroy()
        LoginScreen(root, on_login_success)

    LoginScreen(root, on_login_success)
    root.mainloop()


if __name__ == "__main__":
    start_app()