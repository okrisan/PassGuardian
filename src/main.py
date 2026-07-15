# src/main.py
"""
PassGuardian :: Entry Point
----------------------------
Avvia l'interfaccia grafica desktop (tema cyberpunk: nero / viola / grigio).

La vecchia interfaccia testuale (CLI) e' stata sostituita da questa GUI ed e'
conservata, invariata, in `main_cli.py` solo come riferimento storico:
per tornare alla versione a riga di comando, esegui quel file al suo posto.
"""
import sys
import os

# Aggiungiamo il percorso di root al sys.path per evitare problemi di moduli
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from GUI.app import run


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(0)
