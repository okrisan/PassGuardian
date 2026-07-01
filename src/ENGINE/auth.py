# src/ENGINE/auth.py
import sys
import time
from getpass import getpass

# Importiamo SOLO le costanti dei colori dalla GUI
from GUI.interfaccia import BLU_SCURO, AZZURRO, NERO, BIANCO, RESET

def safe_getpass(prompt):
    """Evita il blocco del programma se eseguito in finti terminali (IDE)."""
    if not sys.stdin.isatty():
        return input(prompt + " (testo visibile nell'IDE): ")
    return getpass(prompt)


def esegui_login():
    """Gestisce l'autenticazione con la Master Password."""
    MASTER_PASSWORD = "admin"  # Puoi personalizzarla qui cambiandola tra virgolette
    tentativi = 3

    while tentativi > 0:
        print("\n" + BLU_SCURO + "=" * 40)
        print(" 🔒 AREA DI AUTENTICAZIONE MASTER  ")
        print("=" * 40 + RESET)
        print(f"Tentativi rimasti: {tentativi}\n")

        password_inserita = safe_getpass("🔑 Inserisci la Master Password: ")

        if password_inserita == MASTER_PASSWORD:
            print(AZZURRO + "\n✅ Autenticazione riuscita! Accesso consentito." + RESET)
            time.sleep(1.0)
            return True
        else:
            tentativi -= 1
            print(NERO + "\n❌ Password errata!" + RESET)
            time.sleep(1.0)

    print(NERO + "\n🚨 Troppi tentativi falliti. Applicazione bloccata per sicurezza." + RESET)
    sys.exit()