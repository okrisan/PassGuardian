import customtkinter as ctk
from GUI import theme
from ENGINE.phishing import verifica_antiphishing_url

class CheckPhishingDialog(ctk.CTkToplevel):
    def __init__(self, parent, credenziali_caricate, callback_autofill=None):
        super().__init__(parent)
        self.credenziali_caricate = credenziali_caricate
        self.callback_autofill = callback_autofill

        self.title("🛡️ Verifica Anti-Phishing URL")
        self.geometry("500x300")
        self.resizable(False, False)
        self.configure(fg_color=theme.BG_BASE)
        self.attributes("-topmost", True)
        self.grab_set()

        # Input URL
        self.label = ctk.CTkLabel(self, text="Incolla l'URL della pagina di login:", font=theme.font_body(14))
        self.label.pack(pady=(20, 5))

        self.url_entry = ctk.CTkEntry(self, placeholder_text="https://example.com/login", width=400, height=40)
        self.url_entry.pack(pady=10)

        # Pulsante di controllo
        self.btn_check = ctk.CTkButton(self, text="Verifica URL", command=self._analizza_url, **theme.button_primary_kwargs())
        self.btn_check.pack(pady=10)

        # Area dei risultati
        self.result_frame = ctk.CTkFrame(self, fg_color="transparent", height=100)
        self.result_frame.pack(fill="x", padx=20, pady=10)
        
        self.result_label = ctk.CTkLabel(self.result_frame, text="", font=theme.font_body(13), wraplength=450)
        self.result_label.pack(pady=5)
        
        self.btn_action = ctk.CTkButton(self.result_frame, text="", width=180) # Apparirà dinamicamente

    def _analizza_url(self):
        url = self.url_entry.get().strip()
        if not url:
            self.result_label.configure(text="Inserisci un URL valido per il controllo.", text_color=theme.TEXT_PRIMARY)
            self.btn_action.pack_forget()
            return

        esito, entry = verifica_antiphishing_url(url, self.credenziali_caricate)

        if esito == "OK":
            self.result_label.configure(
                text=f"✅ URL Sicuro! Corrisponde alla tua credenziale per:\nNome: {entry.titolo} | User: {entry.username}",
                text_color="#00FF88" # Neon Green
            )
            # Mostra il bottone per lanciare subito l'autofill su questa credenziale sicura
            if self.callback_autofill:
                self.btn_action.configure(
                    text="⚡ Avvia Autofill",
                    command=lambda: [self.destroy(), self.callback_autofill(entry)],
                    fg_color=theme.MAGENTA_NEON
                )
                self.btn_action.pack(pady=5)

        elif esito == "PHISHING":
            self.result_label.configure(
                text=f"🚨 ATTENZIONE: POSSIBILE PHISHING!\nL'URL inserito è ingannevole ed è molto simile alla tua credenziale reale '{entry.url}'. Non inserire dati su questo sito!",
                text_color=theme.DANGER
            )
            self.btn_action.pack_forget()

        elif esito == "NON_TROVATO":
            self.result_label.configure(
                text="ℹ️ Nessuna credenziale trovata nel vault per questo URL.\nSe è un sito nuovo, puoi registrarlo tranquillamente.",
                text_color=theme.TEXT_PRIMARY
            )
            self.btn_action.pack_forget()