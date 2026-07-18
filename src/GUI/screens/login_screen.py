# src/GUI/screens/login_screen.py
import customtkinter as ctk
from GUI import theme


class LoginScreen(ctk.CTkFrame):
    """Schermata di login cyberpunk pura. Delega la registrazione all'App."""

    def __init__(self, parent, on_success, on_navigate_to_register):
        super().__init__(parent, fg_color=theme.BG_BASE)
        self.on_success = on_success
        self.on_navigate_to_register = on_navigate_to_register
        self.storage = parent.master.storage

        self.grid_rowconfigure((0, 2), weight=1)
        self.grid_columnconfigure((0, 2), weight=1)

        # Card centrale
        self.card = ctk.CTkFrame(self, **theme.frame_card_kwargs())
        self.card.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        self.card.grid_columnconfigure(0, weight=1)

        # Titolo Card
        self.title = ctk.CTkLabel(
            self.card,
            text="ACCESS GATEWAY",
            font=theme.font_title(size=22),
            text_color=theme.PURPLE_GLOW,
        )
        self.title.pack(pady=(40, 30), padx=50)

        # Campo Username
        self.username_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="Username ID",
            width=320,
            height=40,
            **theme.entry_kwargs()
        )
        self.username_entry.pack(pady=10, padx=50)

        # Campo Master Password
        self.password_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="Master Password",
            show="*",
            width=320,
            height=40,
            **theme.entry_kwargs()
        )
        self.password_entry.pack(pady=10, padx=50)

        # Messaggio di Errore
        self.error_label = ctk.CTkLabel(
            self.card,
            text="",
            font=theme.font_body(size=12),
            text_color=theme.DANGER,
        )
        self.error_label.pack(pady=(5, 10))

        # Pulsante Accedi
        self.login_btn = ctk.CTkButton(
            self.card,
            text="INITIALIZE SESSION",
            width=320,
            height=45,
            command=self._tentativo_login,
            **theme.button_primary_kwargs()
        )
        self.login_btn.pack(pady=(10, 10), padx=50)

        # Pulsante Registrati (navigazione esterna)
        self.go_to_register_btn = ctk.CTkButton(
            self.card,
            text="> REGISTER NEW AGENT",
            font=theme.font_mono(size=11),
            text_color=theme.GRAY_MUTED,
            fg_color="transparent",
            hover_color=theme.BG_SURFACE_2,
            height=30,
            command=self.on_navigate_to_register
        )
        self.go_to_register_btn.pack(pady=(5, 30))

    def imposta_messaggio(self, messaggio, colore=theme.SUCCESS):
        """Metodo utile per mostrare conferme provenienti da altre schermate."""
        self.error_label.configure(text=messaggio, text_color=colore)

    def _tentativo_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            self.error_label.configure(text="Inserisci tutte le credenziali.", text_color=theme.DANGER)
            return

        ruolo = self.storage.verifica_utente(username, password)

        if ruolo:
            self.error_label.configure(text="")
            self.on_success(username, ruolo, password)
        else:
            self.error_label.configure(text="Credenziali non valide o inesistenti.", text_color=theme.DANGER)