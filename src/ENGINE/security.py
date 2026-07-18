"""Funzioni di sicurezza per cifrare e decifrare password."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import os

_SALT_LEN = 16
_NONCE_LEN = 16
_TAG_LEN = 32
_PBKDF2_ITERATIONS = 200_000
_VERSIONE_TOKEN = "v1"


def _deriva_chiave(master_password: str, salt: bytes) -> bytes:
    """Deriva una chiave simmetrica da Master Password con PBKDF2-HMAC-SHA256."""
    return hashlib.pbkdf2_hmac(
        "sha256",
        master_password.encode("utf-8"),
        salt,
        _PBKDF2_ITERATIONS,
        dklen=32,
    )


def _genera_keystream(chiave: bytes, nonce: bytes, lunghezza: int) -> bytes:
    """Genera uno stream pseudocasuale con HMAC-SHA256 in modalità contatore."""
    blocchi: list[bytes] = []
    contatore = 0
    totale = 0

    while totale < lunghezza:
        blocco = hmac.new(
            chiave,
            nonce + contatore.to_bytes(4, "big"),
            hashlib.sha256,
        ).digest()
        blocchi.append(blocco)
        totale += len(blocco)
        contatore += 1

    return b"".join(blocchi)[:lunghezza]


def cifra_password(password_chiaro: str, master_password: str) -> str:
    """Cifra una password in chiaro e restituisce un token serializzabile."""
    salt = os.urandom(_SALT_LEN)
    nonce = os.urandom(_NONCE_LEN)
    chiave = _deriva_chiave(master_password, salt)

    plaintext = password_chiaro.encode("utf-8")
    keystream = _genera_keystream(chiave, nonce, len(plaintext))
    ciphertext = bytes(p ^ k for p, k in zip(plaintext, keystream, strict=False))

    tag = hmac.new(chiave, nonce + ciphertext, hashlib.sha256).digest()
    payload = salt + nonce + ciphertext + tag
    payload_b64 = base64.urlsafe_b64encode(payload).decode("ascii")
    return f"{_VERSIONE_TOKEN}:{payload_b64}"


def decifra_password(password_cifrata: str, master_password: str) -> str:
    """Decifra un token password e restituisce la password in chiaro."""
    prefisso = f"{_VERSIONE_TOKEN}:"
    if not password_cifrata.startswith(prefisso):
        raise ValueError("Formato password cifrata non supportato.")

    payload_b64 = password_cifrata[len(prefisso) :]
    try:
        payload = base64.urlsafe_b64decode(payload_b64.encode("ascii"))
    except binascii.Error as exc:
        raise ValueError("Payload cifrato non decodificabile.") from exc

    min_len = _SALT_LEN + _NONCE_LEN + _TAG_LEN
    if len(payload) < min_len:
        raise ValueError("Payload cifrato non valido.")

    salt = payload[:_SALT_LEN]
    nonce = payload[_SALT_LEN : _SALT_LEN + _NONCE_LEN]
    tag = payload[-_TAG_LEN:]
    ciphertext = payload[_SALT_LEN + _NONCE_LEN : -_TAG_LEN]

    chiave = _deriva_chiave(master_password, salt)
    tag_atteso = hmac.new(chiave, nonce + ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(tag, tag_atteso):
        raise ValueError("Master Password errata o dati alterati.")

    keystream = _genera_keystream(chiave, nonce, len(ciphertext))
    plaintext = bytes(c ^ k for c, k in zip(ciphertext, keystream, strict=False))
    return plaintext.decode("utf-8")
