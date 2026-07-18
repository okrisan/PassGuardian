"""Modello di voce vault per login web."""

from __future__ import annotations

from typing import Any
from ENGINE.utils import calcola_distanza_levenshtein
from .base import VaultEntry
from ENGINE.output_manager import eroga_in_clipboard, eroga_tramite_tastiera, esegui_autofill_completo
from GUI.screens.countdown_dialog import CountdownDialog
import re


@VaultEntry.registra_tipo("web")
class WebLoginEntry(VaultEntry):
    """Voce di credenziali web con supporto ai controlli anti-phishing."""

    def __init__(
        self,
        titolo: str,
        username: str,
        password_cifrata: str | bytes,
        url: str,
        proprietario: str = "",
    ) -> None:
        super().__init__(
            titolo=titolo,
            username=username,
            password_cifrata=password_cifrata,
            proprietario=proprietario,
        )
        self.url = url

    @classmethod
    def from_dict(cls, record: dict[str, Any]) -> WebLoginEntry:
        """Ricostruisce un'istanza Web dagli attributi del JSON."""
        return cls(
            titolo=str(record["titolo"]),
            username=str(record["username"]),
            password_cifrata=str(record["password_cifrata"]),
            url=str(record["url"]),
            proprietario=str(record.get("proprietario", "")),
        )

    def sblocca_credenziali(self, metodo_output: str, password_chiaro: str, **kwargs) -> bool:
        url_richiesto = kwargs.get("url_richiesto")

        if url_richiesto:
            url_salvato_str = str(self.url).strip().lower()
            url_richiesto_str = str(url_richiesto).strip().lower()
            distanza = calcola_distanza_levenshtein(url_salvato_str, url_richiesto_str)

            if distanza == 0:
                print(f"[SICUREZZA][WEB] URL verificato con successo.")
            elif 1 <= distanza <= 2:
                print(f"\n[ATTENZIONE][ALLARME PHISHING] Blocco di sicurezza!")
                print(f"L'URL richiesto '{url_richiesto_str}' assomiglia in modo sospetto a quello reale '{url_salvato_str}'.")
                print("L'erogazione della password è stata interrotta per la tua sicurezza.\n")
                return False
            else:
                print(f"[INFO][WEB] L'URL richiesto '{url_richiesto_str}' non corrisponde a questa credenziale ({url_salvato_str}).")
                return False

        
        if metodo_output == "clipboard":
            eroga_in_clipboard(password_chiaro)
        elif metodo_output == "keyboard":
            eroga_tramite_tastiera(password_chiaro)
        else:
            print(f"[ERRORE] Metodo output '{metodo_output}' non supportato.")
            return False

        return True

    def to_dict(self) -> dict[str, Any]:
        dati = super().to_dict()
        dati.update({
            "tipo": "web",
            "url": self.url
        })
        return dati
    
    @property
    def etichetta_tipo(self) -> str:
        return "🌐     Web Site"

    @property
    def dettagli_tabella(self) -> str:
        return f"URL: {self.url}"  # Oppure "N/A"
    
    def esegui_autofill(self, parent_window) -> None:
        """Avvia il conto alla rovescia grafico per l'autofill Web."""
            

        # Lanciamo il popup grafico
        CountdownDialog(parent=parent_window, secondi=3, callback_successo=lambda: esegui_autofill_completo(username=self.username, password=self.password_cifrata))
    
    def corrisponde_a_ricerca(self, testo: str) -> bool:
        """Verifica se il testo è presente nel titolo, username o nell'URL."""
        t = testo.lower()
        return (
            t in self.titolo.lower() or 
            t in self.username.lower() or 
            t in self.url.lower()
        )

    def valida_indirizzo(self) -> bool:
        """Verifica la validità sintattica dell'URL del servizio."""
        
        regex = r"^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$"
        return bool(re.match(regex, self.url.strip().lower()))