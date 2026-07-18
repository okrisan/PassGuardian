# Devlog

## 2026-06-24

Abbiamo definito il perimetro del progetto e deciso di costruire un vault di credenziali locale con due tipologie concrete: Web e SSH. In questa fase abbiamo chiarito che il requisito di ereditarietà sarebbe stato soddisfatto da una classe base comune per le credenziali, con specializzazioni reali per i due casi d'uso.

La parte più importante del lavoro è stata distinguere bene ciò che appartiene al dominio da ciò che appartiene all'interfaccia. Abbiamo scelto di tenere il motore separato dalla GUI fin dall'inizio, così da evitare una finestra monolitica e un codice difficile da difendere all'orale.

## 2026-07-01

Abbiamo consolidato la persistenza su JSON e la gestione della Master Password. Ci siamo accorti che la parte delicata non era soltanto salvare i dati, ma farlo in modo coerente: utenti, credenziali, cifratura e ricifratura dovevano restare allineati.

In questa settimana abbiamo anche rifinito il modello polimorfico delle credenziali. La deserializzazione basata sul campo `tipo` ci ha permesso di recuperare la sottoclasse corretta senza scrivere catene di `if` sparse nel resto del programma.

## 2026-07-08

Abbiamo lavorato sull'anti-phishing e sulla dashboard. Il controllo sugli URL ci è sembrato un buon esempio di logica utile, perché unisce una funzione semplice a un comportamento di sicurezza visibile all'utente.

La dashboard è stata organizzata per trattare ogni credenziale in modo uniforme, ma lasciando alle singole classi la responsabilità dei dettagli. Questo ci ha aiutato anche nella parte grafica: la tabella mostra proprietà comuni, mentre i dialoghi gestiscono l'inserimento e la modifica dei dati specifici.

## 2026-07-19

Abbiamo rifinito le schermate di accesso, la modifica della Master Password e lo smart autofill. In particolare ci siamo concentrati sul rendere l'esperienza più lineare: prima login, poi dashboard, poi azioni contestuali sulle credenziali.

Ci siamo anche accorti che alcuni dettagli di integrazione fra GUI e core dovevano restare espliciti per non confondere la responsabilità dei moduli. Per questo abbiamo tenuto separate le funzioni di output fisico, le funzioni di storage e la logica anti-phishing.

## Stato finale

Al termine del lavoro il progetto risulta organizzato, navigabile e presentabile. Restano naturalmente i test da completare e ampliare, ma la struttura del codice e la documentazione sono già allineate al comportamento reale del programma.
