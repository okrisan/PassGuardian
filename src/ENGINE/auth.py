# src/ENGINE/auth.py
import json
import os
import hashlib

cartella_db = os.path.join(os.path.dirname(os.path.dirname(__file__)), "DATABASE")
PATH_UTENTI = os.path.join(cartella_db, "users.json")

ruolo_attuale = None


def _hash_password(password):
    """Genera l'hash SHA-256 di una stringa password."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def inizializza_utenti_predefiniti():
    """Crea il file users.json impostando l'ID 0 per il Master se non esiste."""
    if not os.path.exists(cartella_db):
        os.makedirs(cartella_db, exist_ok=True)

    if not os.path.exists(PATH_UTENTI):
        utenti_default = {
            "admin": {
                "id": 0,
                "password": _hash_password("admin123"),
                "role": "super_user"
            },
            "alessandro": {
                "id": 1,
                "password": _hash_password("user123"),
                "role": "user"
            }
        }
        with open(PATH_UTENTI, "w", encoding="utf-8") as f:
            json.dump(utenti_default, f, indent=4)


# Esegue l'inizializzazione automatica al caricamento del modulo
inizializza_utenti_predefiniti()


def verifica_login(username, password):
    """Verifica le credenziali di login inserite."""
    if not os.path.exists(PATH_UTENTI):
        return None
    try:
        with open(PATH_UTENTI, "r", encoding="utf-8") as f:
            utenti = json.load(f)
        if username in utenti:
            if utenti[username]["password"] == _hash_password(password):
                # Controllo di integrità dell'ID
                if "id" not in utenti[username]:
                    utenti[username]["id"] = 0 if utenti[username]["role"] == "super_user" else 1
                    with open(PATH_UTENTI, "w", encoding="utf-8") as fw:
                        json.dump(utenti, fw, indent=4)
                return utenti[username]["role"]
    except Exception:
        return None
    return None


def aggiungi_nuovo_utente(username, password):
    """Aggiunge un nuovo utente standard calcolando l'ID incrementale."""
    try:
        with open(PATH_UTENTI, "r", encoding="utf-8") as f:
            utenti = json.load(f)

        if username in utenti:
            return False

        max_id = 0
        for info in utenti.values():
            if int(info.get("id", 0)) > max_id:
                max_id = int(info["id"])

        utenti[username] = {
            "id": max_id + 1,
            "password": _hash_password(password),
            "role": "user"
        }

        with open(PATH_UTENTI, "w", encoding="utf-8") as f:
            json.dump(utenti, f, indent=4)
        return True
    except Exception:
        return False


def aggiorna_password_utente(username, nuova_password):
    """Aggiorna in sicurezza la Master Password dell'utente corrente senza 'self'."""
    try:
        if not os.path.exists(PATH_UTENTI):
            return False

        with open(PATH_UTENTI, "r", encoding="utf-8") as f:
            utenti = json.load(f)

        if username not in utenti:
            return False

        # Assegna il nuovo hash calcolato localmente
        utenti[username]["password"] = _hash_password(nuova_password)

        with open(PATH_UTENTI, "w", encoding="utf-8") as f:
            json.dump(utenti, f, indent=4, ensure_ascii=False)

        return True
    except Exception as e:
        print(f"Errore nel backend durante il cambio password: {e}")
        return False


def elimina_utente(username):
    """Rimuove un utente dal sistema (impedisce la rimozione dell'admin)."""
    if username == "admin":
        return False
    try:
        with open(PATH_UTENTI, "r", encoding="utf-8") as f:
            utenti = json.load(f)
        if username in utenti:
            del utenti[username]
            with open(PATH_UTENTI, "w", encoding="utf-8") as f:
                json.dump(utenti, f, indent=4)
            return True
    except Exception:
        return False
    return False