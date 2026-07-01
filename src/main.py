# main.py
import time

# Importiamo la logica e il cuore dal pacchetto ENGINE
from ENGINE.auth import esegui_login
from ENGINE.vault import LocalJsonVault

# Importiamo la visualizzazione grafica dal pacchetto GUI
from GUI.splash import stampa_splash_screen
from GUI.interfaccia import (
    mostra_menu_principale,
    interfaccia_aggiungi,
    interfaccia_cerca,
    AZZURRO, NERO, RESET
)


def main():
    # 1. Avvia la Splash Screen iniziale
    stampa_splash_screen()

    # 2. Avvia lo schermo di login master (Controllo accessi)
    esegui_login()

    # 3. Istanzia il database locale per le credenziali
    vault = LocalJsonVault()

    # 4. Ciclo di gestione dell'interfaccia menu
    while True:
        scelta = mostra_menu_principale()

        if scelta == "1":
            interfaccia_aggiungi(vault)
        elif scelta == "2":
            interfaccia_cerca(vault)
        elif scelta == "3":
            print(AZZURRO + "\n👋 Chiusura di PassGuardian. Alla prossima!" + RESET)
            time.sleep(1.0)
            break
        else:
            print(NERO + "\n⚠️ Opzione non valida. Riprova." + RESET)
            time.sleep(1.5)


if __name__ == "__main__":
    main()