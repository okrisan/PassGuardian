# main.py
import time
import sys

# Importiamo la logica dal pacchetto ENGINE
import ENGINE.auth as auth
from ENGINE.vault import LocalJsonVault

# Importiamo le interfacce dal pacchetto GUI
from GUI.interfaccia import (
    stampa_splash_screen,
    mostra_menu_principale,
    interfaccia_aggiungi,
    interfaccia_cerca,
    interfaccia_modifica,
    interfaccia_mostra_in_chiaro_tabellare,
    interfaccia_mostra_utenti_sistema,
    safe_getpass,
    AZZURRO, NERO, BIANCO, RESET
)


def main():
    # 1. Avvia la Splash Screen iniziale
    stampa_splash_screen()

    # Istanzia il database locale per le credenziali fuori dai cicli
    vault = LocalJsonVault()

    # CICLO GLOBALE: Permette il cambio utente infinito senza chiudere l'app
    while True:
        tentativi = 0
        username_loggato = None

        # Schermo di login master centralizzato con blocco di sicurezza (Max 3 tentativi)
        print("\n" + "=" * 30)
        print("      PASSGUARDIAN LOGIN      ")
        print("=" * 30)

        while True:
            username_inserito = input("Username: ").strip()
            password_inserita = safe_getpass("Master Password (caratteri nascosti): ").strip()

            ruolo = auth.verifica_login(username_inserito, password_inserita)
            if ruolo:
                auth.ruolo_attuale = ruolo
                username_loggato = username_inserito
                print(f"\n[OK] Login effettuato con successo! Benvenuto {username_loggato}.")
                time.sleep(1.0)
                break
            else:
                tentativi += 1
                if tentativi >= 3:
                    print(NERO + "\n⚠️ Troppi tentativi errati. Chiusura di sicurezza." + RESET)
                    time.sleep(2.0)
                    sys.exit()
                print(AZZURRO + f"\n🔄 Credenziali errate. Tentativi rimasti: {3 - tentativi}\n" + RESET)

        # CICLO DEL MENU PRINCIPALE
        continua_con_questo_utente = True
        while continua_con_questo_utente:
            scelta = mostra_menu_principale(username_loggato, auth.ruolo_attuale)

            if scelta == "1":
                interfaccia_aggiungi(vault, username_loggato)

            elif scelta == "2":
                interfaccia_cerca(vault, username_loggato)

            elif scelta == "3":
                interfaccia_modifica(vault, username_loggato)

            elif scelta == "4":
                if auth.ruolo_attuale == "super_user":
                    interfaccia_mostra_in_chiaro_tabellare(vault)
                else:
                    print(
                        NERO + "\n⛔ ACCESSO NEGATO: Questa operazione richiede privilegi Master (Super User)." + RESET)
                    time.sleep(2.0)

            elif scelta == "5":
                print(BIANCO + "\n--- REGISTRAZIONE NUOVO UTENTE ---" + RESET)
                nuovo_user = input("Scegli un Username: ").strip()
                if not nuovo_user:
                    print(NERO + "⚠️ L'username non può essere vuoto." + RESET)
                else:
                    nuova_pwd = safe_getpass("Scegli una Master Password: ")
                    if auth.aggiungi_nuovo_utente(nuovo_user, nuova_pwd):
                        print(AZZURRO + f"✅ Utente '{nuovo_user}' creato con successo!" + RESET)
                    else:
                        print(NERO + "❌ Errore: Questo username è già registrato." + RESET)
                time.sleep(2.0)

            elif scelta == "6":
                print(BIANCO + "\n--- RIMOZIONE UTENTE ---" + RESET)
                if auth.ruolo_attuale == "super_user":
                    interfaccia_mostra_utenti_sistema()

                    target_user = input("Inserisci l'username dell'utente da ELIMINARE: ").strip()
                    if auth.elimina_utente(target_user):
                        print(AZZURRO + f"███ Utente '{target_user}' rimosso definitivamente dal sistema." + RESET)
                    else:
                        print(
                            NERO + "❌ Impossibile eliminare l'utente (non esiste o stai tentando di eliminare l'admin supremo)." + RESET)
                else:
                    print(
                        NERO + "\n⛔ ACCESSO NEGATO: Solo l'account amministratore Master può eliminare gli utenti." + RESET)
                time.sleep(2.5)


            elif scelta == "7":

                print(AZZURRO + f"\n🔄 Disconnessione in corso da {username_loggato}..." + RESET)

                time.sleep(1.0)

                # Pulisce completamente lo schermo prima di mostrare il nuovo login

                import os

                os.system('cls' if os.name == 'nt' else 'clear')

                # Rompe il ciclo del menu corrente, tornando al form di login globale

                continua_con_questo_utente = False

            elif scelta == "8":
                print(AZZURRO + "\n👋 Chiusura di PassGuardian. Alla prossima!" + RESET)
                time.sleep(1.0)
                sys.exit()  # Chiude completamente l'intera applicazione

            else:
                print(NERO + "\n⚠️ Opzione non valida. Riprova." + RESET)
                time.sleep(1.5)


if __name__ == "__main__":
    main()