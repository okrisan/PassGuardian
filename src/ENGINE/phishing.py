from ENGINE.utils import calcola_distanza_levenshtein
from ENGINE.models.web import WebLoginEntry
import json
from pathlib import Path

WHITELIST_PATH = Path("database/whitelist.json")

def carica_whitelist_globali() -> list[str]:
    """Carica la whitelist dei siti noti dal file JSON. Ritorna una lista vuota se il file manca."""
    if not WHITELIST_PATH.exists():
        # Fallback di sicurezza se il file viene accidentalmente eliminato
        return ["google.com", "paypal.com", "github.com", "poste.it"]
    
    try:
        with open(WHITELIST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def verifica_antiphishing_estesa(url_richiesto: str, credenziali: list) -> tuple[str, str, any]:
    """
    Analizza l'URL sia contro il Vault dell'utente che contro la Whitelist globale dei brand noti.
    Ritorna una tupla: (stato_esito, dettaglio_messaggio, entità_correlata)
    Stati: "OK_VAULT", "OK_WHITELIST", "PHISHING_VAULT", "PHISHING_BRAND", "NON_TROVATO"
    """
    url_cercato = url_richiesto.strip().lower()
    if not url_cercato:
        return "NON_TROVATO", "URL vuoto", None

    # 1. Controllo di corrispondenza esatta nel Vault
    for entry in credenziali:
        if isinstance(entry, WebLoginEntry):
            if str(entry.url).strip().lower() == url_cercato:
                return "OK_VAULT", f"Corrispondenza esatta trovata per '{entry.titolo}'", entry

    # 2. Controllo di corrispondenza esatta nella Whitelist Globale
    siti_affidabili = carica_whitelist_globali()
    if url_cercato in siti_affidabili:
        return "OK_WHITELIST", f"Il dominio '{url_cercato}' è un brand noto e affidabile.", None

    # 3. Controllo Typosquatting/Phishing contro il Vault
    for entry in credenziali:
        if isinstance(entry, WebLoginEntry):
            distanza = calcola_distanza_levenshtein(str(entry.url).strip().lower(), url_cercato)
            if 1 <= distanza <= 2:
                return "PHISHING_VAULT", f"L'URL imita una tua credenziale salvata: {entry.titolo}", entry

    # 4. Controllo Typosquatting/Phishing contro i Brand Noti della Whitelist
    for sito_noto in siti_affidabili:
        distanza = calcola_distanza_levenshtein(sito_noto, url_cercato)
        if 1 <= distanza <= 2:
            return "PHISHING_BRAND", f"L'URL imita il marchio noto '{sito_noto}'", sito_noto

    return "NON_TROVATO", "Nessun match o minaccia rilevata. Procedi con cautela.", None



def verifica_antiphishing_url(url_richiesto: str, credenziali: list) -> tuple[str, any]:
    """
    Analizza l'URL inserito confrontandolo con le credenziali Web memorizzate.
    Ritorna una tupla: (stato_esito, credenziale_correlata)
    Stati possibili: "OK", "PHISHING", "NON_TROVATO"
    """
    url_richiesto_str = url_richiesto.strip().lower()
    if not url_richiesto_str:
        return "NON_TROVATO", None

    credenziale_sospetta = None

    for entry in credenziali:
        # Il controllo anti-phishing si applica solo alle credenziali Web
        if isinstance(entry, WebLoginEntry):
            url_salvato_str = str(entry.url).strip().lower()
            distanza = calcola_distanza_levenshtein(url_salvato_str, url_richiesto_str)

            if distanza == 0:
                # Corrispondenza esatta trovata! URL sicuro.
                return "OK", entry
            elif 1 <= hasattr(entry, 'url') and distanza <= 2:
                # Trovato un dominio pericolosamente simile (es. g00gle.com vs google.com)
                credenziale_sospetta = entry
                # Non interrompiamo subito, potremmo trovare un match esatto dopo, 
                # ma teniamo traccia del potenziale phishing.

    if credenziale_sospetta:
        return "PHISHING", credenziale_sospetta

    return "NON_TROVATO", None