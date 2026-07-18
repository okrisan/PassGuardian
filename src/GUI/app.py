# src/GUI/app.py
import customtkinter as ctk

from GUI import theme
from GUI.screens.splash_screen import SplashScreen
from GUI.screens.login_screen import LoginScreen
from GUI.screens.registration_screen import RegistrationScreen # Importiamo il nuovo oggetto
from GUI.screens.dashboard import Dashboard

from ENGINE.storage import VaultStorage 


class PassGuardianApp(ctk.CTk):
    """Finestra principale: gestisce il flusso di navigazione ad oggetti."""

    def __init__(self, storage: VaultStorage):
        super().__init__()
        self.storage = storage
        
        self.username = None
        self.master_password = None  
        self.role = None
        
        self._current_frame = None

        self.title("PassGuardian // Secure Vault polimorfico")
        self.geometry("1024x600")
        self.minsize(1180, 680)
        self.configure(fg_color=theme.BG_BASE)

        try:
            self.iconbitmap(default="")
        except Exception:
            pass

        self.container = ctk.CTkFrame(self, fg_color=theme.BG_BASE, corner_radius=0)
        self.container.pack(fill="both", expand=True)

        self.show_splash()

    def _switch(self, frame):
        if self._current_frame is not None:
            self._current_frame.destroy()
        self._current_frame = frame
        frame.pack(fill="both", expand=True)

    def show_splash(self):
        self._switch(SplashScreen(self.container, on_done=self.show_login))

    def show_login(self, messaggio_iniziale=None):
        """Mostra la schermata di login passandole i callback di navigazione e successo."""
        schermata_login = LoginScreen(
            self.container, 
            on_success=self._handle_login,
            on_navigate_to_register=self.show_registration
        )
        
        if messaggio_iniziale:
            schermata_login.imposta_messaggio(messaggio_iniziale, theme.SUCCESS)
            
        self._switch(schermata_login)

    def show_registration(self):
        """Passa alla schermata di registrazione, slegata dal login."""
        self._switch(
            RegistrationScreen(
                self.container,
                on_back=self.show_login,
                on_register_success=self._handle_registration_success
            )
        )

    def _handle_registration_success(self, username_creato):
        """Invocato quando un nuovo utente viene salvato correttamente."""
        messaggio = f"Agente '{username_creato}' registrato! Effettua il login."
        self.show_login(messaggio_iniziale=messaggio)

    def _handle_login(self, username, role, master_password):
        self.username = username
        self.role = role
        self.master_password = master_password  
        self.show_dashboard()

    def show_dashboard(self):
        self._switch(Dashboard(self.container, app=self))

    def logout(self):
        self.username = None
        self.role = None
        self.master_password = None
        self.show_login()


def run():
    theme.apply_global_theme()
    storage = VaultStorage("DATABASE/vault.json") 
    app = PassGuardianApp(storage)
    app.mainloop()