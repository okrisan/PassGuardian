from __future__ import annotations

from pathlib import Path

from ENGINE.models import SSHLoginEntry, WebLoginEntry
from ENGINE.storage import VaultStorage


def test_storage_registers_users_and_rejects_duplicates(tmp_path) -> None:
    storage = VaultStorage(tmp_path / "vault.json")

    assert storage.registra_utente("Alice", "Master-123!") is True
    assert storage.registra_utente("alice", "Master-123!") is False
    assert storage.verifica_utente("ALICE", "Master-123!") is True
    assert storage.verifica_utente("alice", "wrong-password") is False


def test_storage_saves_and_loads_decrypted_credentials(tmp_path) -> None:
    storage = VaultStorage(tmp_path / "vault.json")
    storage.registra_utente("alice", "Master-123!")

    web_entry = WebLoginEntry("GitHub", "alice", "web-password", "https://github.com", proprietario="alice")
    ssh_entry = SSHLoginEntry("Server", "root", "ssh-password", "192.168.1.10", 2222, proprietario="alice")

    storage.salva_credenziale(web_entry, "Master-123!", "alice")
    storage.salva_credenziale(ssh_entry, "Master-123!", "alice")

    loaded_entries = storage.carica_credenziali("Master-123!", "alice")

    assert len(loaded_entries) == 2
    assert isinstance(loaded_entries[0], WebLoginEntry)
    assert isinstance(loaded_entries[1], SSHLoginEntry)
    assert loaded_entries[0].password_cifrata == "web-password"
    assert loaded_entries[1].password_cifrata == "ssh-password"


def test_storage_changes_master_password_and_reecrypts_records(tmp_path) -> None:
    storage = VaultStorage(tmp_path / "vault.json")
    storage.registra_utente("alice", "Old-Password-1")

    entry = WebLoginEntry("GitHub", "alice", "web-password", "https://github.com", proprietario="alice")
    storage.salva_credenziale(entry, "Old-Password-1", "alice")

    assert storage.cambia_master_password("alice", "Old-Password-1", "New-Password-2") is True
    assert storage.verifica_utente("alice", "Old-Password-1") is False
    assert storage.verifica_utente("alice", "New-Password-2") is True

    loaded_entries = storage.carica_credenziali("New-Password-2", "alice")
    assert len(loaded_entries) == 1
    assert loaded_entries[0].password_cifrata == "web-password"


def test_storage_rejects_duplicate_credentials_for_same_owner(tmp_path) -> None:
    storage = VaultStorage(tmp_path / "vault.json")
    storage.registra_utente("alice", "Master-123!")

    entry = WebLoginEntry("GitHub", "alice", "web-password", "https://github.com", proprietario="alice")
    storage.salva_credenziale(entry, "Master-123!", "alice")

    duplicate = WebLoginEntry("GitHub", "alice", "another-password", "https://github.com", proprietario="alice")

    assert storage.esiste_credenziale("GitHub", "alice", "alice") is True

    try:
        storage.salva_credenziale(duplicate, "Master-123!", "alice")
    except ValueError as exc:
        assert "Esiste già una credenziale" in str(exc)
    else:
        raise AssertionError("Expected ValueError for duplicate credential")