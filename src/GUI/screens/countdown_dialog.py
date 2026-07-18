import customtkinter as ctk
from GUI import theme

class CountdownDialog(ctk.CTkToplevel):
    def __init__(self, parent, secondi=3, callback_successo=None):
        super().__init__(parent)
        self.callback_successo = callback_successo
        self.secondi_rimanenti = secondi
        self.running = True

        # Configurazione finestra fluttuante sempre in primo piano
        self.title("⚡ Autofill Pronto")
        self.geometry("320x160")
        self.resizable(False, False)
        self.configure(fg_color=theme.BG_BASE)
        self.attributes("-topmost", True)  # Sempre sopra le altre finestre
        self.grab_set()

        # Label informativa
        self.info_label = ctk.CTkLabel(
            self, 
            text="Seleziona il campo di input attivo!", 
            font=theme.font_body(13), 
            text_color=theme.TEXT_PRIMARY
        )
        self.info_label.pack(pady=(15, 5))

        # Numero del Countdown
        self.timer_label = ctk.CTkLabel(
            self, 
            text=f"{self.secondi_rimanenti}s", 
            font=theme.font_title(28), 
            text_color=theme.MAGENTA_NEON
        )
        self.timer_label.pack(pady=5)

        # Frame Bottoni
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=(10, 15))

        # Bottone Annulla
        self.btn_cancel = ctk.CTkButton(
            self.btn_frame, text="Annulla", width=90, 
            command=self._annulla, **theme.button_secondary_kwargs()
        )
        self.btn_cancel.grid(row=0, column=0, padx=5)

        # Bottone Estendi (+5 secondi)
        self.btn_extend = ctk.CTkButton(
            self.btn_frame, text="⏳ +5s", width=90, 
            command=self._estendi_tempo, **theme.button_primary_kwargs()
        )
        self.btn_extend.grid(row=0, column=1, padx=5)

        # Avvia il ciclo del countdown
        self._aggiorna_countdown()

    def _aggiorna_countdown(self):
        if not self.running:
            return

        if self.secondi_rimanenti > 0:
            # CORRETTO: rimosso il typo 'secondi_rimanents'
            self.timer_label.configure(
                text=f"{self.secondi_rimanenti:.1f}s" if self.secondi_rimanenti < 2 else f"{int(self.secondi_rimanenti)}s"
            )
            # Scaliamo di 0.1 secondi alla volta
            self.secondi_rimanenti -= 0.1
            self.after(100, self._aggiorna_countdown)
        else:
            self.running = False
            self.destroy()
            if self.callback_successo:
                self.callback_successo()

    def _estendi_tempo(self):
        """Aggiunge 5 secondi al contatore corrente."""
        self.secondi_rimanenti += 5.0
        print(f"[TIMER] Tempo esteso! Nuova scadenza: {int(self.secondi_rimanenti)}s")

    def _annulla(self):
        """Interrompe l'operazione prima dell'invio dei dati."""
        self.running = False
        print("[TIMER] Operazione Smart Autofill annullata dall'utente.")
        self.destroy()