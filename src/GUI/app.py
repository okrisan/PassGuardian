# src/GUI/app.py
import customtkinter as ctk

from GUI import theme
from GUI.screens.splash_screen import SplashScreen
from GUI.screens.login_screen import LoginScreen
from GUI.screens.dashboard import Dashboard


class PassGuardianApp(ctk.CTk):
    """Finestra principale: gestisce il passaggio Splash -> Login -> Dashboard."""

    def __init__(self, vault):
        super().__init__()
        self.vault = vault
        self.username = None
        self.role = None
        self._current_frame = None

        self.title("PassGuardian // Secure Vault")
        self.geometry("1360x780")
        self.minsize(1180, 680)
        self.configure(fg_color=theme.BG_BASE)

        try:
            self.iconbitmap(default="")
        except Exception:
            pass

        self.container = ctk.CTkFrame(self, fg_color=theme.BG_BASE, corner_radius=0)
        self.container.pack(fill="both", expand=True)

        self.show_splash()

    # ------------------------------------------------------------------
    def _switch(self, frame):
        if self._current_frame is not None:
            self._current_frame.destroy()
        self._current_frame = frame
        frame.pack(fill="both", expand=True)

    def show_splash(self):
        self._switch(SplashScreen(self.container, on_done=self.show_login))

    def show_login(self):
        self._switch(LoginScreen(self.container, on_success=self._handle_login))

    def _handle_login(self, username, role):
        self.username = username
        self.role = role
        self.show_dashboard()

    def show_dashboard(self):
        self._switch(Dashboard(self.container, app=self))

    def logout(self):
        self.username = None
        self.role = None
        self.show_login()


def run():
    """Entry point della GUI: inizializza il tema, il vault e avvia il mainloop."""
    # Import locali per evitare side-effect all'import del pacchetto GUI
    from ENGINE.vault import LocalJsonVault
    import ENGINE.auth  # noqa: F401  (inizializza users.json di default se assente)

    theme.apply_global_theme()
    vault = LocalJsonVault()
    app = PassGuardianApp(vault)
    app.mainloop()
