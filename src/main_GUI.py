# main_GUI.py
import sys
import os

# Aggiungiamo la cartella "src" al path di ricerca di Python
cartella_corrente = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cartella_corrente, "src"))

# Ora Python troverà correttamente il modulo GUI dentro src!
from GUI.app import run

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(0)