"""Persistenza locale JSON per il vault delle credenziali e degli utenti."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
from typing import Any

from ENGINE.models.base import VaultEntry
from ENGINE.security import cifra_password, decifra_password


class VaultStorage:
    """Gestisce serializzazione, deserializzazione delle credenziali e gestione utenti."""

    def __init__(self, percorso_file: str | Path = "vault.json") -> None:
        self._percorso_file = Path(percorso_file)

    # --- SEZIONE GESTIONE UTENTI (Autenticazione Sicura) ---

    def registra_utente(self, username: str, master_password: str) -> bool:
        """Registra un nuovo utente memorizzando l'hash di sicurezza della sua Master Password."""
        dati = self._leggi_tutto()
        username_normalizzato = username.strip().lower()

        if username_normalizzato in dati["utenti"]:
            return False  # Utente già registrato

        # Calcoliamo l'hash SHA-256 per non salvare MAI le password in chiaro
        hash_password = hashlib.sha256(master_password.encode("utf-8")).hexdigest()
        dati["utenti"][username_normalizzato] = hash_password
        self._scrivi_tutto(dati)
        return True

    def verifica_utente(self, username: str, master_password: str) -> bool:
        """Verifica se l'utente esiste e se la Master Password inserita è corretta."""
        dati = self._leggi_tutto()
        username_normalizzato = username.strip().lower()

        if username_normalizzato not in dati["utenti"]:
            return False

        hash_inserito = hashlib.sha256(master_password.encode("utf-8")).hexdigest()
        return dati["utenti"][username_normalizzato] == hash_inserito

    # --- SEZIONE CREDENZIALI ---

    def esiste_credenziale(self, titolo: str, username_cred: str, proprietario: str) -> bool:
        """Verifica se l'utente loggato possiede già una credenziale con quella combinazione."""
        records = self._leggi_records_utente(proprietario)
        titolo_cercato = titolo.strip().lower()
        username_cercato = username_cred.strip().lower()
        
        for record in records:
            t_record = str(record.get("titolo", "")).strip().lower()
            u_record = str(record.get("username", "")).strip().lower()
            if t_record == titolo_cercato and u_record == username_cercato:
                return True
        return False

    def salva_credenziale(self, entry: VaultEntry, master_password: str, proprietario: str) -> None:
        """Salva una credenziale legandola all'utente corrente."""
        if self.esiste_credenziale(entry.titolo, entry.username, proprietario):
            raise ValueError(
                f"Errore: Esiste già una credenziale per '{entry.titolo}' "
                f"con l'username '{entry.username}' per l'utente '{proprietario}'."
            )
            
        dati_completi = self._leggi_tutto()
        entry.proprietario = proprietario.strip().lower()
        
        dati_completi["credenziali"].append(self._serializza_entry(entry, master_password))
        self._scrivi_tutto(dati_completi)

    def carica_credenziali(self, master_password: str, proprietario: str) -> list[VaultEntry]:
        """Carica SOLO le credenziali che appartengono all'utente loggato."""
        records_utente = self._leggi_records_utente(proprietario)
        return [
            self._deserializza_entry(record, master_password)
            for record in records_utente
        ]

    # --- METODI AUSILIARI DI BASSO LIVELLO ---

    def _leggi_records_utente(self, proprietario: str) -> list[dict[str, Any]]:
        """Filtra e restituisce solo i record JSON grezzi dell'utente specificato."""
        dati = self._leggi_tutto()
        proprietario_cercato = proprietario.strip().lower()
        return [
            rec for rec in dati["credenziali"]
            if str(rec.get("proprietario", "")).strip().lower() == proprietario_cercato
        ]

    def _leggi_tutto(self) -> dict[str, Any]:
        """Legge l'intera struttura del file JSON."""
        struttura_base = {"utenti": {}, "credenziali": []}
        if not self._percorso_file.exists():
            return struttura_base
        try:
            with open(self._percorso_file, "r", encoding="utf-8") as f:
                dati = json.load(f)
                # Assicuriamoci che la struttura interna sia coerente
                if "utenti" not in dati:
                    dati["utenti"] = {}
                if "credenziali" not in dati:
                    dati["credenziali"] = []
                return dati
        except (json.JSONDecodeError, OSError):
            return struttura_base

    def _scrivi_tutto(self, dati: dict[str, Any]) -> None:
        """Salva l'intera struttura (utenti + credenziali) su file JSON."""
        with open(self._percorso_file, "w", encoding="utf-8") as f:
            json.dump(dati, f, indent=4, ensure_ascii=False)

    def _serializza_entry(self, entry: VaultEntry, master_password: str) -> dict[str, Any]:
        record = entry.to_dict()
        password_in_chiaro = self._normalizza_password(entry.password_cifrata)
        record["password_cifrata"] = cifra_password(password_in_chiaro, master_password)
        return record

    def _deserializza_entry(self, record: dict[str, Any], master_password: str) -> VaultEntry:
        record_modificato = record.copy()
        password_cifrata = str(record_modificato["password_cifrata"])
        record_modificato["password_cifrata"] = decifra_password(password_cifrata, master_password)
        return VaultEntry.deserializza(record_modificato)

    @staticmethod
    def _normalizza_password(password: str | bytes) -> str:
        if isinstance(password, bytes):
            return password.decode("utf-8")
        return str(password)
    
    def aggiorna_credenziale(self, entry_aggiornata: VaultEntry, master_password: str, proprietario: str) -> None:
        """Aggiorna una credenziale esistente basandosi su titolo e utente proprietario."""
        dati_completi = self._leggi_tutto()
        username_normalizzato = proprietario.strip().lower()
        
        indice_trovato = -1
        for idx, rec in enumerate(dati_completi["credenziali"]):
            if (str(rec.get("proprietario")).lower() == username_normalizzato and 
                str(rec.get("titolo")).lower() == entry_aggiornata.titolo.lower()):
                indice_trovato = idx
                break
        
        if indice_trovato != -1:
            entry_aggiornata.proprietario = username_normalizzato
            dati_completi["credenziali"][indice_trovato] = self._serializza_entry(entry_aggiornata, master_password)
            self._scrivi_tutto(dati_completi)
        else:
            raise ValueError("Impossibile trovare la credenziale da aggiornare.")
        
    def cambia_master_password(self, username: str, vecchia_password: str, nuova_password: str) -> bool:
        """
        Cambia la Master Password e ricifra l'intero archivio credenziali.
        Logica pura: indipendente da qualsiasi GUI.
        """
        # 1. Verifica autenticazione (logica di validazione)
        if not self.verifica_utente(username, vecchia_password):
            return False

        # 2. Lettura dati
        dati = self._leggi_tutto()
        username_normalizzato = username.strip().lower()

        # 3. Processo di migrazione credenziali (decripta -> ricripta)
        nuove_credenziali = []
        for rec in dati["credenziali"]:
            # Filtra solo le credenziali di questo utente
            if str(rec.get("proprietario", "")).strip().lower() == username_normalizzato:
                # Decifra usando la vecchia chiave
                entry = self._deserializza_entry(rec, vecchia_password)
                # Ricifra usando la nuova chiave
                rec_aggiornato = self._serializza_entry(entry, nuova_password)
                nuove_credenziali.append(rec_aggiornato)
            else:
                # Mantieni intatte le credenziali di altri utenti
                nuove_credenziali.append(rec)

        # 4. Aggiornamento dati[cite: 5]
        hash_nuovo = hashlib.sha256(nuova_password.encode("utf-8")).hexdigest()
        dati["utenti"][username_normalizzato] = hash_nuovo
        dati["credenziali"] = nuove_credenziali

        # 5. Scrittura persistente[cite: 5]
        self._scrivi_tutto(dati)
        return True