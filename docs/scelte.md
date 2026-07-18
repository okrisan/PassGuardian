# Scelte Implementative

## Perché un vault locale JSON

Abbiamo scelto un archivio locale in JSON perché il progetto nasce come strumento personale e didattico. Il formato è semplice da leggere, facile da versionare e permette di concentrarsi su architettura, cifratura e polimorfismo invece che su un database più pesante.

Il compromesso è che non c'è un server centralizzato: la sicurezza dipende dalla protezione del file locale e dalla robustezza della Master Password.

## Perché due soli tipi di credenziali

Il dominio del progetto è stato ridotto a due casi reali e distinti: Web e SSH. Sono abbastanza diversi da giustificare una gerarchia di classi, ma abbastanza vicini da condividere una base comune.

Abbiamo evitato di introdurre tipi artificiali solo per aumentare il numero di sottoclassi.

## Perché l'ereditarietà e non la sola composizione

La relazione tra `VaultEntry`, `WebLoginEntry` e `SSHLoginEntry` è davvero una relazione *is-a*.

Ogni voce del vault ha:

- dati comuni;
- una serializzazione comune;
- un metodo di sblocco che viene usato dal resto del programma senza conoscere il tipo concreto.

In questo caso l'ereditarietà evita duplicazioni e rende naturale il polimorfismo. La dashboard può trattare ogni credenziale come `VaultEntry` e chiedere solo le proprietà comuni. Le differenze restano confinate nelle sottoclassi.

La composizione sarebbe stata meno adatta perché non avremmo avuto un'entità genitore condivisa, ma solo oggetti scollegati con helper separati.

## Perché la distanza di Levenshtein per l'anti-phishing

La distanza di Levenshtein è una soluzione semplice ma efficace per rilevare domini che differiscono di pochi caratteri da un URL noto. Non pretende di sostituire sistemi di reputazione o blacklist online, ma funziona bene come euristica offline e didattica.

Abbiamo preferito questa scelta perché:

- è comprensibile all'orale;
- si implementa senza dipendenze esterne;
- mostra bene il legame tra algoritmi e sicurezza applicata.

## Perché separare GUI e ENGINE

La separazione tra interfaccia e logica serve a due scopi:

- rendere il codice più testabile e navigabile;
- permettere alla CLI e alla GUI di riusare gli stessi oggetti e le stesse regole.

Questa scelta riduce l'accoppiamento e rende più facile spiegare il progetto all'orale, perché il comportamento importante è concentrato nel core.

## Autofill e canali di output

Abbiamo lasciato l'erogazione della password in un modulo separato perché clipboard e digitazione simulata sono aspetti operativi, non regole di dominio.

Questo evita che le classi del vault dipendano direttamente da `pyautogui` o `pyperclip`.

## Ricerca e filtro nella dashboard

La ricerca visiva nella dashboard non modifica il vault. Filtra solo la tabella corrente, così l'utente può cercare rapidamente per titolo, username, URL o host senza rischiare di alterare i dati salvati.


