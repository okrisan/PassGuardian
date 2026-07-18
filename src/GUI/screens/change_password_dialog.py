import customtkinter as ctk
from tkinter import messagebox
from GUI import theme

class ChangePasswordDialog(ctk.CTkToplevel):
    def __init__(self, parent, app, on_success):
        super().__init__(parent)
        self.app = app
        self.on_success = on_success
        
        self.title("Cambia Master Password")
        self.geometry("400x320")
        self.resizable(False, False)
        self.configure(fg_color=theme.BG_BASE)
        
        # Blocca l'interazione con la dashboard sottostante (finestra modale)
        self.grab_set()
        
        # Layout
        self.grid_columnconfigure(0, weight=1)
        
        self.lbl_title = ctk.CTkLabel(
            self, text="MODIFICA MASTER PASSWORD", 
            font=theme.font_title(size=16), text_color=theme.MAGENTA_NEON
        )
        self.lbl_title.grid(row=0, column=0, pady=(20, 15))
        
        # Campi Input
        self.entry_vecchia = ctk.CTkEntry(self, placeholder_text="Vecchia Master Password", show="*", width=300)
        self.entry_vecchia.grid(row=1, column=0, pady=5)
        
        self.entry_nuova = ctk.CTkEntry(self, placeholder_text="Nuova Master Password", show="*", width=300)
        self.entry_nuova.grid(row=2, column=0, pady=5)
        
        self.entry_conferma = ctk.CTkEntry(self, placeholder_text="Conferma Nuova Password", show="*", width=300)
        self.entry_conferma.grid(row=3, column=0, pady=5)
        
        # Bottoni
        self.btn_salva = ctk.CTkButton(
            self, text="Aggiorna Password", command=self._esegui_cambio,
            **theme.button_primary_kwargs()
        )
        self.btn_salva.grid(row=4, column=0, pady=(20, 5))
        
        self.btn_annulla = ctk.CTkButton(
            self, text="Annulla", command=self.destroy,
            **theme.button_secondary_kwargs()
        )
        self.btn_annulla.grid(row=5, column=0, pady=5)

    def _esegui_cambio(self):
        vecchia = self.entry_vecchia.get()
        nuova = self.entry_nuova.get()
        conferma = self.entry_conferma.get()
        
        # 1. Controlli formali puramente grafici
        if not vecchia or not nuova or not conferma:
            messagebox.showwarning("Campi vuoti", "Tutti i campi sono obbligatori.")
            return
            
        if nuova != conferma:
            messagebox.showerror("Errore", "La nuova password e la conferma non corrispondono.")
            return
            
        if vecchia == nuova:
            messagebox.showwarning("Attenzione", "La nuova password deve essere diversa da quella attuale.")
            return

        # 2. Invocazione della logica slegata (lato ENGINE)
        # Interroghiamo lo storage passando i parametri estratti dai widget
        successo = self.app.storage.cambia_master_password(self.app.username, vecchia, nuova)
        
        # 3. La UI reagisce in base al booleano restituito dal motore
        if successo:
            messagebox.showinfo("Successo", "Master Password aggiornata con successo!")
            self.on_success(nuova)  # Comunica la nuova password alla dashboard
            self.destroy()          # Chiude il pop-up
        else:
            messagebox.showerror("Errore", "La vecchia Master Password inserita è errata.")