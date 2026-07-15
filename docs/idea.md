Progetto PassGuardian: Come funziona e cosa ho fatto
L'obiettivo del progetto era creare un gestore di password che girasse nel terminale, ma che fosse sicuro sul serio. Non è il solito programmino dove salvi i dati in chiaro: qui c'è una vera gestione dei permessi, le password vengono criptate e c'è un sistema di compilazione automatica (l'autofill) che controlla se sei sulla pagina giusta prima di digitare, così eviti le truffe di phishing.

Ecco come ho strutturato il codice e come funziona il tutto.

1. Come sono divisi i file
Per evitare di fare un unico file gigante e disordinato, ho diviso il progetto in moduli logici:

main.py: È il file principale, quello che fa partire tutto. Gestisce il login iniziale e i vari cicli del menu.

interfaccia.py (nella cartella GUI): Qui dentro c'è solo la parte grafica. Gestisce i colori del terminale, i testi dei menu, la splash screen iniziale e l'allineamento delle tabelle.

auth.py (nella cartella ENGINE): Gestisce gli utenti che possono usare il programma, controlla se la password di accesso è giusta e assegna i ruoli (Admin o Utente normale).

vault.py (nella cartella ENGINE): È il motore che gestisce il file delle password. Contiene le funzioni per caricare il JSON, cercare un sito, salvarne uno nuovo o modificarlo.

security.py (nella cartella ENGINE): È la cassaforte del programma. Qui ci sono le funzioni per criptare/decriptare e l'algoritmo che analizza i link per la sicurezza.

2. Le funzioni fighe che ho implementato
👥 Dividere gli utenti per ruoli (Admin vs Utente normale)
Ho fatto in modo che il programma si comporti diversamente a seconda di chi entra:

Se entri come alessandro (utente normale), puoi salvare e modificare solo le tue password. Se provi a toccare le funzioni da amministratore, il sistema ti rimbalza con un "Accesso Negato".

Se entri come admin, si sbloccano i poteri da Master. Con l'opzione 4 vedi una tabellona gigante con i dati di tutti gli utenti registrati, e con l'opzione 6 puoi eliminarli.

🔒 Isolamento dei dati (Ognuno vede solo il suo)
Ho modificato la struttura del file passwords.json. Ora non salviamo più i siti alla rinfusa. Quando salvi una password, il programma crea una cartella virtuale col tuo nome dentro il file.

Esempio: Se sia io che un altro utente salviamo l'account di github.com, il sistema non sovrascrive nulla. Crea due righe separate. Quando faccio il login io, vedo solo il mio GitHub; quando entra l'Admin, li vede entrambi e specifica di chi è ognuno.

🤖 Autofill intelligente che blocca il Phishing
Questa è la parte più complessa. Quando cerchi una password (opzione 2) per usarla su un sito:

Il programma ti dà 5 secondi di tempo per aprire il browser e cliccare sulla casella dell'username.

Prima di scrivere, il codice analizza la finestra attiva del computer. Se rileva che non sei su un browser o che il titolo della pagina web non c'entra niente con il sito che hai cercato (es. cerchi google.com ma hai aperto la pagina di un hacker), il programma si blocca e non digita nulla.

Se il controllo è OK, scrive da solo l'utente, preme TAB, scrive la password e cancella la memoria degli appunti del PC per evitare che qualcuno te la copi.

🔄 Logout e cambio utente senza riavviare
Ho inserito l'opzione 7 ("Cambia Utente"). Se la premi, il programma pulisce all'istante lo schermo del terminale (senza lasciare traccia dei tuoi dati a video) e ti riporta alla schermata di login iniziale. È comodissimo per passare dall'utente normale all'admin in un secondo per fare i test.

3. La sicurezza reale (Cosa dire al prof)
Se il prof fa domande sulla sicurezza, digli queste tre cose che ho inserito:

Le Master Password sono protette da Hashing (SHA-256): Nel database degli utenti non salviamo la password vera, ma solo un'impronta digitale cifrata e impossibile da invertire.

Le password dei siti sono criptate in AES-128: Sul disco, le password dei siti vengono salvate come stringhe di testo totalmente illeggibili. Vengono decriptate solo in memoria nel momento esatto in cui servono.

Zero-Knowledge su GitHub: Ho configurato il file .gitignore per bloccare il caricamento della cartella DATABASE. Online ci va solo il codice pulito, i dati sensibili non lasciano mai il computer locale.

🛠️ Come testarlo insieme per vedere se è tutto ok:
Lancia il comando pip install -r requirements.txt per installare le librerie necessarie.

Avvia con python src/main.py.

Fai il login con alessandro (password: user123) e salva un sito.

Premi 7 per disconnetterti, vedrai lo schermo pulirsi, poi entra come admin (password: admin123).

Premi 4 e vedrai la tabella globale con l'iconcina 🌐 che ti mostra anche i dati che avevi salvato prima con l'altro utente.
