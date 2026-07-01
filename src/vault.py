# src/vault.py
import json
import os

class CredentialVault:
    """
    CLASSE BASE (ASTRATTA)
    Definisce lo scheletro comune per tutti i gestori di password.
    Soddisfa il requisito d'esame sulla struttura comune.
    """
    def __init__(self):
        # Il dizionario in memoria ereditato da tutte le sottoclassi
        self.credentials = {}

    def salva_credenziale(self, servizio, username, password):
        """Metodo polimorfico che le sottoclassi DEVONO ridefinire."""
        raise NotImplementedError("Le sottoclassi devono implementare questo metodo!")

    def cerca_credenziale(self, servizio):
        """Metodo polimorfico che le sottoclassi DEVONO ridefinire."""
        raise NotImplementedError("Le sottoclassi devono implementare questo metodo!")


class MemoryVault(CredentialVault):
    """
    SOTTO CLASSE CONCRETA 1
    Gestisce le password solo in memoria RAM (Volatile).
    Ideale per i futuri test con pytest.
    """
    def salva_credenziale(self, servizio, username, password):
        self.credentials[servizio.lower()] = {
            "username": username,
            "password": password
        }
        print("\n[MemoryVault] Dati salvati temporaneamente in RAM.")

    def cerca_credenziale(self, servizio):
        return self.credentials.get(servizio.lower(), None)


class LocalJsonVault(CredentialVault):
    """
    SOTTO CLASSE CONCRETA 2
    Gestisce la persistenza salvando i dati su un file JSON locale.
    """
    def __init__(self, filepath="passwords.json"):
        super().__init__()  # Inizializza il dizionario del genitore
        self.filepath = filepath
        self._carica_da_file()

    def _carica_da_file(self):
        """Carica i dati dal file JSON se esiste, gestendo eventuali corruzioni."""
        if os.path.exists(self.filepath):
            with open(self.filepath, "r", encoding="utf-8") as f:
                try:
                    self.credentials = json.load(f)
                except json.JSONDecodeError:
                    self.credentials = {}

    def salva_credenziale(self, servizio, username, password):
        # Aggiorna il dizionario in memoria
        self.credentials[servizio.lower()] = {
            "username": username,
            "password": password
        }
        # Scrive in modo persistente sul file JSON
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.credentials, f, indent=4)
        print(f"\n[LocalJsonVault] File '{self.filepath}' aggiornato con successo.")

    def cerca_credenziale(self, servizio):
        return self.credentials.get(servizio.lower(), None)