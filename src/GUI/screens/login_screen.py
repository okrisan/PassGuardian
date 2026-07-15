# src/GUI/screens/login_screen.py
import customtkinter as ctk
from GUI import theme
import ENGINE.auth as auth


class LoginScreen(ctk.CTkFrame):
    """Schermata di login. Chiama on_success(username, role) se le credenziali sono valide."""

    def __init__(self, master, on_success):
        super().__init__(master, fg_color=theme.BG_BASE)
        self.on_success = on_success
        self._password_visible = False

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(
            self,
            fg_color=theme.BG_SURFACE,
            corner_radius=16,
            border_width=1,
            border_color=theme.PURPLE_DEEP,
            width=420,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        content = ctk.CTkFrame(card, fg_color=theme.TRANSPARENT)
        content.pack(padx=48, pady=44)

        # Barra neon in cima al card
        accent_bar = ctk.CTkFrame(content, fg_color=theme.MAGENTA_NEON, height=3, width=64, corner_radius=2)
        accent_bar.pack(pady=(0, 18))

        ctk.CTkLabel(
            content, text="PASS\u2589GUARDIAN",
            font=theme.font_display(size=26),
            text_color=theme.PURPLE_GLOW,
        ).pack()

        ctk.CTkLabel(
            content, text="Accesso al vault protetto",
            font=theme.font_body(size=12),
            text_color=theme.TEXT_SECONDARY,
        ).pack(pady=(2, 26))

        ctk.CTkLabel(content, text="USERNAME", font=theme.font_mono(size=10),
                     text_color=theme.GRAY_MUTED, anchor="w").pack(fill="x")
        self.username_entry = ctk.CTkEntry(
            content, width=300, height=38, placeholder_text="es. admin",
            **theme.entry_kwargs(),
        )
        self.username_entry.pack(pady=(4, 16))
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())

        ctk.CTkLabel(content, text="MASTER PASSWORD", font=theme.font_mono(size=10),
                     text_color=theme.GRAY_MUTED, anchor="w").pack(fill="x")

        pwd_row = ctk.CTkFrame(content, fg_color=theme.TRANSPARENT)
        pwd_row.pack(pady=(4, 6), fill="x")

        self.password_entry = ctk.CTkEntry(
            pwd_row, width=250, height=38, show="\u2022", placeholder_text="\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022",
            **theme.entry_kwargs(),
        )
        self.password_entry.pack(side="left")
        self.password_entry.bind("<Return>", lambda e: self._attempt_login())

        self.toggle_btn = ctk.CTkButton(
            pwd_row, text="\U0001F441", width=38, height=38,
            command=self._toggle_password, **theme.button_secondary_kwargs(),
        )
        self.toggle_btn.pack(side="left", padx=(8, 0))

        self.error_label = ctk.CTkLabel(
            content, text="", font=theme.font_body(size=11),
            text_color=theme.DANGER, wraplength=300, justify="left",
        )
        self.error_label.pack(pady=(4, 6), fill="x")

        self.login_button = ctk.CTkButton(
            content, text="ACCEDI AL VAULT", width=300, height=42,
            command=self._attempt_login, **theme.button_primary_kwargs(),
        )
        self.login_button.pack(pady=(14, 0))

        ctk.CTkLabel(
            content, text="Connessione cifrata locale \u2022 SHA-256 / Fernet",
            font=theme.font_mono(size=9), text_color=theme.TEXT_DISABLED,
        ).pack(pady=(18, 0))

        self.username_entry.focus()

    def _toggle_password(self):
        self._password_visible = not self._password_visible
        self.password_entry.configure(show="" if self._password_visible else "\u2022")

    def _attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            self._show_error("Inserisci username e master password.")
            return

        self.login_button.configure(state="disabled", text="VERIFICA IN CORSO...")
        self.update_idletasks()

        ruolo = auth.verifica_login(username, password)

        self.login_button.configure(state="normal", text="ACCEDI AL VAULT")

        if ruolo:
            self.on_success(username, ruolo)
        else:
            self._show_error("\u274c Credenziali errate o utente inesistente.")
            self.password_entry.delete(0, "end")

    def _show_error(self, message):
        self.error_label.configure(text=message)
