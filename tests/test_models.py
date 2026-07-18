from __future__ import annotations

from ENGINE.models import SSHLoginEntry, VaultEntry, WebLoginEntry
import ENGINE.models.ssh as ssh_module
import ENGINE.models.web as web_module


def test_deserializza_ricostruisce_la_sottoclasse_corretta() -> None:
    web_record = {
        "tipo": "web",
        "titolo": "GitHub",
        "username": "alice",
        "password_cifrata": "secret-web",
        "proprietario": "alice",
        "url": "https://github.com",
    }
    ssh_record = {
        "tipo": "ssh",
        "titolo": "Server",
        "username": "root",
        "password_cifrata": "secret-ssh",
        "proprietario": "alice",
        "host": "192.168.1.10",
        "port": 2222,
    }

    web_entry = VaultEntry.deserializza(web_record)
    ssh_entry = VaultEntry.deserializza(ssh_record)

    assert isinstance(web_entry, WebLoginEntry)
    assert isinstance(ssh_entry, SSHLoginEntry)
    assert web_entry.dettagli_tabella == "URL: https://github.com"
    assert ssh_entry.dettagli_tabella == "Port: 2222"


def test_polymorphic_unlock_accepts_mixed_vault_entries(monkeypatch) -> None:
    calls: list[tuple[str, str]] = []

    monkeypatch.setattr(web_module, "eroga_in_clipboard", lambda password: calls.append(("web", password)))
    monkeypatch.setattr(ssh_module, "eroga_in_clipboard", lambda password: calls.append(("ssh", password)))

    entries: list[VaultEntry] = [
        WebLoginEntry("GitHub", "alice", "web-password", "https://github.com"),
        SSHLoginEntry("Server", "root", "ssh-password", "192.168.1.10", 22),
    ]

    results = [entry.sblocca_credenziali("clipboard", entry.password_cifrata) for entry in entries]

    assert results == [True, True]
    assert calls == [("web", "web-password"), ("ssh", "ssh-password")]


def test_web_autofill_delegates_to_callback(monkeypatch) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        web_module,
        "esegui_autofill_completo",
        lambda username, password: captured.update({"username": username, "password": password}),
    )

    entry = WebLoginEntry("GitHub", "alice", "web-password", "https://github.com")

    def fake_wait(callback):
        captured["callback"] = callback

    entry.esegui_autofill(callback_attesa=fake_wait)
    callback = captured["callback"]
    assert callable(callback)

    callback()

    assert captured["username"] == "alice"
    assert captured["password"] == "web-password"