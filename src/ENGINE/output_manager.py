"""Gestori dei canali di output fisici per l'erogazione delle password."""

from __future__ import annotations

import time
import threading
import pyautogui
import pyperclip


def eroga_in_clipboard(password: str, secondi: int = 15) -> None:
    """
    Copia la password nella clipboard e avvia un thread in background 
    per sovrascriverla e cancellarla dopo il tempo stabilito.
    """
    pyperclip.copy(password)
    # Avvia il thread in background in modalità daemon
    threading.Thread(target=cancella_clipboard, args=(password, secondi), daemon=True).start()


def cancella_clipboard(password: str, secondi: int):
    time.sleep(secondi)
    # Verifica se negli appunti c'è ancora la password prima di cancellare
    if pyperclip.paste() == password:
        pyperclip.copy("") 

def _ripristina_o_svuota_clipboard(vecchio_contenuto: str):
    """ Ripristina la clipboard dell'utente o la cancella del tutto per sicurezza. """
    if vecchio_contenuto and vecchio_contenuto.strip():
        pyperclip.copy(vecchio_contenuto)
    else:
        # Se non c'era nulla, forziamo la pulizia reale del buffer di Windows/Linux
        pyperclip.copy("")
        # Trick aggiuntivo per determinati OS: pulizia tramite ctypes se necessario,
        # ma pyperclip.copy("") dopo aver iniettato testo di solito basta a sovrascrivere.
        # Per massima sicurezza, iniettiamo uno spazio invisibile o puliamo.
        try:
            import ctypes
            if ctypes.windll.user32.OpenClipboard(None):
                ctypes.windll.user32.EmptyClipboard()
                ctypes.windll.user32.CloseClipboard()
        except Exception:
            # Fallback se non siamo su Windows o i permessi falliscono
            pyperclip.copy(" ")


def eroga_tramite_tastiera(password: str, ritardo_iniziale: float = 3.0) -> None:
    """
    Attende qualche secondo (per permettere all'utente di posizionarsi sul campo di testo)
    e poi digita in automatico la password simulando la tastiera hardware.
    """
    #print(f"[OUTPUT] Autofill avviato. Posizionati sul campo di testo entro {ritardo_iniziale} secondi...")
    time.sleep(ritardo_iniziale)
    
    # Scrive la password in modo sicuro carattere per carattere
    pyautogui.write(password, interval=0.05)
    #print("[OUTPUT] Digitazione completata.")

def esegui_autofill_completo(username: str, password: str) -> None:
    """ Esegue immediatamente l'autofill WEB (l'attesa è già passata). """
    vecchio_contenuto = pyperclip.paste()
    
    # --- USERNAME ---
    pyperclip.copy(username)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.05)
    
    pyautogui.press("tab")
    time.sleep(0.1)
    
    # --- PASSWORD ---
    pyperclip.copy(password)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.05)
    
    _ripristina_o_svuota_clipboard(vecchio_contenuto)

def esegui_autofill_ssh(username: str, host: str, porta: int, password: str) -> None:
    """ Esegue immediatamente l'autofill SSH (l'attesa è già passata). """
    vecchio_contenuto = pyperclip.paste()
    
    # --- COMANDO SSH ---
    comando_ssh = f"ssh {username}@{host} -p {porta}"
    pyperclip.copy(comando_ssh)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.05)
    pyautogui.press("enter")
    
    # Resta questa pausa: serve al server remoto per generare il prompt della password
    time.sleep(1.5)
    
    # --- PASSWORD ---
    pyperclip.copy(password)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.05)
    pyautogui.press("enter")
    
    _ripristina_o_svuota_clipboard(vecchio_contenuto)