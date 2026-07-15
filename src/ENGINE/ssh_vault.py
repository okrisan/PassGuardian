import json
import os
from ENGINE.security import cifra_password, decifra_password


class SshVault:
    def __init__(self):
        self.cartella_db = os.path.join(os.path.dirname(os.path.dirname(__file__)), "DATABASE")
        self.percorso_file = os.path.join(self.cartella_db, "ssh_keys.json")

        if not os.path.exists(self.cartella_db):
            os.makedirs(self.cartella_db, exist_ok=True)

    def _carica_dati(self):
        """Legge i dati dal file JSON se esiste, altrimenti ritorna un dict vuoto."""
        if not os.path.exists(self.percorso_file):
            return {}
        try:
            with open(self.percorso_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _salva_dati(self, dati):
        """Scrive i dati nel file JSON."""
        with open(self.percorso_file, "w", encoding="utf-8") as f:
            json.dump(dati, f, indent=4, ensure_ascii=False)

    def salva_ssh(
            self,
            utente_corrente,
            nome_macchina,
            ip,
            ssh_username,
            password,
            porta,
            chiave_privata,
            note=""
    ):
        """Salva (o sovrascrive) una connessione SSH sotto l'utente corrente."""
        dati = self._carica_dati()
        if utente_corrente not in dati:
            dati[utente_corrente] = {}

        dati[utente_corrente][nome_macchina] = {
            "ip": ip,
            "ssh_username": ssh_username,
            "password": cifra_password(password) if password else "",
            "porta": int(porta) if porta else 22,
            "chiave_privata": cifra_password(chiave_privata) if chiave_privata else "",
            "note": note or ""
        }
        self._salva_dati(dati)

    def modifica_ssh(
            self,
            utente_corrente,
            nome_macchina,
            ip,
            ssh_username,
            password,
            porta,
            chiave_privata,
            note=""
    ):
        """Modifica una connessione SSH esistente.
        Se password o chiave privata sono vuote mantiene i valori precedenti.
        """

        dati = self._carica_dati()

        if utente_corrente in dati and nome_macchina in dati[utente_corrente]:

            dati[utente_corrente][nome_macchina]["ip"] = ip
            dati[utente_corrente][nome_macchina]["ssh_username"] = ssh_username
            dati[utente_corrente][nome_macchina]["porta"] = int(porta) if porta else 22
            dati[utente_corrente][nome_macchina]["note"] = note or ""

            if password:
                dati[utente_corrente][nome_macchina]["password"] = cifra_password(password)

            if chiave_privata:
                dati[utente_corrente][nome_macchina]["chiave_privata"] = cifra_password(chiave_privata)

            self._salva_dati(dati)
            return True

        return False

    def elenca_ssh(self, utente_corrente):
        """Ritorna le connessioni SSH di un singolo utente (chiave privata ancora cifrata)."""
        dati = self._carica_dati()
        return dati.get(utente_corrente, {})

    def elenca_tutte(self):
        """Ritorna l'intero database SSH (tutti gli utenti), usato dalla vista admin."""
        return self._carica_dati()

    def cerca_ssh(self, utente_corrente, nome_macchina):
        """Ritorna una singola connessione SSH con password e chiave privata decifrate."""
        dati = self._carica_dati()
        utente_dati = dati.get(utente_corrente, {})
        voce = utente_dati.get(nome_macchina, None)

        if voce:
            try:
                password_decifrata = decifra_password(voce.get("password", ""))
            except Exception:
                password_decifrata = ""

            try:
                chiave_decifrata = decifra_password(voce.get("chiave_privata", ""))
            except Exception:
                chiave_decifrata = ""

            return {
                "ip": voce.get("ip", ""),
                "ssh_username": voce.get("ssh_username", ""),
                "password": password_decifrata,
                "porta": voce.get("porta", 22),
                "chiave_privata": chiave_decifrata,
                "note": voce.get("note", "")
            }

        return None

    def elimina_ssh(self, utente_corrente, nome_macchina):
        """Rimuove una connessione SSH specifica."""
        dati = self._carica_dati()
        if utente_corrente in dati and nome_macchina in dati[utente_corrente]:
            del dati[utente_corrente][nome_macchina]
            self._salva_dati(dati)
            return True
        return False