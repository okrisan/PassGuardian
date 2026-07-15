# src/splash.py
import os
import time

# --- DEFINIZIONE COLORI ANSI ---
NERO = "\033[1;30m"
BLU_SCURO = "\033[1;34m"
AZZURRO = "\033[1;36m"
BIANCO = "\033[1;37m"
RESET = "\033[0m"

LOGO_MENU = r"""  ██████╗  █████╗ ███████╗███████╗ ██████╗ ██╗   ██╗ █████╗ ██████╗ ██████╗ ██╗ █████╗ ███╗   ██╗
  ██╔══██╗██╔══██╗██╔════╝██╔════╝██╔════╝ ██║   ██║██╔══██╗██╔══██╗██╔══██╗██║██╔══██╗████╗  ██║
  ██████╔╝███████║███████╗███████╗██║  ███╗██║   ██║███████║██████╔╝██║  ██║██║███████║██╔██╗ ██║
  ██╔═══╝ ██╔══██║╚════██║╚════██║██║   ██║██║   ██║██╔══██║██╔══██╗██║  ██║██║██╔══██║██║╚██╗██║
  ██║     ██║  ██║███████║███████║╚██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝██║██║  ██║██║ ╚████║
  ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝"""


def stampa_splash_screen():
    """Configura la finestra del terminale e stampa l'ASCII art."""
    # 1. Configurazione finestra per Windows (Forza 150 colonne e 30 righe)
    if os.name == 'nt':
        os.system('mode con: cols=150 lines=30')
        # Forza Windows ad abilitare i colori ANSI sul prompt dei comandi nativo
        os.system('')

    # 2. Pulizia iniziale dello schermo
    os.system('cls' if os.name == 'nt' else 'clear')

    """Pulisce lo schermo, stampa l'ASCII art gotica a sfumature e attende 3 secondi."""
    # Pulizia iniziale dello schermo per un effetto ordinato
    os.system('cls' if os.name == 'nt' else 'clear')

    ascii_art = [
        "  ▄███████▄    ▄████████    ▄████████    ▄████████    ▄██████▄  ███    █▄     ▄████████    ▄████████ ████████▄   ▄█     ▄████████ ███▄▄▄▄   ",
        "  ███    ███   ███    ███   ███    ███   ███    ███   ███    ███ ███    ███   ███    ███   ███    ███ ███    ▀███ ███    ███    ███ ███▀▀▀██▄ ",
        "  ███    ███   ███    ███   ███    █▀    ███    █▀    ███    █▀  ███    ███   ███    ███   ███    ███ ███    ███ ███▌   ███    ███ ███   ███ ",
        "  ███    ███   ███    ███   ███          ███          ▄███       ███    ███   ███    ███   ▄███▄▄▄▄██▀███    ███ ███▌   ███    ███ ███   ███ ",
        "▀█████████▀  ▀███████████ ▀███████████ ▀███████████ ▀▀███ ████▄  ███    ███ ▀███████████ ▀▀███▀▀▀▀▀   ███    ███ ███▌ ▀███████████ ███   ███ ",
        "  ███          ███    ███          ███          ███   ███    ███ ███    ███   ███    ███   ███    ███ ███    ███ ███    ███    ███ ███   ███ ",
        "  ███          ███    ███    ▄█    ███    ▄█    ███   ███    ███ ███    ███   ███    ███   ███    ███ ███    ▄███ ███    ███    ███ ███   ███ ",
        " ▄████▀        ███    █▀   ▄████████▀   ▄████████▀     ████████▀  ████████▀     ███    █▀    ███    ███ ████████▀  █▀     ███    █▀   ▀█   █▀  ",
        "                                                                                      ███    ███                                          "
    ]

    print("\n" * 2)

    # Applicazione della sfumatura verticale
    print(AZZURRO + ascii_art[0] + RESET)
    print(AZZURRO + ascii_art[1] + RESET)
    print(AZZURRO + ascii_art[2] + RESET)
    print(BLU_SCURO + ascii_art[3] + RESET)
    print(BLU_SCURO + ascii_art[4] + RESET)
    print(BLU_SCURO + ascii_art[5] + RESET)
    print(NERO + ascii_art[6] + RESET)
    print(NERO + ascii_art[7] + RESET)
    print(NERO + ascii_art[8] + RESET)

    # Pausa di 3 secondi esatti per mostrare l'applicazione prima del login
    time.sleep(3.0)

    # Pulizia finale prima di passare alla schermata di login/menu del main
    os.system('cls' if os.name == 'nt' else 'clear')