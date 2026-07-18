import pytest

from ENGINE.security import cifra_password, decifra_password


def test_password_roundtrip_with_master_password() -> None:
    token = cifra_password("correct horse battery staple", "master-password")

    assert token.startswith("v1:")
    assert decifra_password(token, "master-password") == "correct horse battery staple"


def test_decifra_password_rejects_wrong_master_password() -> None:
    token = cifra_password("super-secret", "master-password")

    with pytest.raises(ValueError, match="Master Password errata"):
        decifra_password(token, "different-password")


def test_decifra_password_rejects_tampered_token() -> None:
    token = cifra_password("super-secret", "master-password")
    prefix, payload = token.split(":", 1)
    tampered_payload = list(payload)
    tampered_payload[len(tampered_payload) // 2] = "A" if tampered_payload[len(tampered_payload) // 2] != "A" else "B"
    tampered_token = f"{prefix}:{''.join(tampered_payload)}"

    with pytest.raises(ValueError):
        decifra_password(tampered_token, "master-password")