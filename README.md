# 🛡️ PassGuardian - Gestore Password Locale

PassGuardian è un'applicazione sicura in Python per la gestione delle password. Il sistema include un controllo degli accessi basato sui ruoli (**RBAC**), crittografia dei dati e un sistema di **Autofill sicuro** con protezione integrata contro il phishing.

---

## 🚀 Guida all'Avvio Rapido

Segui questi passaggi dal terminale (PowerShell o Prompt dei Comandi) per configurare ed eseguire il programma sul tuo computer.

### 1. Clonare il progetto
Posizionati nella cartella in cui desideri scaricare il codice ed esegui:
```bash
git clone <URL_DEL_TUO_REPOSITORY_GITHUB>
cd PassGuardian

Il programma richiede alcune librerie esterne per gestire in sicurezza l'emulazione della tastiera e il controllo delle finestre attive del browser. Installale con un unico comando:

Bash
pip install -r requirements.txt
3. Avviare l'applicazione
Esegui lo script principale per far partire la schermata di login e accedere al menu:

Bash
python src/main.py

Credenziali di Test Predefinite
Al primo avvio, il sistema genera automaticamente due profili di test per permettere la verifica dei diversi livelli di autorizzazione:

1️⃣ Account MASTER (Amministratore)
Username: admin

Password: admin123

Cosa può fare: Accede a tutte le funzioni standard, sblocca il menu [4] per vedere la tabella globale di tutti gli utenti con le password decifrate in chiaro e può eliminare gli utenti tramite l'opzione [6].

2️⃣ Account USER (Utente Standard)
Username: alessandro

Password: user123

Cosa può fare: Può salvare, cercare e modificare esclusivamente le proprie password personali. Se prova ad accedere alle opzioni di amministrazione ([4] o [6]), il sistema risponderà con un messaggio di ⛔ ACCESSO NEGATO.

🛡️ Note sulla Sicurezza e Architettura
Isolamento dei Dati: I dati sensibili vengono salvati localmente. Grazie al file .gitignore, la cartella src/DATABASE/ non viene mai caricata su GitHub, garantendo un approccio Zero-Knowledge.

Crittografia: Le Master Password sono protette da hashing non invertibile (SHA-256), mentre le credenziali dei singoli siti sono cifrate su disco con algoritmo simmetrico AES-128 (modulo Fernet).

Controllo Anti-Phishing: Durante la procedura di Autofill ([2]), il sistema analizza la finestra attiva del sistema operativo. Se l'utente non si trova su un browser supportato o se il titolo della pagina web non corrisponde al dominio memorizzato, l'inserimento automatico viene bloccato istantaneamente.


Una volta salvato il file sul PC, puoi caricarlo su GitHub con i classici comandi:
```powershell
git add README.md
git commit -m "Docs: Aggiunto file README con le istruzioni di avvio"
git push
