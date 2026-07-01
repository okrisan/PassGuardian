# src/GUI/interfaccia.py
import os
import sys
import time
import pyautogui
import pyperclip
import pygetwindow as gw

# Importiamo dal cuore solo il modulo di sicurezza indipendente
from ENGINE.security import PhishingDetector

# --- COSTANTI COLORE ---
NERO = "\033[1;30m"
BLU_SCURO = "\033[1;34m"
AZZURRO = "\033[1;36m"
BIANCO = "\033[1;37m"
RESET = "\033[0m"

# Logo compatto per il Menu
LOGO_MENU = r"""  ██████╗  █████╗ ███████╗███████╗ ██████╗ ██╗   ██╗ █████╗ ██████╗ ██████╗ ██╗ █████╗ ███╗   ██╗
  ██╔══██╗██╔══██╗██╔════╝██╔════╝██╔════╝ ██║   ██║██╔══██╗██╔══██╗██╔══██╗██║██╔══██╗████╗  ██║
  ██████╔╝███████║███████╗███████╗██║  ███╗██║   ██║███████║██████╔╝██║  ██║██║███████║██╔██╗ ██║
  ██╔═══╝ ██╔══██║╚════██║╚════██║██║   ██║██║   ██║██╔══██║██╔══██╗██║  ██║██║██╔══██║██║╚██╗██║
  ██║     ██║  ██║███████║███████║╚██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝██║██║  ██║██║ ╚████║
  ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝"""


def safe_getpass(prompt):
    """Evita il blocco del programma se eseguito in finti terminali (IDE)."""
    from getpass import getpass
    if not sys.stdin.isatty():
        return input(prompt + " (testo visibile nell'IDE): ")
    return getpass(prompt)


def stampa_splash_screen():
    """Configura la finestra e stampa l'ASCII art gotica iniziale."""
    if os.name == 'nt':
        os.system('mode con: cols=150 lines=30')
        os.system('')

    os.system('cls' if os.name == 'nt' else 'clear')

    ascii_art = [
        "  ▄███████▄    ▄████████    ▄████████    ▄████████    ▄██████▄  ███    █▄     ▄████████    ▄████████ ████████▄   ▄█     ▄████████ ███▄▄▄▄   ",
        "  ███    ███   ███    ███   ███    ███   ███    ███   ███    ███ ███    ███   ███    ███   ███    ███ ███    ▀███ ███    ███    ███ ███▀▀▀██▄ ",
        "  ███    ███   ███    ███   ███    █▀    ███    █▀    ███    █▀  ███    ███   ███    ███   ███    ███ ███    ███ ███▌   ███    ███ ███   ███ ",
        "  ███    ███   ███    ███   ███          ███          ▄███        ███    ███   ███    ███   ███    ███ ▄███▄▄▄▄██▀ ███    ███ ███▌   ███    ███ ███   ███ ",
        "▀█████████▀  ▀███████████ ▀███████████ ▀███████████ ▀▀███ ████▄  ███    ███ ▀███████████ ▀▀███▀▀▀▀▀   ███    ███ ███▌ ▀███████████ ███   ███ ",
        "  ███          ███    ███          ███          ███   ███    ███ ███    ███   ███    ███   ███    ███ ███    ███ ███    ███    ███ ███   ███ ",
        "  ███          ███    ███    ▄█    ███    ▄█    ███   ███    ███ ███    ███   ███    ███   ███    ███ ███    ███ ███    ▄███ ███    ███    ███ ███   ███ ",
        " ▄████▀        ███    █▀   ▄████████▀   ▄████████▀     ████████▀  ████████▀     ███    █▀    ███    ███ ████████▀  █▀     ███    █▀   ▀█   █▀  ",
        "                                                                                      ███    ███                                          "
    ]

    print("\n" * 2)
    print(AZZURRO + ascii_art[0] + RESET)
    print(AZZURRO + ascii_art[1] + RESET)
    print(AZZURRO + ascii_art[2] + RESET)
    print(BLU_SCURO + ascii_art[3] + RESET)
    print(BLU_SCURO + ascii_art[4] + RESET)
    print(BLU_SCURO + ascii_art[5] + RESET)
    print(NERO + ascii_art[6] + RESET)
    print(NERO + ascii_art[7] + RESET)
    print(NERO + ascii_art[8] + RESET)

    time.sleep(3.0)
    os.system('cls' if os.name == 'nt' else 'clear')


def mostra_menu_principale():
    """Disegna l'interfaccia grafica fissa del menu e restituisce la scelta dell'utente."""
    os.system('cls' if os.name == 'nt' else 'clear')

    print(
        AZZURRO + "==========================================================================================" + RESET)
    print(AZZURRO + LOGO_MENU + RESET)
    print(
        AZZURRO + "==========================================================================================" + RESET)

    print(
        "\n" + BIANCO + "   [1] Aggiungi una nuova password                  [2] Cerca una password (Autofill)" + RESET)
    print(BIANCO + "   [3] Esci dall'applicazione" + RESET)
    print(
        AZZURRO + "------------------------------------------------------------------------------------------" + RESET)

    return input("\n👉 Scegli un'opzione (1-3): ").strip()


def interfaccia_aggiungi(vault_attivo):
    """Gestisce l'inserimento visivo di una nuova credenziale."""
    print(BIANCO + "\n--- AGGIUNGI NUOVA CREDENZIALE ---" + RESET)
    servizio = input("Inserisci il dominio del sito (es. google.com): ").strip()
    if not servizio:
        print(AZZURRO + "⚠️ Il nome del servizio non può essere vuoto." + RESET)
        return

    detector = PhishingDetector()
    dominio_pulito = detector.estrai_dominio(servizio)

    username = input("Inserisci l'username o l'email: ").strip()
    password = safe_getpass("Inserisci la password: ")

    vault_attivo.salva_credenziale(dominio_pulito, username, password)
    print(AZZURRO + f"✅ Credenziale per '{dominio_pulito}' salvata correttamente." + RESET)
    input("\n⌨️  Premere Invio per tornare al menu principale...")


def interfaccia_cerca(vault_attivo):
    """Gestisce l'interfaccia di ricerca e avvia la routine di Autofill."""
    print(BIANCO + "\n--- CERCA E AUTOFILL (SICURO) ---" + RESET)
    url_ricerca = input("Inserisci il sito/dominio da cercare: ").strip()

    detector = PhishingDetector()
    dominio_pulito = detector.estrai_dominio(url_ricerca)

    sicuro, messaggio = detector.verifica_dominio(url_ricerca)
    credenziali = vault_attivo.cerca_credenziale(dominio_pulito)

    if credenziali:
        print("\n" + BLU_SCURO + "=" * 40 + RESET)
        print(f"🔒 ACCOUNT TROVATO PER: {dominio_pulito}")
        print(BLU_SCURO + "=" * 40 + RESET)
        print(f"👤 Username: {credenziali['username']}")
        print("🔑 Password: [••••••••••••] (Nascosta per sicurezza)")
        print(BLU_SCURO + "-" * 40 + RESET)

        colore_messaggio = AZZURRO if sicuro else NERO
        print(colore_messaggio + f"🛡️ Analisi Sicurezza: {messaggio}" + RESET)
        print(BLU_SCURO + "=" * 40 + RESET)

        if not sicuro:
            print(NERO + f"\n{messaggio}" + RESET)
            conferma = input("⚠️ Vuoi procedere comunque all'autofill? (si/no): ").strip().lower()
            if conferma != "si":
                print(AZZURRO + "❌ Operazione annullata per motivi di sicurezza." + RESET)
                input("\n⌨️  Premere Invio per tornare al menu principale...")
                return

        print(AZZURRO + "\n🚀 MODALITÀ AUTOFILL AVVIATA!")
        print(f"👉 APRI IL BROWSER SULLA PAGINA DI LOGIN DI: {dominio_pulito}")
        print("🎯 Fai clic sulla casella dell'Username/Email.")

        for i in range(5, 0, -1):
            sys.stdout.write(f"\r⏱️ L'autofill partirà tra: {i}s ... ")
            sys.stdout.flush()
            time.sleep(1)

        try:
            finestra_attiva = gw.getActiveWindow()
            titolo_finestra = finestra_attiva.title.lower() if finestra_attiva else ""
        except Exception:
            titolo_finestra = ""

        browser_ammessi = ["chrome", "edge", "firefox", "opera", "safari", "brave"]
        if not any(browser in titolo_finestra for browser in browser_ammessi):
            print(NERO + "\n\n❌ ERRORE DI SICUREZZA: Non sei all'interno di un browser web!" + RESET)
            input("\n⌨️  Premere Invio per tornare al menu principale...")
            return

        parola_chiave_sito = dominio_pulito.split(".")[0]
        parola_chiave_normalizzata = parola_chiave_sito.replace("-", "").replace(" ", "")
        titolo_finestra_normalizzato = titolo_finestra.replace("-", "").replace(" ", "")

        if parola_chiave_normalizzata not in titolo_finestra_normalizzato:
            print(NERO + f"\n\n❌ ERRORE DI SICUREZZA (SITO ERRATO): Non sei sulla pagina di {dominio_pulito}!" + RESET)
            input("\n⌨️  Premere Invio per tornare al menu principale...")
            return

        print(AZZURRO + f"\n\n🖥️ Controllo superato! Inserimento..." + RESET)
        tasto_incolla = "command" if sys.platform == "darwin" else "ctrl"

        pyperclip.copy(credenziali["username"])
        pyautogui.hotkey(tasto_incolla, "v")
        time.sleep(0.1)

        pyautogui.press("tab")
        time.sleep(0.2)

        pyperclip.copy(credenziali["password"])
        pyautogui.hotkey(tasto_incolla, "v")
        time.sleep(0.1)

        pyperclip.copy("")
        print(AZZURRO + "✅ Autofill completato e appunti di sistema ripuliti!" + RESET)
    else:
        print(f"\n❌ Nessuna credenziale trouvata per '{dominio_pulito}'.")

    input("\n⌨️  Premere Invio per tornare al menu principale...")