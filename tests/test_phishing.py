from __future__ import annotations

import ENGINE.phishing as phishing
from ENGINE.models import WebLoginEntry


def test_verifica_antiphishing_url_exact_match_returns_ok() -> None:
    entry = WebLoginEntry("GitHub", "alice", "secret", "github.com")

    status, related = phishing.verifica_antiphishing_url("github.com", [entry])

    assert status == "OK"
    assert related is entry


def test_verifica_antiphishing_url_detects_similar_domain_as_phishing() -> None:
    entry = WebLoginEntry("GitHub", "alice", "secret", "github.com")

    status, related = phishing.verifica_antiphishing_url("githab.com", [entry])

    assert status == "PHISHING"
    assert related is entry


def test_verifica_antiphishing_estesa_uses_whitelist_and_vault(monkeypatch) -> None:
    entry = WebLoginEntry("GitHub", "alice", "secret", "github.com")
    monkeypatch.setattr(phishing, "carica_whitelist_globali", lambda: ["github.com", "paypal.com"])

    ok_status, ok_message, ok_related = phishing.verifica_antiphishing_estesa("github.com", [entry])
    brand_status, brand_message, brand_related = phishing.verifica_antiphishing_estesa("githab.com", [])

    assert ok_status == "OK_VAULT"
    assert "Corrispondenza esatta" in ok_message
    assert ok_related is entry

    assert brand_status == "PHISHING_BRAND"
    assert "marchio noto" in brand_message
    assert brand_related == "github.com"