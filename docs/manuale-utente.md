# Manuale Utente

PassGuardian è un gestore di credenziali locale per account web e SSH. L'applicazione consente di registrare utenti, salvare credenziali cifrate, cercare record salvati, verificare URL sospetti e rigenerare la Master Password.

## Requisiti

- Python 3.11 o superiore.
- Le dipendenze presenti in `requirements.txt`.
- Un ambiente grafico se si usa la versione GUI.

## Avvio

Dal clone del repository:

```bash
pip install -r requirements.txt
python src/main_GUI.py
```

Per la versione a riga di comando:

```bash
python src/main_CLI.py
```

## Primo accesso

Alla prima esecuzione devi creare un profilo utente con una Master Password. La password principale non viene salvata in chiaro: serve per sbloccare e ricifrare il vault locale.

Puoi accedere in due modi:

- dalla GUI, tramite la schermata di login e quella di registrazione;
- dalla CLI, scegliendo se registrarti o effettuare l'accesso all'avvio.

## Funzioni principali della GUI

La finestra principale mostra una dashboard con le credenziali dell'utente loggato.

Le azioni disponibili sono:

- aggiungere una credenziale Web;
- aggiungere una credenziale SSH;
- modificare una credenziale già salvata;
- eliminare una credenziale;
- copiare la password negli appunti;
- avviare lo smart autofill;
- cambiare la Master Password;
- uscire dalla sessione.

### Aggiunta di una credenziale Web

Inserisci:

- titolo o servizio;
- username o email;
- URL del sito;
- password.

La credenziale viene salvata nel vault cifrato e sarà poi disponibile nella tabella principale.

### Aggiunta di una credenziale SSH

Inserisci:

- titolo o host;
- username SSH;
- host o indirizzo IP;
- porta SSH, opzionale;
- password.

Se la porta non viene indicata, viene usato il valore predefinito `22`.

## Ricerca e controllo

In alto nella dashboard è presente una barra di ricerca con tre modalità:

- `Username` per filtrare per titolo o username;
- `URL (Web)` per verificare un dominio e controllare eventuali casi di phishing o typosquatting;
- `IP / Host (SSH)` per filtrare le credenziali SSH per host.

Nel controllo URL, PassGuardian confronta il dominio inserito con:

- le credenziali Web salvate nel vault dell'utente;
- la whitelist globale dei domini fidati.

Se il dominio è troppo simile a uno già noto, l'app blocca l'operazione e segnala il rischio.

## Sblocco delle credenziali

Una credenziale selezionata può essere usata in due modi:

- copia della password negli appunti;
- autofill guidato con digitazione simulata.

Per le credenziali Web, lo smart autofill compila username e password nel campo attivo dopo un breve conto alla rovescia.
Per le credenziali SSH, viene costruito il comando di connessione e poi viene digitata la password.

## Cambio Master Password

La voce dedicata alla modifica password:

- verifica la password attuale;
- richiede la nuova password e la conferma;
- ricifra tutte le credenziali dell'utente con la nuova chiave derivata.

## Uso da CLI

La CLI offre le stesse funzioni principali in forma testuale:

- `list` per visualizzare le credenziali salvate;
- `add_web` per salvare una credenziale Web;
- `add_ssh` per salvare una credenziale SSH;
- `check_url` per analizzare un URL;
- `select <numero>` per sbloccare una credenziale;
- `chpwd` per cambiare la Master Password;
- `exit` per uscire.

## Dati salvati

I dati del progetto vengono memorizzati in JSON nella cartella `DATABASE/`:

- `vault.json` contiene utenti e credenziali cifrate;
- `whitelist.json` contiene i domini affidabili usati dal controllo anti-phishing.

## Note d'uso

- Non condividere il file del vault con altre persone.
- Usa una Master Password robusta e diversa dalle password archiviate.
- Se il programma segnala un dominio sospetto, interrompi l'accesso e verifica il sito da una fonte attendibile.
