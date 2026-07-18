# src/GUI/screens/dashboard.py
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from ENGINE.phishing import verifica_antiphishing_estesa
from GUI import theme

from GUI.screens.change_password_dialog import ChangePasswordDialog
from GUI.screens.countdown_dialog import CountdownDialog
from GUI.screens.countdown_dialog import CountdownDialog
from GUI.screens.credential_dialogs import AddWebDialog, AddSshDialog
from ENGINE.models.web import WebLoginEntry
from ENGINE.models.ssh import SSHLoginEntry
from GUI.screens.check_phishing_dialog import CheckPhishingDialog
from ENGINE.models.web import WebLoginEntry
from ENGINE.utils import calcola_distanza_levenshtein
from urllib.parse import urlparse



class Dashboard(ctk.CTkFrame):
    """Pannello di controllo principale per gestire credenziali Web e SSH."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=theme.BG_BASE)
        self.app = app
        
        # Configurazione Layout (Sidebar a sinistra, Contenuto a destra)
        self.grid_columnconfigure(0, weight=0)  # Sidebar fissa
        self.grid_columnconfigure(1, weight=1)  # Contenuto principale flessibile
        self.grid_rowconfigure(0, weight=1)

        # ----------------- SIDEBAR -----------------
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=theme.BG_SURFACE)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)  # Spazio flessibile prima del logout

        # Titolo Sidebar
        self.sb_title = ctk.CTkLabel(
            self.sidebar, text="PASS GUARDIAN", font=theme.font_title(size=18), text_color=theme.MAGENTA_NEON
        )
        self.sb_title.grid(row=0, column=0, padx=20, pady=30, sticky="w")

        # Info Utente Loggato
        self.user_info = ctk.CTkLabel(
            self.sidebar,
            text=f"Utente: {self.app.username}",
            font=theme.font_body(size=12),
            text_color=theme.GRAY_TEXT,
            justify="left"
        )
        self.user_info.grid(row=1, column=0, padx=20, pady=(0, 30), sticky="w")

        # Bottoni di navigazione Sidebar
        self.btn_add_web = ctk.CTkButton(
            self.sidebar, text="+ Credenziale Web", command=self._aggiungi_web, **theme.button_ghost_kwargs()
        )
        self.btn_add_web.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.btn_add_ssh = ctk.CTkButton(
            self.sidebar, text="+ Credenziale SSH", command=self._aggiungi_ssh, **theme.button_ghost_kwargs()
        )
        self.btn_add_ssh.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # --- NUOVO BOTTONE AGGIUNTO QUI (Riga 4) ---
        self.btn_change_pwd = ctk.CTkButton(
            self.sidebar, text="🔒 Cambia Password", command=self._apri_cambio_password, **theme.button_ghost_kwargs()
        )
        self.btn_change_pwd.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

        # Logout posizionato in fondo
        self.btn_logout = ctk.CTkButton(
            self.sidebar, text="Disconnect Session", command=self.app.logout, **theme.button_danger_kwargs()
        )
        self.btn_logout.grid(row=6, column=0, padx=20, pady=20, sticky="ew")

        # ----------------- CONTENUTO PRINCIPALE -----------------
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
        
        # AGGIORNAMENTO RIGHE: row 1 è la ricerca, row 2 la tabella (si espande), row 3 le azioni
        self.content_frame.grid_rowconfigure(0, weight=0)  # Header
        self.content_frame.grid_rowconfigure(1, weight=0)  # Barra di Ricerca
        self.content_frame.grid_rowconfigure(2, weight=1)  # Tabella flessibile
        self.content_frame.grid_rowconfigure(3, weight=0)  # Barra azioni fissa
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Intestazione
        self.header_label = ctk.CTkLabel(
            self.content_frame, text="LOGGED CREDENTIALS", font=theme.font_title(size=20), text_color=theme.TEXT_PRIMARY
        )
        self.header_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # ----------------- BARRA DI RICERCA AVANZATA -----------------
        self.search_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        # FONDAMENTALE: Posiziona fisicamente il frame nello schermo!
        self.search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))

        # Menu a tendina per scegliere la tipologia di target
        self.search_type = ctk.CTkOptionMenu(
            self.search_frame,
            values=["Username", "URL (Web)", "IP / Host (SSH)"],
            width=180,
            command=self._cambia_placeholder_ricerca
        )
        self.search_type.pack(side="left", padx=(0, 10))

        # Input di testo della ricerca
        self.search_entry = ctk.CTkEntry(
            self.search_frame, 
            placeholder_text="Inserisci username/URL/hostname da cercare...", 
            height=35
        )
        self.search_entry.pack(fill="x", side="left", expand=True, padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self._esegui_ricerca_e_controllo())

        # Bottone Cerca e Controlla
        self.btn_search = ctk.CTkButton(
            self.search_frame, 
            text="🔍 Cerca e Controlla", 
            width=140,
            command=self._esegui_ricerca_e_controllo,
            **theme.button_primary_kwargs()
        )
        self.btn_search.pack(side="right")

        # ----------------- TABELLA (Spostata a riga 2) -----------------
        self.credenziali_caricate = []
        self._crea_tabella()
        # Nota: ricordati di verificare che all'interno di self._crea_tabella() il widget 
        # contenitore (es. Treeview o il canvas) sia posizionato a row=2 del content_frame.

        # ----------------- BARRA DELLE AZIONI RAPIDE (Spostata a riga 3) -----------------
        self.action_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.action_frame.grid(row=3, column=0, sticky="ew", pady=(20, 0))
        
        # 1. Sblocca in clipboard
        self.btn_copy_clip = ctk.CTkButton(
            self.action_frame, text="📋 Copia in Clipboard", command=lambda: self._sblocca_selezionata("clipboard"),
            width=150, **theme.button_primary_kwargs()
        )
        self.btn_copy_clip.grid(row=0, column=0, padx=(0, 10))

        # 2. Smart Autofill
        self.btn_autofill = ctk.CTkButton(
            self.action_frame, text="⚡ Smart Autofill", command=self._esegui_smart_autofill,
            width=150, fg_color="#1F3A60", hover_color="#2A5288", text_color="#A4C7FF"
        )
        self.btn_autofill.grid(row=0, column=1, padx=10)

        # 3. Modifica Dati
        self.btn_edit = ctk.CTkButton(
            self.action_frame, text="📝 Modifica Dati", command=self._modifica_selezionata,
            width=130, **theme.button_secondary_kwargs()
        )
        self.btn_edit.grid(row=0, column=2, padx=10)

        # 4. Rimuovi Credenziale
        self.btn_delete = ctk.CTkButton(
            self.action_frame, text="🗑️ Rimuovi", command=self._cancella_selezionata,
            width=110, fg_color="#3A1C1C", hover_color="#6B2424", text_color="#FF8282"
        )
        self.btn_delete.grid(row=0, column=3, padx=10)
        
        # Inizializzazione dati della tabella
        self._aggiorna_tabella()

    def _crea_tabella(self):
        style = ttk.Style()
        theme.style_treeview(style)

        # Container per nascondere i bordi bianchi
        self.tree_container = ctk.CTkFrame(self.content_frame, fg_color="#120E16", border_width=0)
        self.tree_container.grid(row=2, column=0, sticky="nsew")
        self.tree_container.grid_rowconfigure(0, weight=1)
        self.tree_container.grid_columnconfigure(0, weight=1)

        colonne = ("Tipo", "Titolo/Servizio", "Username", "Dettagli Extra")
        self.tree = ttk.Treeview(
            self.tree_container, columns=colonne, show="headings", style="Cyber.Treeview"
        )
        
        # Configurazione delle Intestazioni (Headers) con allineamento a sinistra
        self.tree.heading("Tipo", text=" TIPO", anchor="w")
        self.tree.heading("Titolo/Servizio", text=" SERVIZIO / HOST", anchor="w")
        self.tree.heading("Username", text=" USERNAME / ACCOUNT", anchor="w")
        self.tree.heading("Dettagli Extra", text=" DETTAGLI (Porta / URL)", anchor="w")

        # Allineamento millimetrico delle Colonne (Dati)
        self.tree.column("Tipo", width=130, minwidth=100, anchor="w", stretch=True)
        self.tree.column("Titolo/Servizio", width=250, minwidth=180, anchor="w", stretch=True)
        self.tree.column("Username", width=220, minwidth=150, anchor="w", stretch=True)
        self.tree.column("Dettagli Extra", width=220, minwidth=150, anchor="w", stretch=True)

        scrollbar = ttk.Scrollbar(
            self.tree_container, orient="vertical", command=self.tree.yview, style="Cyber.Vertical.TScrollbar"
        )
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _aggiorna_tabella(self):
        """Pulisce la tabella, interroga il database e ricollega le istanze reali."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Carichiamo i record reali decifrati
        self.credenziali_caricate = self.app.storage.carica_credenziali(
            self.app.master_password, self.app.username
        )

        # Inseriamo i dati in tabella usando le proprietà polimorfiche delle classi base
        for index, entry in enumerate(self.credenziali_caricate):
            self.tree.insert(
                "",
                "end",
                iid=str(index),  # Usiamo l'indice della lista come ID della riga
                values=(
                    entry.etichetta_tipo,
                    entry.titolo,
                    entry.username,
                    entry.dettagli_tabella
                )
            )

    def _aggiungi_web(self):
        AddWebDialog(self, on_save=self._salva_nuova_credenziale)

    def _aggiungi_ssh(self):
        AddSshDialog(self, on_save=self._salva_nuova_credenziale)

    def _salva_nuova_credenziale(self, tipo, servizio, username, password, porta=None, is_modifica=False):
        try:
            if tipo == "web":
                entry = WebLoginEntry(
                    titolo=servizio, 
                    username=username, 
                    password_cifrata=password, 
                    url=servizio, 
                    proprietario=self.app.username
                )
            else:
                entry = SSHLoginEntry(
                    titolo=f"SSH: {servizio}", 
                    username=username, 
                    password_cifrata=password, 
                    host=servizio, 
                    port=int(porta) if porta else 22, 
                    proprietario=self.app.username
                )

            if is_modifica:
                # Usiamo il metodo di update
                self.app.storage.aggiorna_credenziale(entry, self.app.master_password, self.app.username)
            else:
                # Nuovo inserimento standard
                self.app.storage.salva_credenziale(entry, self.app.master_password, self.app.username)
            
            self._aggiorna_tabella()
            
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile elaborare l'operazione:\n{e}")

    def _sblocca_selezionata(self, metodo):
        """Prende la credenziale selezionata ed esegue l'erogazione della password decifrata."""
        selezionato = self.tree.selection()
        if not selezionato:
            messagebox.showwarning("Selezione mancante", "Seleziona prima una credenziale dalla tabella.")
            return

        index_selezionato = int(selezionato[0])
        entry = self.credenziali_caricate[index_selezionato]

        # Sostituiamo il controllo entry.tipo con isinstance per evitare l'AttributeError[cite: 5]
        url_richiesto = entry.titolo if isinstance(entry, WebLoginEntry) else None

        successo = entry.sblocca_credenziali(
            metodo_output=metodo,
            password_chiaro=entry.password_cifrata,
            url_richiesto=url_richiesto
        )

        if successo:
            print(f"[SESSIONE] Erogazione password per {entry.titolo} tramite {metodo} completata.")

    def _esegui_smart_autofill(self):
        """Esegue l'autofill iniettando il countdown grafico tramite una espressione lambda."""
        selezionato = self.tree.selection()
        if not selezionato:
            messagebox.showwarning("Selezione mancante", "Seleziona una credenziale per l'autofill.")
            return

        entry = self.credenziali_caricate[int(selezionato[0])]
        
        # Determiniamo dinamicamente i secondi di attesa (3 per Web, 4 per SSH)
        secondi = 3 if isinstance(entry, WebLoginEntry) else 4

        # Invochiamo il modello passando la lambda che istanzia la View grafica
        entry.esegui_autofill(
            callback_attesa=lambda azione: CountdownDialog(parent=self, secondi=secondi, callback_successo=azione)
        )

        

    def _modifica_selezionata(self):
        """Apre il pop-up configurato in modalità modifica passandogli i dati attuali."""
        selezionato = self.tree.selection()
        if not selezionato:
            
            messagebox.showwarning("Selezione mancante", "Seleziona prima la credenziale da modificare.")
            return

        entry = self.credenziali_caricate[int(selezionato[0])]

        # Usiamo isinstance anche qui
        if isinstance(entry, WebLoginEntry):
            AddWebDialog(self, on_save=self._salva_nuova_credenziale, entry=entry)
        else:
            AddSshDialog(self, on_save=self._salva_nuova_credenziale, entry=entry)

    def _cancella_selezionata(self):
        """Rimuove la credenziale selezionata dal file JSON."""
        selezionato = self.tree.selection()
        if not selezionato:
            messagebox.showwarning("Selezione mancante", "Seleziona prima una credenziale da rimuovere.")
            return

        index_selezionato = int(selezionato[0])
        entry = self.credenziali_caricate[index_selezionato]

        conferma = messagebox.askyesno(
            "Conferma Eliminazione",
            f"Sei sicuro di voler eliminare definitivamente la credenziale per '{entry.titolo}'?"
        )
        if conferma:
            try:
                dati = self.app.storage._leggi_tutto()
                
                nuove_credenziali = []
                for rec in dati["credenziali"]:
                    if (str(rec.get("proprietario")).lower() == self.app.username.lower() and 
                        str(rec.get("titolo")).lower() == entry.titolo.lower() and 
                        str(rec.get("username")).lower() == entry.username.lower()):
                        continue
                    nuove_credenziali.append(rec)
                
                dati["credenziali"] = nuove_credenziali
                self.app.storage._scrivi_tutto(dati)
                
                self._aggiorna_tabella()
                
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile eliminare l'elemento: {e}")

    def _apri_controllo_phishing(self):
        """Apre la finestra di verifica per l'URL inserito esternamente."""
        
        
        def avvia_autofill_diretto(entry):
            # Lancia l'autofill polimorfico dell'entry selezionata dopo il check positivo
            entry.esegui_autofill(parent_window=self)

        CheckPhishingDialog(
            parent=self, 
            credenziali_caricate=self.credenziali_caricate, 
            callback_autofill=avvia_autofill_diretto
    )
        

    def _cambia_placeholder_ricerca(self, scelta):
        """Aggiorna il testo di aiuto in base alla modalità selezionata."""
        if scelta == "URL (Web)":
            self.search_entry.configure(placeholder_text="Incolla qui l'URL del sito (es. https://google.com)...")
        elif scelta == "IP / Host (SSH)":
            self.search_entry.configure(placeholder_text="Incolla qui l'IP o l'Host (es. 192.168.1.1)...")
        else:
            self.search_entry.configure(placeholder_text="Inserisci il nome o l'username da cercare...")

    def _esegui_ricerca_e_controllo(self):
        """Esegue il filtro visivo applicando la logica di protezione estesa con la whitelist centralizzata."""
        tipo_controllo = self.search_type.get()
        testo = self.search_entry.get().strip()

        if not testo:
            self._aggiorna_tabella_visiva(self.credenziali_caricate)
            return

        risultati_filtrati = []
        
        # Allineamento dei valori con l'OptionMenu ("Username" mappa al ramo di ricerca testuale)
        if tipo_controllo == "Username":
            for entry in self.credenziali_caricate:
                if testo.lower() in entry.titolo.lower() or testo.lower() in entry.username.lower():
                    risultati_filtrati.append(entry)
            self._aggiorna_tabella_visiva(risultati_filtrati)

        elif tipo_controllo == "URL (Web)":
            # --- PARSING E PULIZIA AVANZATA DELL'URL INSERITO ---
            url_inserito = testo.strip().lower()
            if not url_inserito.startswith(("http://", "https://")):
                url_analizzabile = "https://" + url_inserito
            else:
                url_analizzabile = url_inserito
                
            parsed_url = urlparse(url_analizzabile)
            url_cercato = parsed_url.netloc
            if url_cercato.startswith("www."):
                url_cercato = url_cercato[4:]
            
            if not url_cercato:
                url_cercato = url_inserito

            # --- INVOCAZIONE DELLA LOGICA CENTRALIZZATA ANTI-PHISHING DELL'ENGINE ---
            # La funzione interroga sia il Vault dell'utente che il file whitelist.json sul database
            esito, messaggio, entita = verifica_antiphishing_estesa(url_cercato, self.credenziali_caricate)

            if esito == "OK_VAULT":
                # Mostra solo il record esatto associato
                if entita:
                    risultati_filtrati.append(entita)
                self._aggiorna_tabella_visiva(risultati_filtrati)
                messagebox.showinfo("✅ URL Sicuro", f"{messaggio}\nTrovata una corrispondenza esatta nel tuo database.")
                
            elif esito == "OK_WHITELIST":
                # È presente nella whitelist globale
                self._aggiorna_tabella_visiva([])
                messagebox.showinfo("✅ Brand Affidabile", messaggio)

            elif esito == "PHISHING_VAULT":
                # Blocchiamo la GUI e isoliamo l'elemento imitato
                if entita:
                    risultati_filtrati.append(entita)
                self._aggiorna_tabella_visiva(risultati_filtrati)
                messagebox.showerror(
                    "🚨 ALLARME PHISHING - ATTENZIONE",
                    f"ATTENZIONE!\n\n{messaggio}\n\n"
                    f"Il dominio inserito sembra contraffatto per ingannarti.\n"
                    f"Credenziale reale memorizzata: {entita.titolo} ({entita.url})"
                )

            elif esito == "PHISHING_BRAND":
                # Il dominio imita un brand noto della whitelist globale
                self._aggiorna_tabella_visiva([])
                messagebox.showerror(
                    "🚨 ALLARME SICUREZZA - MARCHIO COPIATO",
                    f"ATTENZIONE PERICOLO PHISHING!\n\n{messaggio}\n\n"
                    "L'erogazione dei dati è bloccata. Non immettere credenziali in questo sito!"
                )

            else:  # NON_TROVATO
                self._aggiorna_tabella_visiva([])
                messagebox.showinfo("ℹ️ Esito Controllo", messaggio)

        elif tipo_controllo == "IP / Host (SSH)":
            for entry in self.credenziali_caricate:
                if isinstance(entry, SSHLoginEntry):
                    if testo.lower() in entry.host.lower():
                        risultati_filtrati.append(entry)

            self._aggiorna_tabella_visiva(risultati_filtrati)

            if risultati_filtrati:
                if risultati_filtrati[0].valida_indirizzo():
                    messagebox.showinfo("✅ Host Valido", f"Trovata credenziale valida per l'Host/IP: {testo}")
                else:
                    messagebox.showwarning("⚠️ Host Malformato", "La credenziale trovata ha un formato IP o Hostname non valido nel database.")
            else:
                messagebox.showinfo("ℹ️ Esito Controllo", "Nessun server SSH trovato con questo IP o Host.")

    def _aggiorna_tabella_visiva(self, lista_credenziali):
        """Svuota e ripopola la tabella con una lista specifica di credenziali."""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for idx, entry in enumerate(self.credenziali_caricate):
            if entry in lista_credenziali:
                self.tree.insert(
                    "", 
                    "end", 
                    iid=str(idx), 
                    values=(entry.etichetta_tipo, entry.titolo, entry.username, entry.dettagli_tabella)
                )

    def _apri_cambio_password(self):
        """Apre il pop-up grafico passando l'azione da eseguire in caso di successo."""
        
        def al_successo_cambio(nuova_password):
            # Aggiorna la password della sessione corrente nell'istanza principale dell'app
            self.app.master_password = nuova_password
            # Ricarica la tabella (anche se i dati visivi non cambiano, 
            # verifica che la nuova password decifri tutto correttamente)
            self._aggiorna_tabella()

        # Mostra il pop-up passandogli la dashboard (self) come parent
        ChangePasswordDialog(
            parent=self,
            app=self.app,
            on_success=al_successo_cambio
        )