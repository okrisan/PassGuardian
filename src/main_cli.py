# src/main.py
import sys
import os
import time

# Aggiungiamo il percorso di root al sys.path per evitare problemi di moduli
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Importiamo auth come modulo globale e LocalJsonVault dal modulo vault
import ENGINE.auth as auth
from ENGINE.vault import LocalJsonVault
from GUI.splash import stampa_splash_screen

from GUI.interfaccia import (
    NERO, AZZURRO, BIANCO, RESET,
    safe_getpass,
    mostra_menu_principale,
    sottomenu_vault,
    sottomenu_sicurezza,
    sottomenu_amministrazione,
    interfaccia_aggiungi,
    interfaccia_aggiungi_ssh_stub,
    interfaccia_cerca,
    interfaccia_modifica,
    interfaccia_mostra_in_chiaro,
    interfaccia_mostra_utenti_sistema
)

# Variabile globale di sessione per tracciare il ruolo dell'utente loggato
ruolo_attuale = None


def esegui_login():
    """Gestisce la schermata di login iniziale basata sulle funzioni globali di auth.py."""
    global ruolo_attuale
    os.system('cls' if os.name == 'nt' else 'clear')
    print(AZZURRO + "==============================" + RESET)
    print(BIANCO + "      PASSGUARDIAN LOGIN      " + RESET)
    print(AZZURRO + "==============================" + RESET)

    username = input("Username: ").strip()
    if not username:
        return None

    password = safe_getpass("Master Password: ")

    # Chiamata alla funzione globale del tuo auth.py
    ruolo = auth.verifica_login(username, password)

    if ruolo:
        ruolo_attuale = ruolo  # Salviamo il ruolo per i controlli nei sottomenu
        print(AZZURRO + f"\n✅ Accesso consentito! Benvenuto {username}." + RESET)
        time.sleep(1.5)
        return username
    else:
        print(NERO + "\n❌ Credenziali errate o utente inesistente." + RESET)
        time.sleep(2)
        return None


def main():
    global ruolo_attuale

    # 1. Mostra la splash screen animata all'avvio
    stampa_splash_screen()

    # 2. Inizializzazione dell'oggetto Vault con il nome corretto della classe
    vault = LocalJsonVault()

    while True:
        username_loggato = esegui_login()

        if not username_loggato:
            continue

        while True:
            # Passiamo ruolo_attuale al menu principale
            scelta = mostra_menu_principale(username_loggato, ruolo_attuale)

            # --------------------------------------------------------
            # [1] AREA GESTIONE VAULT (SITI WEB & SSH)
            # --------------------------------------------------------
            if scelta == "1":
                while True:
                    op_vault = sottomenu_vault()
                    if op_vault == "1":
                        interfaccia_aggiungi(vault, username_loggato)
                    elif op_vault == "2":
                        interfaccia_aggiungi_ssh_stub()
                    elif op_vault == "3":
                        interfaccia_cerca(vault, username_loggato, ruolo_attuale)
                    elif op_vault == "4":
                        interfaccia_modifica(vault, username_loggato)
                    elif op_vault == "5":
                        interfaccia_mostra_in_chiaro(vault, username_loggato, ruolo_attuale)
                    elif op_vault == "6":
                        break

            # --------------------------------------------------------
            # [2] AREA SICUREZZA ACCOUNT
            # --------------------------------------------------------
            elif scelta == "2":
                while True:
                    op_sicurezza = sottomenu_sicurezza()
                    if op_sicurezza == "1":
                        print(BIANCO + "\n--- CAMBIO DELLA MASTER PASSWORD ---" + RESET)
                        nuova_password = safe_getpass("Inserisci la NUOVA Master Password: ")
                        conferma_password = safe_getpass("Conferma la NUOVA Master Password: ")

                        if nuova_password != conferma_password:
                            print(NERO + "❌ Le password non coincidono!" + RESET)
                        elif len(nuova_password) < 8:
                            print(NERO + "⚠️ Password troppo corta! Minimo 8 caratteri." + RESET)
                        else:
                            if auth.aggiorna_password_utente(username_loggato, nuova_password):
                                print(
                                    AZZURRO + "✅ Master Password aggiornata con successo! Sarà attiva al prossimo login." + RESET)
                            else:
                                print(NERO + "❌ Errore durante il salvataggio." + RESET)
                        input("\n⌨️ Premi Invio per continuare...")

                    elif op_sicurezza == "2":
                        break

            # --------------------------------------------------------
            # [3] AREA AMMINISTRAZIONE DI SISTEMA (SOLO ADMIN)
            # --------------------------------------------------------
            elif scelta == "3":
                if ruolo_attuale == "super_user":
                    while True:
                        op_admin = sottomenu_amministrazione()
                        if op_admin == "1":
                            interfaccia_mostra_utenti_sistema()
                        elif op_admin == "2":
                            print(BIANCO + "\n--- REGISTRA NUOVO UTENTE ---" + RESET)
                            nuovo_user = input("Inserisci Username: ").strip()
                            nuova_pass = safe_getpass("Inserisci Password: ")
                            if nuovo_user and nuova_pass:
                                if auth.aggiungi_nuovo_utente(nuovo_user, nuova_pass):
                                    print(AZZURRO + f"✅ Utente '{nuovo_user}' registrato con successo." + RESET)
                                else:
                                    print(NERO + "❌ Errore: l'utente esiste già o database non raggiungibile." + RESET)
                            input("\n⌨️ Premi Invio per continuare...")
                        elif op_admin == "3":
                            print(BIANCO + "\n--- ELIMINA UTENTE ---" + RESET)
                            user_da_eliminare = input("Inserisci Username da rimuovere: ").strip()
                            if user_da_eliminare:
                                if auth.elimina_utente(user_da_eliminare):
                                    print(AZZURRO + f"✅ Utente '{user_da_eliminare}' eliminato con successo." + RESET)
                                else:
                                    print(
                                        NERO + "❌ Impossibile eliminare l'utente (l'admin non può essere rimosso)." + RESET)
                            input("\n⌨️ Premi Invio per continuare...")
                        elif op_admin == "4":
                            break
                else:
                    print(NERO + "\n⚠️ Opzione non consentita. Permessi amministrativi mancanti." + RESET)
                    time.sleep(2)

            # --------------------------------------------------------
            # [7] CAMBIA UTENTE (SWITCH SESSIONE)
            # --------------------------------------------------------
            elif scelta == "7":
                print(AZZURRO + "\n🔄 Disconnessione in corso..." + RESET)
                ruolo_attuale = None  # Resetta il ruolo di sessione
                time.sleep(1)
                break

            # --------------------------------------------------------
            # [8] ESCI DALL'APPLICAZIONE
            # --------------------------------------------------------
            elif scelta == "8":
                print(AZZURRO + "\n👋 Grazie per aver utilizzato PassGuardian. Chiusura..." + RESET)
                sys.exit(0)

            else:
                print(NERO + "\n⚠️ Opzione non valida. Riprova." + RESET)
                time.sleep(1.5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Chiusura improvvisa rilevata. Uscita in sicurezza.")
        sys.exit(0)