"""Modello di voce vault per login SSH."""

from __future__ import annotations

from typing import Any
from .base import VaultEntry
from ENGINE.output_manager import eroga_in_clipboard, eroga_tramite_tastiera, esegui_autofill_ssh
import re


@VaultEntry.registra_tipo("ssh")
class SSHLoginEntry(VaultEntry):
    """Voce di credenziali SSH con host e porta di connessione."""

    def __init__(
        self,
        titolo: str,
        username: str,
        password_cifrata: str | bytes,
        host: str,
        port: int = 22,
        proprietario: str = "",
    ) -> None:
        super().__init__(
            titolo=titolo,
            username=username,
            password_cifrata=password_cifrata,
            proprietario=proprietario,
        )
        self.host = host
        self.port = port

    @classmethod
    def from_dict(cls, record: dict[str, Any]) -> SSHLoginEntry:
        """Ricostruisce un'istanza SSH dagli attributi del JSON."""
        return cls(
            titolo=str(record["titolo"]),
            username=str(record["username"]),
            password_cifrata=str(record["password_cifrata"]),
            host=str(record["host"]),
            port=int(record.get("port", 22)),
            proprietario=str(record.get("proprietario", "")),
        )

    def sblocca_credenziali(self, metodo_output: str, password_chiaro: str, **kwargs) -> bool:
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
            "tipo": "ssh",
            "host": self.host,
            "port": self.port
        })
        return dati
    
    @property
    def etichetta_tipo(self) -> str:
        return "🖥️SSH Server"

    @property
    def dettagli_tabella(self) -> str:
        return f"Port: {self.port}"
    
    # RIMUOVI QUESTO IMPORT IN ALTO: from GUI.screens.countdown_dialog import CountdownDialog

    def esegui_autofill(self, callback_attesa: callable = None) -> None:
        """Predispone l'autofill SSH delegando l'attesa al chiamante."""
        azione_finale = lambda: esegui_autofill_ssh(
            username=self.username, 
            host=self.host, 
            porta=self.port, 
            password=self.password_cifrata
        )
        
        if callback_attesa:
            callback_attesa(azione_finale)
        else:
            azione_finale()
        
    def corrisponde_a_ricerca(self, testo: str) -> bool:
        """Verifica se il testo corrisponde a titolo, username o all'IP/Host."""
        t = testo.lower()
        return (
            t in self.titolo.lower() or 
            t in self.username.lower() or 
            t in self.host.lower()
        )

    def valida_indirizzo(self) -> bool:
        """Valida se il campo host è un indirizzo IP valido o un hostname."""
        
        regex_ip = r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        regex_host = r"^([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.*([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])*$"
        h = self.host.strip()
        return bool(re.match(regex_ip, h) or re.match(regex_host, h))