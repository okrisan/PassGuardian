# src/ENGINE/auth.py
import json
import os
import getpass  # Libreria standard per nascondere l'input della password
from ENGINE.security import hash_master_password

# Forziamo il percorso della cartella DATABASE tassativamente dentro src/
CARTELLA_SRC = os.path.dirname(os.path.dirname(__file__))
PATH_UTENTI = os.path.join(CARTELLA_SRC, "DATABASE", "utenti.json")

# Variabile globale per tracciare chi è loggato ("user", "super_user" o None)
ruolo_attuale = None


def inizializza_utenti():
    """Crea la cartella DATABASE e il file utenti.json con credenziali di test se non esiste."""
    cartella_db = os.path.dirname(PATH_UTENTI)
    if not os.path.exists(cartella_db):
        os.makedirs(cartella_db, exist_ok=True)

    if not os.path.exists(PATH_UTENTI):
        # Generiamo gli hash di default per i test:
        # admin -> admin123  (Super User master)
        # alessandro -> user123 (Utente normale)
        dati_default = {
            "admin": {
                "password_hash": hash_master_password("admin123"),
                "ruolo": "super_user"
            },
            "alessandro": {
                "password_hash": hash_master_password("user123"),
                "ruolo": "user"
            }
        }
        with open(PATH_UTENTI, "w", encoding="utf-8") as f:
            json.dump(dati_default, f, indent=4)


def verifica_login(username_inserito, password_inserita):
    """
    Verifica se lo username esiste e se l'hash della password coincide.
    Ritorna il ruolo dell'utente se il login ha successo, altrimenti None.
    """
    inizializza_utenti()

    try:
        with open(PATH_UTENTI, "r", encoding="utf-8") as f:
            utenti = json.load(f)
    except Exception:
        return None

    if username_inserito in utenti:
        utente = utenti[username_inserito]
        hash_calcolato = hash_master_password(password_inserita)

        if hash_calcolato == utente["password_hash"]:
            return utente["ruolo"]

    return None


def esegui_login():
    """
    Gestisce il flusso di login nascondendo la password durante la digitazione.
    """
    global ruolo_attuale
    inizializza_utenti()

    print("\n" + "=" * 30)
    print("      PASSGUARDIAN LOGIN      ")
    print("=" * 30)

    username = input("Username: ").strip()

    # Nasconde i caratteri digitati nel terminale per sicurezza
    password = getpass.getpass("Master Password (caratteri nascosti): ").strip()

    ruolo = verifica_login(username, password)

    if ruolo:
        ruolo_attuale = ruolo
        print(f"\n[OK] Login effettuato con successo! Benvenuto {username} ({ruolo}).")
        return True
    else:
        ruolo_attuale = None
        print("\n[ERRORE] Username o Master Password errati.")
        return False


def aggiungi_nuovo_utente(username, password, ruolo="user"):
    """
    Aggiunge un nuovo utente nel file utenti.json.
    Visibile ed eseguibile da tutti per la registrazione autonoma.
    Ritorna True se l'utente viene creato, False se esiste già.
    """
    inizializza_utenti()
    try:
        with open(PATH_UTENTI, "r", encoding="utf-8") as f:
            utenti = json.load(f)
    except Exception:
        utenti = {}

    if username in utenti:
        return False  # Impedisce la creazione di duplicati

    # Salviamo l'hash sicuro della password, mai il testo in chiaro
    utenti[username] = {
        "password_hash": hash_master_password(password),
        "ruolo": ruolo
    }

    with open(PATH_UTENTI, "w", encoding="utf-8") as f:
        json.dump(utenti, f, indent=4)
    return True


def elimina_utente(username_da_eliminare):
    """
    Elimina un utente dal file utenti.json.
    Ritorna True se eliminato, False se l'utente non esiste o se si tenta di eliminare l'admin.
    Nota: Il controllo sui permessi (se chi preme è 'super_user') viene delegato al main/interfaccia.
    """
    if username_da_eliminare == "admin":
        return False  # L'amministratore supremo di sistema non può essere cancellato

    try:
        with open(PATH_UTENTI, "r", encoding="utf-8") as f:
            utenti = json.load(f)
    except Exception:
        return False

    if username_da_eliminare in utenti:
        del utenti[username_da_eliminare]
        with open(PATH_UTENTI, "w", encoding="utf-8") as f:
            json.dump(utenti, f, indent=4)
        return True

    return False