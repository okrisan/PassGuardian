# src/GUI/screens/security_view.py
import customtkinter as ctk
from GUI import theme
import ENGINE.auth as auth


class SecurityView(ctk.CTkFrame):
    """Permette all'utente loggato di cambiare la propria master password."""

    def __init__(self, master, username):
        super().__init__(master, fg_color=theme.BG_BASE)
        self.username = username

        header = ctk.CTkFrame(self, fg_color=theme.TRANSPARENT)
        header.pack(fill="x", padx=28, pady=(24, 10))
        ctk.CTkLabel(header, text="SICUREZZA ACCOUNT", font=theme.font_title(size=22),
                     text_color=theme.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(header, text="Aggiorna la master password usata per accedere al vault",
                     font=theme.font_body(size=12), text_color=theme.TEXT_SECONDARY).pack(anchor="w", pady=(2, 0))

        card = ctk.CTkFrame(self, **theme.frame_card_kwargs())
        card.pack(padx=28, pady=10, fill="x")

        body = ctk.CTkFrame(card, fg_color=theme.TRANSPARENT)
        body.pack(padx=32, pady=28, fill="x")

        ctk.CTkLabel(body, text="\U0001F511 CAMBIO MASTER PASSWORD", font=theme.font_title(size=14),
                     text_color=theme.PURPLE_GLOW).pack(anchor="w", pady=(0, 18))

        self.current_entry = self._field(body, "PASSWORD ATTUALE")
        self.new_entry = self._field(body, "NUOVA MASTER PASSWORD")
        self.confirm_entry = self._field(body, "CONFERMA NUOVA PASSWORD")

        self.strength_label = ctk.CTkLabel(body, text="", font=theme.font_mono(size=11),
                                            text_color=theme.TEXT_SECONDARY)
        self.strength_label.pack(anchor="w", pady=(0, 6))
        self.new_entry.bind("<KeyRelease>", lambda e: self._update_strength())

        self.feedback_label = ctk.CTkLabel(body, text="", font=theme.font_body(size=12),
                                            wraplength=420, justify="left")
        self.feedback_label.pack(anchor="w", pady=(6, 6))

        ctk.CTkButton(
            body, text="Aggiorna Master Password", height=40, width=260,
            command=self._submit, **theme.button_primary_kwargs(),
        ).pack(anchor="w", pady=(10, 0))

        tip_card = ctk.CTkFrame(self, fg_color=theme.TRANSPARENT)
        tip_card.pack(padx=28, pady=(4, 10), fill="x")
        ctk.CTkLabel(
            tip_card,
            text="\u2139 Suggerimento: usa almeno 8 caratteri, mischiando lettere, numeri e simboli.",
            font=theme.font_body(size=11), text_color=theme.GRAY_MUTED,
        ).pack(anchor="w")

    def _field(self, parent, label):
        ctk.CTkLabel(parent, text=label, font=theme.font_mono(size=10),
                     text_color=theme.GRAY_MUTED, anchor="w").pack(fill="x")
        entry = ctk.CTkEntry(parent, height=38, show="\u2022", width=340, **theme.entry_kwargs())
        entry.pack(anchor="w", pady=(4, 14))
        return entry

    def _update_strength(self):
        pwd = self.new_entry.get()
        if not pwd:
            self.strength_label.configure(text="")
            return
        score = 0
        if len(pwd) >= 8:
            score += 1
        if any(c.isdigit() for c in pwd):
            score += 1
        if any(c.isupper() for c in pwd) and any(c.islower() for c in pwd):
            score += 1
        if any(not c.isalnum() for c in pwd):
            score += 1

        levels = {
            0: ("DEBOLE", theme.DANGER),
            1: ("DEBOLE", theme.DANGER),
            2: ("MEDIA", theme.WARNING),
            3: ("BUONA", theme.INFO),
            4: ("ECCELLENTE", theme.SUCCESS),
        }
        label, color = levels[score]
        self.strength_label.configure(text=f"Robustezza: {label}", text_color=color)

    def _submit(self):
        current = self.current_entry.get()
        new_pwd = self.new_entry.get()
        confirm = self.confirm_entry.get()

        if not current or not new_pwd or not confirm:
            self._feedback("Compila tutti i campi.", theme.DANGER)
            return

        if not auth.verifica_login(self.username, current):
            self._feedback("\u274c La password attuale non e' corretta.", theme.DANGER)
            return

        if new_pwd != confirm:
            self._feedback("\u274c Le nuove password non coincidono.", theme.DANGER)
            return

        if len(new_pwd) < 8:
            self._feedback("\u26A0 La password deve avere almeno 8 caratteri.", theme.WARNING)
            return

        if auth.aggiorna_password_utente(self.username, new_pwd):
            self._feedback("\u2705 Master Password aggiornata con successo!", theme.SUCCESS)
            self.current_entry.delete(0, "end")
            self.new_entry.delete(0, "end")
            self.confirm_entry.delete(0, "end")
            self.strength_label.configure(text="")
        else:
            self._feedback("\u274c Errore durante il salvataggio.", theme.DANGER)

    def _feedback(self, text, color):
        self.feedback_label.configure(text=text, text_color=color)
