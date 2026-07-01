# src/ENGINE/vault.py
import json
import os
# Importiamo le funzioni di crittografia dal modulo security
from ENGINE.security import cifra_password, decifra_password


class LocalJsonVault:
    def __init__(self):
        # os.path.dirname(__file__) si trova in src/ENGINE. Saliamo di un livello ed entriamo in DATABASE
        self.cartella_db = os.path.join(os.path.dirname(os.path.dirname(__file__)), "DATABASE")
        self.percorso_file = os.path.join(self.cartella_db, "passwords.json")

        # Crea la cartella DATABASE dentro src se non esiste ancora
        if not os.path.exists(self.cartella_db):
            os.makedirs(self.cartella_db, exist_ok=True)

        self._inizializza_vault()

    def _inizializza_vault(self):
        """Crea il file passwords.json vuoto se non esiste ancora."""
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
        """
        Salva una nuova credenziale. La password viene cifrata
        automaticamente prima del salvataggio su disco.
        """
        dati = self._carica_dati()

        # Cifriamo la password prima di scriverla nel JSON
        password_cifrata = cifra_password(password)

        dati[servizio] = {
            "username": username,
            "password": password_cifrata
        }
        self._salva_dati(dati)

    def cerca_credenziale(self, servizio):
        """
        Cerca una credenziale in base al nome del servizio.
        Ritorna il dizionario con lo username e la password DECIFRATA.
        """
        dati = self._carica_dati()
        credenziale = dati.get(servizio, None)

        if credenziale:
            try:
                # Decifriamo la password prima di passarla all'interfaccia
                password_decifrata = decifra_password(credenziale["password"])
                return {
                    "username": credenziale["username"],
                    "password": password_decifrata
                }
            except Exception:
                # Gestione dell'errore nel caso la stringa non sia cifrata correttamente
                return credenziale

        return None

    def modifica_password(self, servizio, nuova_password):
        """
        Modifica la password di un servizio esistente senza toccare lo username.
        Ritorna True se il servizio esiste ed è stato modificato, altrimenti False.
        """
        dati = self._carica_dati()

        if servicio in dati:
            # Cifriamo la nuova password
            password_cifrata = cifra_password(nuova_password)
            # Aggiorniamo solo il campo password mantenendo lo username intatto
            dati[servizio]["password"] = password_cifrata
            self._salva_dati(dati)
            return True

        return False