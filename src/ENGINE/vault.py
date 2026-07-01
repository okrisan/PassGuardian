# src/ENGINE/vault.py
import json
import os


class LocalJsonVault:
    def __init__(self):
        # Definiamo il percorso all'interno della cartella DATABASE con il nome password.json
        # os.path.dirname(os.path.dirname(__file__)) sale di un livello da ENGINE alla radice del progetto
        self.cartella_db = os.path.join(os.path.dirname(os.path.dirname(__file__)), "DATABASE")
        self.percorso_file = os.path.join(self.cartella_db, "passwords.json")

        # Crea la cartella DATABASE se non esiste ancora
        if not os.path.exists(self.cartella_db):
            os.makedirs(self.cartella_db)

        self._inizializza_vault()

    def _inizializza_vault(self):
        """Crea il file password.json vuoto se non esiste ancora."""
        if not os.path.exists(self.percorso_file):
            with open(self.percorso_file, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)

    def _carica_dati(self):
        """Legge i dati dal file JSON."""
        try:
            with open(self.percorso_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _salva_dati(self, dati):
        """Scrive i dati nel file JSON."""
        with open(self.percorso_file, "w", encoding="utf-8") as f:
            json.dump(dati, f, indent=4)

    def salva_credenziale(self, servizio, username, password):
        """Salva o aggiorna una credenziale associata a un servizio (dominio)."""
        dati = self._carica_dati()
        dati[servizio] = {
            "username": username,
            "password": password
        }
        self._salva_dati(dati)

    def cerca_credenziale(self, servizio):
        """Cerca una credenziale in base al nome del servizio."""
        dati = self._carica_dati()
        return dati.get(servizio, None)