# src/GUI/screens/credential_dialogs.py
import customtkinter as ctk
from GUI import theme

class AddWebDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_save, entry=None):
        super().__init__(parent)
        self.on_save = on_save
        self.entry = entry  # Salviamo il riferimento (se esiste, siamo in MODIFICA)
        
        self.title("EDIT WEB CREDENTIAL" if entry else "ADD WEB CREDENTIAL")
        self.geometry("450x400")
        self.resizable(False, False)
        self.configure(fg_color=theme.BG_BASE)
        self.grab_set()
        
        self.title_label = ctk.CTkLabel(
            self, text="EDIT WEB CREDENTIAL" if entry else "NEW WEB CREDENTIAL", 
            font=theme.font_title(18), text_color=theme.MAGENTA_NEON
        )
        self.title_label.pack(pady=(30, 20))

        self.service_entry = ctk.CTkEntry(self, placeholder_text="Servizio / URL", width=320, height=40, **theme.entry_kwargs())
        self.service_entry.pack(pady=10)

        self.user_entry = ctk.CTkEntry(self, placeholder_text="Username / Email", width=320, height=40, **theme.entry_kwargs())
        self.user_entry.pack(pady=10)

        self.pass_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*", width=320, height=40, **theme.entry_kwargs())
        self.pass_entry.pack(pady=10)

        # SE SIAMO IN MODIFICA: Pre-compiliamo i campi con i dati esistenti
        if self.entry:
            # Inseriamo i testi quando lo stato è ancora normale
            self.service_entry.insert(0, self.entry.titolo)
            self.user_entry.insert(0, self.entry.username)
            self.pass_entry.insert(0, self.entry.password_cifrata)
            
            # Impostiamo su "readonly": l'utente non può modificarli, ma rimangono leggibili e funzionanti!
            self.service_entry.configure(state="readonly")
            self.user_entry.configure(state="readonly")
            
            # Ci assicuriamo al 100% che la password sia editabile
            self.pass_entry.configure(state="normal")

        self.error_label = ctk.CTkLabel(self, text="", font=theme.font_body(12), text_color=theme.DANGER)
        self.error_label.pack(pady=5)

        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=(10, 20))

        self.btn_cancel = ctk.CTkButton(self.btn_frame, text="Annulla", width=100, command=self.destroy, **theme.button_secondary_kwargs())
        self.btn_cancel.grid(row=0, column=0, padx=10)

        self.btn_save = ctk.CTkButton(
            self.btn_frame, 
            text="Aggiorna" if entry else "Salva", 
            width=150, 
            command=self._save, 
            **theme.button_primary_kwargs()
        )
        self.btn_save.grid(row=0, column=1, padx=10)

    def _save(self):
        # Grazie a 'readonly', .get() ora estrarrà correttamente i valori!
        servizio = self.service_entry.get().strip()
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()

        if not servizio or not username or not password:
            self.error_label.configure(text="Tutti i campi sono obbligatori.")
            return

        # Passiamo is_modifica basandoci sulla presenza di self.entry
        self.on_save(tipo="web", servizio=servizio, username=username, password=password, is_modifica=bool(self.entry))
        self.destroy()


class AddSshDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_save, entry=None):  # <--- Aggiunto entry=None
        super().__init__(parent)
        self.on_save = on_save
        self.entry = entry
        
        self.title("EDIT SSH CREDENTIAL" if entry else "ADD SSH CREDENTIAL")
        self.geometry("450x450")
        self.resizable(False, False)
        self.configure(fg_color=theme.BG_BASE)
        self.grab_set()
        
        self.title_label = ctk.CTkLabel(
            self, text="EDIT SSH CREDENTIAL" if entry else "NEW SSH CREDENTIAL", 
            font=theme.font_title(18), text_color=theme.MAGENTA_NEON
        )
        self.title_label.pack(pady=(20, 15))

        self.service_entry = ctk.CTkEntry(self, placeholder_text="Host / Server SSH", width=320, height=40, **theme.entry_kwargs())
        self.service_entry.pack(pady=8)

        self.user_entry = ctk.CTkEntry(self, placeholder_text="Username SSH", width=320, height=40, **theme.entry_kwargs())
        self.user_entry.pack(pady=8)

        self.pass_entry = ctk.CTkEntry(self, placeholder_text="Password / Passphrase", show="*", width=320, height=40, **theme.entry_kwargs())
        self.pass_entry.pack(pady=8)

        self.port_entry = ctk.CTkEntry(self, placeholder_text="Porta SSH (default: 22)", width=320, height=40, **theme.entry_kwargs())
        self.port_entry.pack(pady=8)

        # SE SIAMO IN MODIFICA: Pre-compiliamo i campi
        if self.entry:
            # Inseriamo i testi esistenti prima di bloccare lo stato
            self.service_entry.insert(0, self.entry.host)
            self.user_entry.insert(0, self.entry.username)
            self.pass_entry.insert(0, self.entry.password_cifrata)
            self.port_entry.insert(0, str(self.entry.port))
            
            # Impostiamo su "readonly": l'utente non può alterarli, ma .get() continuerà a funzionare!
            self.service_entry.configure(state="readonly")
            self.user_entry.configure(state="readonly")
            
            # Ci assicuriamo che i campi editabili siano attivi ed espliciti
            self.pass_entry.configure(state="normal")
            self.port_entry.configure(state="normal")

        self.error_label = ctk.CTkLabel(self, text="", font=theme.font_body(12), text_color=theme.DANGER)
        self.error_label.pack(pady=5)

        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(pady=(10, 15))

        self.btn_cancel = ctk.CTkButton(self.btn_frame, text="Annulla", width=100, command=self.destroy, **theme.button_secondary_kwargs())
        self.btn_cancel.grid(row=0, column=0, padx=10)

        self.btn_save = ctk.CTkButton(
            self.btn_frame, 
            text="Aggiorna" if entry else "Salva", 
            width=150, 
            command=self._save, 
            **theme.button_primary_kwargs()
        )
        self.btn_save.grid(row=0, column=1, padx=10)

    def _save(self):
        # Grazie allo stato 'readonly', recuperiamo i dati senza problemi!
        servizio = self.service_entry.get().strip()
        username = self.user_entry.get().strip()
        password = self.pass_entry.get()
        porta = self.port_entry.get().strip()

        if not servizio or not username or not password:
            self.error_label.configure(text="I campi Host, Username e Password sono obbligatori.")
            return

        self.on_save(tipo="ssh", servizio=servizio, username=username, password=password, porta=porta, is_modifica=bool(self.entry))
        self.destroy()