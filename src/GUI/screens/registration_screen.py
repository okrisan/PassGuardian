# src/GUI/screens/registration_screen.py
import customtkinter as ctk
from GUI import theme


class RegistrationScreen(ctk.CTkFrame):
    """Oggetto schermata dedicato esclusivamente alla creazione di nuovi utenti."""

    def __init__(self, parent, on_back, on_register_success):
        super().__init__(parent, fg_color=theme.BG_BASE)
        self.on_back = on_back
        self.on_register_success = on_register_success
        self.storage = parent.master.storage  # Accesso al motore di storage

        self.grid_rowconfigure((0, 2), weight=1)
        self.grid_columnconfigure((0, 2), weight=1)

        # Card di Registrazione
        self.card = ctk.CTkFrame(self, **theme.frame_card_kwargs())
        self.card.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        self.card.grid_columnconfigure(0, weight=1)

        # Titolo Card
        self.title = ctk.CTkLabel(
            self.card,
            text="REGISTER NEW AGENT",
            font=theme.font_title(size=22),
            text_color=theme.MAGENTA_NEON,
        )
        self.title.pack(pady=(35, 20), padx=50)

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

        # Campo Conferma Password
        self.confirm_password_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="Confirm Master Password",
            show="*",
            width=320,
            height=40,
            **theme.entry_kwargs()
        )
        self.confirm_password_entry.pack(pady=10, padx=50)

        # Messaggio di Feedback
        self.feedback_label = ctk.CTkLabel(
            self.card,
            text="",
            font=theme.font_body(size=12),
            text_color=theme.DANGER,
        )
        self.feedback_label.pack(pady=(5, 5))

        # Pulsante Crea Utente
        self.register_btn = ctk.CTkButton(
            self.card,
            text="CREATE SECURE PROFILE",
            width=320,
            height=45,
            command=self._esegui_registrazione,
            **theme.button_primary_kwargs()
        )
        self.register_btn.pack(pady=(10, 10), padx=50)

        # Torna al Login
        self.back_btn = ctk.CTkButton(
            self.card,
            text="< BACK TO LOGIN",
            font=theme.font_mono(size=11),
            text_color=theme.GRAY_MUTED,
            fg_color="transparent",
            hover_color=theme.BG_SURFACE_2,
            height=30,
            command=self.on_back
        )
        self.back_btn.pack(pady=(5, 30))

    def _esegui_registrazione(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not username or not password or not confirm_password:
            self._mostra_errore("Tutti i campi sono obbligatori.")
            return

        if password != confirm_password:
            self._mostra_errore("Le password non coincidono.")
            return

        if len(password) < 8:
            self._mostra_errore("La password deve avere almeno 8 caratteri.")
            return

        # Scrittura sul nostro storage reale
        successo = self.storage.registra_utente(username, password)

        if successo:
            self.on_register_success(username)
        else:
            self._mostra_errore("Username già esistente.")

    def _mostra_errore(self, messaggio):
        self.feedback_label.configure(text=messaggio, text_color=theme.DANGER)