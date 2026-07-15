# src/ENGINE/vault.py
import json
import os
from ENGINE.security import cifra_password, decifra_password


class LocalJsonVault:
    def __init__(self):
        # Definiamo i percorsi ma NON creiamo il file json vuoto all'avvio
        self.cartella_db = os.path.join(os.path.dirname(os.path.dirname(__file__)), "DATABASE")
        self.percorso_file = os.path.join(self.cartella_db, "passwords.json")

        if not os.path.exists(self.cartella_db):
            os.makedirs(self.cartella_db, exist_ok=True)

    def _carica_dati(self):
        """Legge i dati dal file JSON se esiste, altrimenti ritorna un dizionario vuoto senza creare file."""
        if not os.path.exists(self.percorso_file):
            return {}
        try:
            with open(self.percorso_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _salva_dati(self, dati):
        """Scrive i dati nel file JSON, creandolo solo nel momento in cui c'è qualcosa da salvare."""
        with open(self.percorso_file, "w", encoding="utf-8") as f:
            json.dump(dati, f, indent=4)

    def salva_credenziale(self, utente_corrente, servizio, username, password):
        """Salva la credenziale isolandola sotto il nome dell'utente loggato."""
        dati = self._carica_dati()

        if utente_corrente not in dati:
            dati[utente_corrente] = {}

        password_cifrata = cifra_password(password)
        dati[utente_corrente][servizio] = {
            "username": username,
            "password": password_cifrata
        }
        self._salva_dati(dati)

    def cerca_credenziale(self, utente_corrente, servizio):
        """Cerca una credenziale solo tra quelle appartenenti all'utente loggato."""
        dati = self._carica_dati()
        utente_dati = dati.get(utente_corrente, {})
        credenziale = utente_dati.get(servizio, None)

        if credenziale:
            try:
                password_decifrata = decifra_password(credenziale["password"])
                return {
                    "username": credenziale["username"],
                    "password": password_decifrata
                }
            except Exception:
                return credenziale
        return None

    def modifica_password(self, utente_corrente, servicio, nuova_password):
        """Modifica la password di un servizio appartenente all'utente loggato."""
        dati = self._carica_dati()

        if utente_corrente in dati and servicio in dati[utente_corrente]:
            password_cifrata = cifra_password(nuova_password)
            dati[utente_corrente][servicio]["password"] = password_cifrata
            self._salva_dati(dati)
            return True
        return False

    def elenca_credenziali(self, utente_corrente):
        """Ritorna la lista dei servizi salvati per un dato utente (senza decifrare)."""
        dati = self._carica_dati()
        return dati.get(utente_corrente, {})

    def elenca_tutte(self):
        """Ritorna l'intero database (tutti gli utenti), usato dalla vista admin."""
        return self._carica_dati()

    def elimina_credenziale(self, utente_corrente, servizio):
        """Rimuove una credenziale specifica dal vault dell'utente."""
        dati = self._carica_dati()
        if utente_corrente in dati and servizio in dati[utente_corrente]:
            del dati[utente_corrente][servizio]
            self._salva_dati(dati)
            return True
        return False