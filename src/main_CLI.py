#!/usr/bin/env tuple
import cmd
import getpass
import sys
from urllib.parse import urlparse
import os

# Aggiungiamo la cartella "src" al path di ricerca di Python
cartella_corrente = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cartella_corrente, "src"))


# Import dei moduli dell'ENGINE
from ENGINE.phishing import verifica_antiphishing_estesa
from ENGINE.storage import VaultStorage
from ENGINE.models.web import WebLoginEntry
from ENGINE.models.ssh import SSHLoginEntry
from ENGINE.utils import calcola_distanza_levenshtein

class PassGuardianCLI(cmd.Cmd):
    intro = """
    ==================================================
              PASS GUARDIAN - CLI             
    ==================================================
    Benvenuto in PassGuardian. Digita 'help' o '?' per i comandi.
    """
    prompt = "PassGuardian> "

    def __init__(self):
        super().__init__()
        self.storage = VaultStorage("database/vault.json")
        self.username = None
        self.master_password = None
        self.credenziali_caricate = []

    def preloop(self):
        """Gestisce il login o la registrazione iniziale dell'utente."""
        print("Scegli un'opzione per iniziare:")
        print("1) Accedi")
        print("2) Registrati")
        scelta = input("Seleziona (1/2): ").strip()

        if scelta not in ("1", "2"):
            print("Scelta non valida. Uscita.")
            sys.exit(0)

        username = input("Username: ").strip()
        password = getpass.getpass("Master Password: ")

        if scelta == "1":
            if self.storage.verifica_utente(username, password):
                self.username = username
                self.master_password = password
                print(f"\n[+] Accesso eseguito con successo. Benvenuto {self.username}!")
                self.prompt = f"PassGuardian ({self.username})> "
                self._ricarica_vault()
            else:
                print("[-] Credenziali errate o utente inesistente. Accesso negato.")
                sys.exit(0)
        else:
            if self.storage.registra_utente(username, password):
                print(f"\n[+] Utente '{username}' registrato correttamente! Riavvia per accedere.")
                sys.exit(0)
            else:
                print("[-] Errore: l'username è già registrato.")
                sys.exit(0)

    def _ricarica_vault(self):
        """Aggiorna la cache locale delle credenziali in chiaro decifrate."""
        self.credenziali_caricate = self.storage.carica_credenziali(self.master_password, self.username)

    def _estrai_dominio(self, url: str) -> str:
        """Esegue il cut dell'URL prendendo solo la parte del dominio principale."""
        url_pulito = url.strip().lower()
        if not url_pulito.startswith(("http://", "https://")):
            url_pulito = "https://" + url_pulito
        
        parsed = urlparse(url_pulito)
        dominio = parsed.netloc
        if dominio.startswith("www."):
            dominio = dominio[4:]
        return dominio if dominio else url.strip().lower()

    def do_list(self, arg):
        """Mostra tutte le credenziali salvate nel vault dell'utente."""
        self._ricarica_vault()
        if not self.credenziali_caricate:
            print("Nessuna credenziale salvata nel tuo vault.")
            return

        print(f"\n{'N°':<4} | {'TIPO':<15} | {'SERVIZIO / HOST':<30} | {'USERNAME':<20}")
        print("-" * 75)
        for idx, entry in enumerate(self.credenziali_caricate):
            tipo = "Web Site" if isinstance(entry, WebLoginEntry) else "SSH Server"
            print(f"{idx:<4} | {tipo:<15} | {entry.titolo:<30} | {entry.username:<20}")
        print()

    def do_add_web(self, arg):
        """Aggiunge una nuova credenziale Web: add_web"""
        titolo = input("Titolo/Servizio: ").strip()
        username = input("Username/Account: ").strip()
        url = input("URL del sito: ").strip()
        password = getpass.getpass("Password del sito: ")

        if not titolo or not username or not url or not password:
            print("[-] Tutti i campi sono obbligatori.")
            return

        try:
            entry = WebLoginEntry(titolo=titolo, username=username, password_cifrata=password, url=url, proprietario=self.username)
            self.storage.salva_credenziale(entry, self.master_password, self.username)
            print("[+] Credenziale Web memorizzata con successo.")
            self._ricarica_vault()
        except Exception as e:
            print(f"[-] Errore durante il salvataggio: {e}")

    def do_add_ssh(self, arg):
        """Aggiunge una nuova credenziale SSH: add_ssh"""
        titolo = input("Titolo/Host SSH: ").strip()
        username = input("Username SSH: ").strip()
        host = input("Indirizzo IP/Hostname: ").strip()
        porta_raw = input("Porta [Default 22]: ").strip()
        porta = int(porta_raw) if porta_raw.isdigit() else 22
        password = getpass.getpass("Password SSH: ")

        if not titolo or not username or not host or not password:
            print("[-] Tutti i campi sono obbligatori.")
            return

        try:
            entry = SSHLoginEntry(titolo=titolo, username=username, password_cifrata=password, host=host, port=porta, proprietario=self.username)
            self.storage.salva_credenziale(entry, self.master_password, self.username)
            self._ricarica_vault()
        except Exception as e:
            print(f"[-] Errore durante il salvataggio: {e}")

    def do_check_url(self, arg):
        """Esegue il controllo anti-phishing centralizzato tramite l'ENGINE."""
        if not arg:
            arg = input("Incolla l'URL da verificare: ")
        
        url_cercato = self._estrai_dominio(arg)
        print(f"[*] Analisi dominio estratto: {url_cercato}")

        # Invochiamo la funzione centralizzata dell'ENGINE
        esito, messaggio, entita = verifica_antiphishing_estesa(url_cercato, self.credenziali_caricate)

        if esito in ("OK_VAULT", "OK_WHITELIST"):
            print(f"[✅ SICURO] {messaggio}")
        elif esito == "PHISHING_VAULT":
            print("\n" + "!"*60)
            print(f"[🚨 ALLARME PHISHING] {messaggio}")
            print(f"   -> Credenziale reale: {entita.titolo} ({entita.url})")
            print("!"*60 + "\n")
        elif esito == "PHISHING_BRAND":
            print("\n" + "!"*60)
            print(f"[🚨 ALLARME PHISHING] {messaggio}")
            print("!"*60 + "\n")
        else:
            print(f"[⚠️ INFO] {messaggio}")

    def do_chpwd(self, arg):
        """Cambia la Master Password di accesso ricifrando il database intero."""
        vecchia = getpass.getpass("Inserisci la vecchia Master Password: ")
        nuova = getpass.getpass("Inserisci la nuova Master Password: ")
        conferma = getpass.getpass("Conferma la nuova Master Password: ")

        if nuova != conferma:
            print("[-] Errore: la nuova password e la conferma non corrispondono.")
            return

        if vecchia == nuova:
            print("[-] Errore: la nuova password deve essere differente da quella precedente.")
            return

        successo = self.storage.cambia_master_password(self.username, vecchia, nuova)
        if successo:
            self.master_password = nuova
            print("[+] Master Password aggiornata con successo. Tutti i record sono stati ricifrati.")
            self._ricarica_vault()
        else:
            print("[-] Errore: la vecchia Master Password inserita non è corretta.")

    def do_exit(self, arg):
        """Sconnette l'utente e chiude la console."""
        print("Disconnessione della sessione in corso... Arrivederci!")
        return True
    def do_select(self, arg):
        """Seleziona e sblocca una credenziale tramite il suo numero. Uso: select <numero>"""
        if not arg.isdigit():
            print("[-] Specifica un numero di indice valido. Es: select 0")
            return

        idx = int(arg)
        # Ricarica per sicurezza prima di controllare gli indici
        self._ricarica_vault()

        if idx < 0 or idx >= len(self.credenziali_caricate):
            print(f"[-] Indice {idx} non valido. Usa 'list' per vedere gli indici disponibili.")
            return

        entry = self.credenziali_caricate[idx]
        print(f"\nHai selezionato: {entry.titolo} ({entry.username})")
        print("1) Copia Password negli appunti")
        print("2) Mostra Password in chiaro")
        print("3) Annulla")
        
        scelta = input("Cosa vuoi fare? (1/2/3): ").strip()

        if scelta == "1":
            # Usiamo il metodo polimorfico dell'entry per copiarla in clipboard
            # Nota: passiamo il parametro per disattivare eventuali controlli anti-phishing locali interattivi
            successo = entry.sblocca_credenziali(metodo_output="clipboard", password_chiaro=entry.password_cifrata, url_richiesto=None)
            if successo:
                print("[+] Password copiata negli appunti! Verrà ripulita automaticamente.")
        elif scelta == "2":
            # Mostra la password direttamente a schermo (presa in chiaro dalla cache in memoria)
            print(f"[👉 PASSWORD] {entry.password_cifrata}")
        else:
            print("[*] Operazione annullata.")

if __name__ == "__main__":
    # Avvio del listener CLI impostando il corretto percorso di ricerca per i pacchetti se necessario
    try:
        PassGuardianCLI().cmdloop()
    except KeyboardInterrupt:
        print("\n\nSessione interrotta forzatamente. Arrivederci!")