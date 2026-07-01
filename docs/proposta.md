# PassGUARDIAN

## Descrizione dell'idea

L'idea è sviluppare un password manager locale con funzionalità di autofill e anti-phishing.

Un utente che deve effettuare il login su un sito web utilizzando una password salvata dovrebbe copiare nell'applicazione l'URL del sito a cui sta tentando di accedere. A quel punto vengono eseguiti controlli per verificare:

- l'attendibilità del dominio;
- la presenza di un record salvato nel database locale.

La funzionalità potrebbe inoltre essere estesa per registrare anche autenticazioni per connessioni SSH.

Le password verrebbero salvate in modo crittografato, in strutture JSON locali. L'interfaccia prevista è una CLI essenziale, con alcune funzionalità aggiuntive.

Quando viene richiesta un'utenza per un determinato sito, le credenziali non viene mostrata semplicemente a video: viene invece avviata una procedura guidata per attivare l'autofill nel browser tramite simulazione della tastiera.

## Struttura OOP

Per rispettare i vincoli OOP, la struttura proposta è la seguente.

### Classe base astratta

Questa classe viene ereditata da tutti gli altri componenti e contiene:

- la gestione dei log di validazione dei passaggi;
- i controlli di base comuni a tutte le classi;
- un metodo `execute_target()` da sovrascrivere in ogni sottoclasse, responsabile dell'azione specifica.

### Esempi di sottoclassi

1. **ClipboardSecureTarget**: copia la password negli appunti e avvia un thread in background per cancellarla dopo 15 secondi (misura di sicurezza contro malware locali).
2. **KeyboardSimulationTarget**: digita automaticamente le credenziali simulando la tastiera fisica (riduce il rischio di intercettazione tramite clipboard).
3. **AntiPhishingMatcherTarget**: esegue il controllo algoritmico di Levenshtein prima di sbloccare le password.

## Nota sull'algoritmo di Levenshtein

L'algoritmo di Levenshtein interviene in caso di differenze tra domini: calcola il numero minimo di modifiche (inserimenti, cancellazioni, sostituzioni) necessarie per trasformare una stringa nell'altra.

Se la distanza risulta bassa (ad esempio 1 o 2), il sistema può identificare un potenziale tentativo di phishing e mostrare un allarme specifico.
