# PassGuardian 🔐

**PassGuardian** è un gestore di credenziali avanzato e sicuro scritto in Python. L'applicazione è stata progettata seguendo una rigorosa separazione architetturale tra il motore logico dell'applicazione (**ENGINE**) e i moduli dell'interfaccia utente (**GUI** e **CLI**), garantendo scalabilità, riutilizzabilità del codice e indipendenza dei moduli.

---

## Architettura del Progetto

Il codice è organizzato in una struttura a moduli pulita:


PassGuardian/
│
├── database/
│   ├── vault.json            # Archivio crittografato delle credenziali
│   └── whitelist.json        # Whitelist centralizzata dei brand affidabili
│
├── src/
│   ├── main_GUI.py           # Entrypoint dell'applicazione grafica
│   ├── main_CLI.py           # Entrypoint dell'interfaccia a riga di comando
│   │
│   ├── ENGINE/               # CORE LOGICO (Model & Business Logic)
│   │   ├── models/           # Modelli polimorfici (Base, Web, SSH)
│   │   ├── output_manager.py # Gestione erogazione dati (Clipboard/Autofill)
│   │   ├── phishing.py       # Algoritmi di controllo sicurezza e Typosquatting
│   │   ├── storage.py        # Cifratura e persistenza dati su file JSON
│   │   └── utils.py          # Funzioni di supporto (es. Distanza Levenshtein)
│   │
│   └── GUI/                  # INTERFACCIA GRAFICA (View & Controller)
│       ├── app.py            # Gestore dell'applicazione principale e degli stati
│       ├── theme.py          # Configurazione estetica e stili grafici (Cyber/Dark)
│       └── screens/          # Finestre e dialoghi interattivi
│           ├── splash_screen.py
│           ├── login_screen.py
│           ├── registration_screen.py
│           ├── dashboard.py
│           ├── credential_dialogs.py
│           ├── change_password_dialog.py
│           ├── countdown_dialog.py
│           └── check_phishing_dialog.py
│
├── requirements.txt          # Dipendenze del progetto
└── README.md                 # Questa documentazione


## Funzionalità Principali


1. Separazione Moduli (Architettura Decoupled)
L'ENGINE è completamente agnostico rispetto all'interfaccia visiva. Non importa moduli grafici come tkinter o customtkinter. La GUI comunica con l'ENGINE tramite iniezione di dipendenze e chiamate polimorfiche. L'attesa temporizzata per lo Smart Autofill viene passata dall'interfaccia al modello tramite espressioni lambda, mantenendo il codice del core pulito e privo di vincoli visivi.

2. Erogazione Polimorfica e SicuraWeb Login Entry: Ottimizzato per la gestione di credenziali internet con controlli anti-phishing integrati basati sulla distanza di Levenshtein.SSH Login Entry: Integra controlli sintattici per validare host e indirizzi IP, gestendo porte personalizzate per i server.Le credenziali supportano molteplici metodi di output sicuri: copia temporizzata negli appunti o simulazione hardware di digitazione sulla tastiera (Smart Autofill).


3. Protezione Anti-Phishing AvanzataCerca e Controlla: Inserendo un URL nella barra superiore, l'applicazione ne estrae il dominio principale e lo analizza in tempo reale.Whitelist Centralizzata: L'app confronta l'URL sia con il database personale dell'utente che con un file globale database/whitelist.json. Se viene rilevato un tentativo di Typosquatting (un dominio contraffatto che imita un brand noto con una distanza $\le 2$), l'interfaccia si congela mostrando un avviso critico di sicurezza a schermo per proteggere l'utente.🚀 Installazione e SetupRequisitiPython 3.12 o superiore




## Installazione delle Dipendenze

installa i pacchetti necessari tramite il file dei requisiti (incluso setuptools richiesto per la compatibilità di CustomTkinter su Python 3.12+)

:Bash
pip install -r requirements.txt


## Come Eseguire l'ApplicazioneAvvio Interfaccia Grafica (GUI)

Per lanciare la finestra desktop di PassGuardian ed esplorare la dashboard scura in stile Cyberpunk:
Bash
python src/main_GUI.py

Avvio Interfaccia a Riga di Comando (CLI)
Per utilizzare l'applicazione direttamente all'interno del terminale sfruttando il menu comandi interattivo:

Bash
python src/main_CLI.py