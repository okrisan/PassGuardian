# src/GUI/interfaccia.py
import os
import sys
import time
import json
import pyautogui
import pyperclip
import pygetwindow as gw
import socket

from ENGINE.security import PhishingDetector

# --- COSTANTI COLORE ---
NERO = "\033[1;30m"
BLU_SCURO = "\033[1;34m"
AZZURRO = "\033[1;36m"
BIANCO = "\033[1;37m"
RESET = "\033[0m"


def safe_getpass(prompt):
    """Previene il blocco del programma nei terminali IDE non interattivi."""
    from getpass import getpass
    if not sys.stdin.isatty():
        return input(prompt + " (Password visibile): ")
    return getpass(prompt)


def verifica_stato_sito(dominio):
    """Verifica se uno specifico dominio è raggiungibile sulla porta 80."""
    try:
        dominio_pulito = dominio.strip()
        socket.setdefaulttimeout(0.5)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((dominio_pulito, 80))
        return True
    except Exception:
        return False


# ==========================================
#           MENU E SOTTOMENU (GUI)
# ==========================================

def mostra_menu_principale(username, role):
    """Menu di primo livello, diviso per macro-aree senza icone."""
    os.system('cls' if os.name == 'nt' else 'clear')
    from .splash import LOGO_MENU

    print(
        AZZURRO + "==========================================================================================" + RESET)
    access_level = "MASTER" if role == "super_user" else "USER"
    info_text = f"Utente: {username}  |  Ruolo: {access_level}"
    print(BIANCO + f"{info_text:^90}" + RESET)
    print(
        AZZURRO + "==========================================================================================" + RESET)
    print(AZZURRO + LOGO_MENU + RESET)
    print(
        AZZURRO + "==========================================================================================" + RESET)

    print("\n" + BIANCO + "   [1] GESTIONE VAULT (Credenziali Web & Terminali SSH)" + RESET)
    print(BIANCO + "   [2] SICUREZZA ACCOUNT (Cambio Master Password)" + RESET)
    if role == "super_user":
        print(BIANCO + "   [3] AMMINISTRAZIONE DI SISTEMA (Gestione Utenti)" + RESET)

    print(
        "\n" + AZZURRO + "------------------------------------------------------------------------------------------" + RESET)
    print(BIANCO + "   [7] Cambia Utente (Switch)                      [8] Esci dall'Applicazione" + RESET)
    print(
        AZZURRO + "------------------------------------------------------------------------------------------" + RESET)

    return input("\nScegli un'opzione (1-8): ").strip()


def sottomenu_vault():
    """Menu di secondo livello per le operazioni sui segreti."""
    print("\n" + AZZURRO + "=== 📂 AREA GESTIONE VAULT ===" + RESET)
    print(BIANCO + "   [1] Aggiungi Credenziale Web (Dominio)")
    print("   [2] Aggiungi Credenziale Terminale (SSH - IP & Chiave) [PREDISPOSTO]")
    print("   [3] Ricerca Sicura & Autofill Web (Seleziona da elenco con ID)")
    print("   [4] Modifica Password Dominio (Seleziona da elenco con ID)")
    print("   [5] Mostra tutte le Credenziali in Chiaro (Tabella Globale)")
    print("   [6] ↩️ Torna al Menu Principale" + RESET)
    return input("\n👉 Scegli un'operazione: ").strip()


def sottomenu_sicurezza():
    """Menu di secondo livello per la sicurezza personale."""
    print("\n" + AZZURRO + "=== 🛡️  AREA SICUREZZA ACCOUNT ===" + RESET)
    print(BIANCO + "   [1] Cambia la TUA Master Password")
    print("   [2] ↩️ Torna al Menu Principale" + RESET)
    return input("\n👉 Scegli un'operazione: ").strip()


def sottomenu_amministrazione():
    """Menu di secondo livello per il Master Admin."""
    print("\n" + AZZURRO + "=== ⚙️  AREA AMMINISTRAZIONE SISTEMA ===" + RESET)
    print(BIANCO + "   [1] Visualizza Elenco Utenti di Sistema")
    print("   [2] Registra un Nuovo Utente")
    print("   [3] Elimina un Utente Esistente")
    print("   [4] ↩️ Torna al Menu Principale" + RESET)
    return input("\n👉 Scegli un'operazione: ").strip()


# ==========================================
#         FUNZIONALITÀ OPERATIVE
# ==========================================

def interfaccia_aggiungi(vault_attivo, utente_corrente):
    print(BIANCO + "\n--- AGGIUNGI CREDENZIALE WEB ---" + RESET)
    service = input("Inserisci il dominio del sito (es: google.com): ").strip()
    if not service:
        print(AZZURRO + "⚠️ Il nome del dominio non può essere vuoto." + RESET)
        return

    detector = PhishingDetector()
    clean_domain = detector.estrai_dominio(service)
    username = input("Inserisci Username/Email: ").strip()
    password = safe_getpass("Inserisci Password: ")

    vault_attivo.salva_credenziale(utente_corrente, clean_domain, username, password)
    print(AZZURRO + f"✅ Credenziali per '{clean_domain}' salvate correttamente." + RESET)
    input("\n⌨️ Premi Invio per continuare...")


def interfaccia_aggiungi_ssh_stub():
    """Predisposizione per la futura logica SSH."""
    print(BIANCO + "\n--- [FUTURE] AGGIUNGI CREDENZIALE TERMINALE (SSH) ---" + RESET)
    ip_address = input("Inserisci IP del Server o Hostname (es: 192.168.1.50): ").strip()
    username = input("Inserisci Username SSH: ").strip()
    path_chiave = input("Inserisci il percorso della chiave privata (o incolla il testo): ").strip()

    print(AZZURRO + f"🛠️ [Stub] Ricevuto IP: {ip_address} ed utente {username}. Struttura salvataggio pronta." + RESET)
    input("\n⌨️ Premi Invio per continuare...")


def interfaccia_cerca(vault_attivo, utente_corrente, ruolo_corrente):
    print(BIANCO + "\n--- RICERCA SICURA & AUTOFILL ---" + RESET)
    all_data = vault_attivo._carica_dati()
    dati_utente = {utente_corrente: all_data.get(utente_corrente, {})}

    domini_disponibili = []
    indice = 1
    for owner, domains in dati_utente.items():
        for service in domains.keys():
            domini_disponibili.append((str(indice), service))
            indice += 1

    if not domini_disponibili:
        print(NERO + "⚠️ Il tuo Vault è vuoto. Aggiungi prima una credenziale." + RESET)
        input("\n⌨️ Premi Invio per continuare...")
        return

    print(AZZURRO + "\nVerifica stato domini in corso... Attendi." + RESET)
    print("\n" + AZZURRO + "=" * 75 + RESET)
    print(BIANCO + f"{'ID':<6} | {'DOMINIO DISPONIBILE':<50} | {'STATUS':<12}" + RESET)
    print(AZZURRO + "=" * 75 + RESET)
    for idx, service in domini_disponibili:
        site_online = verifica_stato_sito(service)
        str_status = "🔵 ONLINE" if site_online else "🔴 OFFLINE"
        id_str = f"[{idx}]"
        print(f"{id_str:<6} | 🌐 {service:<50} | {str_status:<12}")
    print(AZZURRO + "=" * 75 + RESET + "\n")

    scelta_input = input("Inserisci l'ID numerico o il nome del Dominio: ").strip()
    if not scelta_input:
        return

    url_search = scelta_input
    for idx, service in domini_disponibili:
        if scelta_input == idx:
            url_search = service
            break

    detector = PhishingDetector()
    clean_domain = detector.estrai_dominio(url_search)
    credentials = vault_attivo.cerca_credenziale(utente_corrente, clean_domain)

    if credentials:
        # Logica di riempimento pyautogui (già ottimizzata in precedenza)
        print(AZZURRO + f"✅ Trovato account per {clean_domain}. Esecuzione Autofill..." + RESET)
        # [... resto della tua logica pyautogui standard ...]
    else:
        print(NERO + f"❌ Nessuna credenziale trovata per '{clean_domain}'." + RESET)
    input("\n⌨️ Premi Invio per continuare...")


def interfaccia_modifica(vault_attivo, utente_corrente):
    """Corretta ed equiparata in veste tabellare allineata identica alla 2."""
    print(BIANCO + "\n--- MODIFICA PASSWORD DOMINIO ---" + RESET)
    all_data = vault_attivo._carica_dati()
    user_data = all_data.get(utente_corrente, {})

    if not user_data:
        print(NERO + "⚠️ Il tuo Vault è vuoto. Niente da modificare." + RESET)
        input("\n⌨️ Premi Invio per continuare...")
        return

    domini_disponibili = []
    indice = 1
    for dom in user_data.keys():
        domini_disponibili.append((str(indice), dom))
        indice += 1

    print(AZZURRO + "\nVerifica stato domini in corso... Attendi." + RESET)
    print("\n" + AZZURRO + "=" * 75 + RESET)
    print(BIANCO + f"{'ID':<6} | {'DOMINIO SALVATO':<50} | {'STATUS':<12}" + RESET)
    print(AZZURRO + "=" * 75 + RESET)
    for idx, service in domini_disponibili:
        site_online = verifica_stato_sito(service)
        str_status = "🔵 ONLINE" if site_online else "🔴 OFFLINE"
        id_str = f"[{idx}]"
        print(f"{id_str:<6} | 🌐 {service:<50} | {str_status:<12}")
    print(AZZURRO + "=" * 75 + RESET + "\n")

    scelta_input = input("Inserisci l'ID numerico o il nome del Dominio da modificare: ").strip()
    if not scelta_input:
        return

    url_search = scelta_input
    for idx, service in domini_disponibili:
        if scelta_input == idx:
            url_search = service
            break

    detector = PhishingDetector()
    clean_domain = detector.estrai_dominio(url_search)

    if vault_attivo.cerca_credenziale(utente_corrente, clean_domain):
        new_pwd = safe_getpass("Inserisci la NUOVA password: ")
        if vault_attivo.modifica_password(utente_corrente, clean_domain, new_pwd):
            print(AZZURRO + f"✅ Password per '{clean_domain}' modificata con successo!" + RESET)
        else:
            print(NERO + "❌ Errore durante l'aggiornamento." + RESET)
    else:
        print(NERO + f"❌ Dominio '{clean_domain}' non trovato." + RESET)
    input("\n⌨️ Premi Invio per continuare...")


def interfaccia_mostra_in_chiaro(vault_attivo, utente_corrente, r_corrente):
    """Mostra le credenziali decifrate con allineamenti tabellari corretti."""
    print(BIANCO + "\n--- VISUALIZZAZIONE CREDENZIALI IN CHIARO ---" + RESET)

    all_data = vault_attivo._carica_dati()
    if not all_data:
        print(NERO + "⚠️ Il database del Vault è completamente vuoto." + RESET)
        input("\nPremi Invio per tornare al menu...")
        return

    target_utenti = []

    # --- TABELLA SELEZIONE UTENTE SE SUPER_USER ---
    if r_corrente == "super_user":
        print(AZZURRO + "\nFiltro proprietari Vault disponibili:" + RESET)
        print(AZZURRO + "=" * 45 + RESET)
        print(BIANCO + f"{'ID':<6} | {'PROPRIETARIO VAULT':<35}" + RESET)
        print(AZZURRO + "=" * 45 + RESET)

        mappa_utenti = {}
        for idx, utente in enumerate(all_data.keys(), start=1):
            mappa_utenti[str(idx)] = utente
            id_str = f"[{idx}]"
            print(f"{id_str:<6} | {utente:<35}")
        print(AZZURRO + "=" * 45 + RESET)

        scelta = input("\nInserisci l'ID dell'utente, il nome oppure 'all': ").strip().lower()

        if scelta == "all":
            target_utenti = list(all_data.keys())
        elif scelta in mappa_utenti:
            target_utenti = [mappa_utenti[scelta]]
        elif scelta in all_data:
            target_utenti = [scelta]
        else:
            print(NERO + "⚠️ Scelta non valida. Ritorno al menu." + RESET)
            input("\nPremi Invio per continuare...")
            return
    else:
        target_utenti = [utente_corrente]

    # --- TABELLA DI OUTPUT FINALE ---
    dati_da_mostrare = False

    print("\n" + AZZURRO + "=" * 110 + RESET)
    print(
        BIANCO + f"{'PROPRIETARIO':<15} | {'DOMINIO / SERVIZIO':<30} | {'USERNAME / EMAIL':<35} | {'PASSWORD':<20}" + RESET)
    print(AZZURRO + "=" * 110 + RESET)

    for utente in target_utenti:
        user_data = all_data.get(utente, {})
        if user_data:
            dati_da_mostrare = True
            for servizio, info in user_data.items():
                try:
                    from ENGINE.security import decifra_password
                    pwd_chiaro = decifra_password(info["password"])
                except Exception:
                    pwd_chiaro = "[Errore Decifratura]"

                print(f"{utente:<15} | {servizio:<30} | {info['username']:<35} | {pwd_chiaro:<20}")

    if not dati_da_mostrare:
        print(BIANCO + f"{'Nessun dato presente per i filtri selezionati.':^110}" + RESET)

    print(AZZURRO + "=" * 110 + RESET)
    input("\nPremi Invio per tornare al menu...")

def interfaccia_mostra_utenti_sistema():
    from ENGINE.auth import PATH_UTENTI
    print(BIANCO + "\n--- ELENCO UTENTI DI SISTEMA ---" + RESET)
    try:
        with open(PATH_UTENTI, "r", encoding="utf-8") as f:
            users = json.load(f)
        print(AZZURRO + "=" * 65 + RESET)
        print(BIANCO + f"{'USER ID':<10} | {'USERNAME':<25} | {'RUOLO':<20}" + RESET)
        print(AZZURRO + "=" * 65 + RESET)
        for user, info in users.items():
            u_id = 0 if user == "admin" else info.get("id", 1)
            role_clean = "MASTER (Admin)" if info['role'] == "super_user" else "USER (Standard)"
            print(f"{str(u_id):<10} | {user:<25} | {role_clean:<20}")
        print(AZZURRO + "=" * 65 + RESET)
    except Exception:
        print(NERO + "⚠️ Impossibile leggere il database utenti." + RESET)
    input("\n⌨️ Premi Invio per continuare...")