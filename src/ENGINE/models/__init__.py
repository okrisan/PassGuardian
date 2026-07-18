"""API pubblica dei modelli del dominio PassGUARDIAN."""

from .base import VaultEntry
from .ssh import SSHLoginEntry
from .web import WebLoginEntry

__all__ = ["VaultEntry", "WebLoginEntry", "SSHLoginEntry"]
