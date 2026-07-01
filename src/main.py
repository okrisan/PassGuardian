# src/main.py
import sys
import time
from getpass import getpass

import pyautogui
import pyperclip  # Lo usiamo per passare i dati in sicurezza senza perdere la chiocciola (@)
# Libreria per controllare le finestre attive (si installa insieme a pyautogui)
import pygetwindow as gw

# Importiamo i nostri moduli locali
from security import PhishingDetector
from vault import LocalJsonVault, MemoryVault


def safe_getpass(prompt):
    if not sys.stdin.isatty():
        return input(prompt + " (testo visibile nell'IDE): ")
    return getpass(prompt)


def interfaccia_aggiungi(vault_attivo):
    servizio = input(
        "Inserisci il dominio del sito (es. google.com o github.com): "
    ).strip()
    if not servizio:
        print("⚠️ Il nome del servizio non può essere vuoto.")
        return

    detector = PhishingDetector()
    dominio_pulito = detector.estrai_dominio(servizio)

    username = input("Inserisci l'username o l'email: ").strip()
    password = safe_getpass("Inserisci la password: ")

    vault_attivo.salva_credenziale(dominio_pulito, username, password)


def interfaccia_cerca(vault_attivo):
    url_ricerca = input("Inserisci il sito/dominio da cercare (es. fad.its-ictpiemonte.it): ").strip()

    detector = PhishingDetector()
    dominio_pulito = detector.estrai_dominio(url_ricerca)

    sicuro, messaggio = detector.verifica_dominio(url_ricerca)
    credenziali = vault_attivo.cerca_credenziale(dominio_pulito)

    if credenziali:
        print("\n" + "=" * 30)
        print(f"🔒 ACCOUNT TROVATO PER: {dominio_pulito}")
        print("=" * 30)
        print(f"👤 Username: {credenziali['username']}")
        print("🔑 Password: [••••••••••••] (Nascosta per sicurezza)")
        print("-" * 30)
        print(f"🛡️ Analisi Sicurezza: {messaggio}")
        print("=" * 30)

        if not sicuro:
            print(f"\n{messaggio}")
            conferma = input("⚠️ Vuoi procedere comunque all'autofill? (si/no): ").strip().lower()
            if conferma != "si":
                print("❌ Operazione annullata per motivi di sicurezza.")
                return

        print("\n🚀 MODALITÀ AUTOFILL AVVIATA!")
        print(f"👉 APRI IL BROWSER SULLA PAGINA DI LOGIN DI: {dominio_pulito}")
        print("🎯 Fai clic sulla casella dell'Username/Email.")

        # Diamo all'utente 5 secondi di tempo per spostarsi sulla scheda corretta del browser
        secondi_preparazione = 5
        for i in range(secondi_preparazione, 0, -1):
            sys.stdout.write(f"\r⏱️ L'autofill partirà tra: {i}s ... ")
            sys.stdout.flush()
            time.sleep(1)

        # --- CONTROLLO STRINGENTE DELLA FINESTRA ATTIVA ---
        try:
            finestra_attiva = gw.getActiveWindow()
            titolo_finestra = finestra_attiva.title.lower() if finestra_attiva else ""
        except Exception:
            titolo_finestra = ""

        browser_ammessi = ["chrome", "edge", "firefox", "opera", "safari", "brave"]

        # 1. Verifichiamo prima di tutto se l'utente si trova in un browser web
        if not any(browser in titolo_finestra for browser in browser_ammessi):
            print("\n\n❌ ERRORE DI SICUREZZA: Non sei all'interno di un browser web!")
            print(f"L'applicazione attiva era: '{finestra_attiva.title if finestra_attiva else 'Sconosciuta'}'")
            return

        # 2. Eseguiamo il controllo specifico sul dominio con NORMALIZZAZIONE
        # Es: "its-ictpiemonte.it" -> prendiamo "its-ictpiemonte"
        parola_chiave_sito = dominio_pulito.split(".")[0]

        # TRUCCO: Rimuoviamo trattini e spazi per il confronto (es. "its-ictpiemonte" -> "itsictpiemonte")
        parola_chiave_normalizzata = parola_chiave_sito.replace("-", "").replace(" ", "")
        titolo_finestra_normalizzato = titolo_finestra.replace("-", "").replace(" ", "")

        # CONTROLLO AGGIORNATO: Ora confronta i testi normalizzati puliti
        if parola_chiave_normalizzata not in titolo_finestra_normalizzato:
            print(f"\n\n❌ ERRORE DI SICUREZZA (SITO ERRATO): Non sei sulla pagina di {dominio_pulito}!")
            print(f"ℹ️ Il tuo browser è aperto su: '{finestra_attiva.title}'")
            print(f"🔒 Autofill BLOCCATO per evitare di inserire credenziali nel sito sbagliato.")
            return

        # Se i controlli passano, procediamo all'inserimento
        print(f"\n\n🖥️ Controllo superato! Sei correttamente sulla pagina di '{dominio_pulito}'. Inserimento...")

        tasto_incolla = "command" if sys.platform == "darwin" else "ctrl"

        # 1. Copia l'username ed esegue l'incolla automatico
        pyperclip.copy(credenziali["username"])
        pyautogui.hotkey(tasto_incolla, "v")
        time.sleep(0.1)

        # 2. Preme TAB per passare al campo password
        pyautogui.press("tab")
        time.sleep(0.2)

        # 3. Copia la password ed esegue l'incolla automatico
        pyperclip.copy(credenziali["password"])
        pyautogui.hotkey(tasto_incolla, "v")
        time.sleep(0.1)

        # 4. PULIZIA FINALE: Svuota la clipboard
        pyperclip.copy("")
        print("✅ Autofill completato con successo!")

    else:
        print(f"\n❌ Nessuna credenziale trovata per '{dominio_pulito}'.")

def main():
    vault = LocalJsonVault()

    while True:
        print("\n" + "=" * 30)
        print(" 🔒 CLI PASSWORD MANAGER v3.1 🔒")
        print("=" * 30)
        print("1. Aggiungi una password")
        print("2. Cerca una password (Con Autofill Automatico)")
        print("3. Esci")
        print("=" * 30)

        scelta = input("Scegli un'opzione (1-3): ").strip()

        if scelta == "1":
            interfaccia_aggiungi(vault)
        elif scelta == "2":
            interfaccia_cerca(vault)
        elif scelta == "3":
            print("\n👋 Chiusura del gestore password. Alla prossima!")
            break
        else:
            print("\n⚠️ Opzione non valida.")


if __name__ == "__main__":
    main()