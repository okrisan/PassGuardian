# PassGuardian — GUI Edition

Password manager locale con vault cifrato, ora con **interfaccia grafica desktop**
in stile cyberpunk (nero / viola scuro / grigio) al posto del vecchio menu da
terminale.

## Avvio

```bash
pip install -r requirements.txt
python src/main.py
```

Al primo avvio viene creato automaticamente `src/DATABASE/users.json` con due
utenti di default (uguali a prima):

| Username     | Password   | Ruolo      |
|--------------|------------|------------|
| admin        | admin123   | super_user |
| alessandro   | user123    | user       |

## Cosa è cambiato

- **`src/main.py`** ora avvia la GUI (`GUI/app.py`) invece del menu testuale.
  La vecchia versione CLI è conservata, invariata, in **`src/main_cli.py`**
  se vuoi confrontarle o tornare indietro (`python src/main_cli.py`).
- Nuovo pacchetto **`src/GUI/`**:
  - `theme.py` — palette colori e stili condivisi (nero / viola / grigio, accenti neon).
  - `app.py` — finestra principale, gestisce Splash → Login → Dashboard.
  - `screens/splash_screen.py` — schermata di avvio animata.
  - `screens/login_screen.py` — login con toggle mostra/nascondi password.
  - `screens/dashboard.py` — shell con sidebar di navigazione.
  - `screens/vault_view.py` — tabella credenziali: ricerca, verifica stato online/offline
    in background, mostra/nascondi in chiaro, aggiungi/modifica/elimina, copia negli appunti.
  - `screens/security_view.py` — cambio master password (ora richiede anche la password attuale).
  - `screens/admin_view.py` — gestione utenti di sistema (solo per `super_user`).
- **`ENGINE/vault.py`**: aggiunti i metodi `elenca_credenziali`, `elenca_tutte`,
  `elimina_credenziale` (mancava la possibilità di eliminare una credenziale).
- La logica di autenticazione, cifratura (Fernet/SHA-256) e anti-phishing
  (`ENGINE/auth.py`, `ENGINE/security.py`) **non è stata toccata**: la GUI
  è un nuovo strato sopra lo stesso motore.

## Note

- Il pulsante "Copia Password/Username" usa `pyperclip`; se non disponibile
  usa il clipboard nativo di Tkinter come fallback.
- La verifica "online/offline" dei domini gira in un thread separato per non
  bloccare l'interfaccia.
- `main.spec` (PyInstaller) punta ancora a `src/main.py`: per generare un
  nuovo `.exe` con la GUI basta rilanciare la build, es. `pyinstaller main.spec`.
