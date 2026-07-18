"""Funzioni di utili per PassGUARDIAN."""

from __future__ import annotations


def calcola_distanza_levenshtein(s1: str, s2: str) -> int:
    """
    Calcola la distanza di Levenshtein tra due stringhe s1 e s2.
    Utilizza l'ottimizzazione dello spazio a due righe.
    Complessità temporale: O(N * M), Spaziale: O(min(N, M)).
    """
    if len(s1) < len(s2):
        return calcola_distanza_levenshtein(s2, s1)

    if len(s2) == 0:
        return len(s1)

    riga_precedente = list(range(len(s2) + 1))
    riga_corrente = [0] * (len(s2) + 1)

    for i, c1 in enumerate(s1):
        riga_corrente[0] = i + 1
        for j, c2 in enumerate(s2):
            inserimento = riga_precedente[j + 1] + 1
            cancellazione = riga_corrente[j] + 1
            sostituzione = riga_precedente[j] + (0 if c1 == c2 else 1)
            riga_corrente[j + 1] = min(inserimento, cancellazione, sostituzione)
        riga_precedente = list(riga_corrente)

    return riga_precedente[-1]