"""Classi base del dominio PassGUARDIAN."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Type


class VaultEntry(ABC):
    """Rappresenta una voce astratta del vault delle credenziali."""

    _REGISTRO: dict[str, Type[VaultEntry]] = {}

    def __init__(
        self,
        titolo: str,
        username: str,
        password_cifrata: str | bytes,
        proprietario: str = "",
    ) -> None:
        self.titolo = titolo
        self.username = username
        self.password_cifrata = password_cifrata
        self.proprietario = proprietario  # Collega la credenziale al suo utente proprietario

    @classmethod
    def registra_tipo(cls, nome_tipo: str) -> Any:
        """Decoratore per registrare automaticamente le sottoclassi."""
        def decorator(sottoclasse: Type[VaultEntry]) -> Type[VaultEntry]:
            cls._REGISTRO[nome_tipo] = sottoclasse
            return sottoclasse
        return decorator

    @staticmethod
    def deserializza(record: dict[str, Any]) -> VaultEntry:
        """Trova la classe corretta nel registro e la istanzia polimorficamente."""
        tipo = record.get("tipo")
        if not tipo or tipo not in VaultEntry._REGISTRO:
            raise ValueError(f"Tipo di credenziale sconosciuto o non registrato: {tipo!r}")
        
        return VaultEntry._REGISTRO[tipo].from_dict(record)

    @classmethod
    @abstractmethod
    def from_dict(cls, record: dict[str, Any]) -> VaultEntry:
        """Crea un'istanza della sottoclasse a partire da un dizionario JSON."""

    @abstractmethod
    def sblocca_credenziali(self, metodo_output: str, password_chiaro: str, **kwargs) -> bool:
        """Sblocca le credenziali inviando la password decifrata al canale richiesto."""

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Converte l'istanza in un dizionario per la serializzazione JSON."""
        return {
            "titolo": self.titolo,
            "username": self.username,
            "proprietario": self.proprietario,
        }
    @property
    @abstractmethod
    def etichetta_tipo(self) -> str:
        """Restituisce il nome formattato del tipo di credenziale (es. '🌐 Web Site')."""

    @property
    @abstractmethod
    def dettagli_tabella(self) -> str:
        """Restituisce le informazioni extra da mostrare in tabella (es. 'Porta: 22')."""