# src/security.py
import re


class PhishingDetector:
    """
    Modulo di sicurezza per l'analisi dei domini e la prevenzione del phishing.
    Sfrutta Regex e analisi delle stringhe (Distanza di Levenshtein).
    """

    def __init__(self):
        # Lista di domini famosi spesso bersaglio di phishing
        self.domini_protetti = ["google.com", "paypal.com", "github.com", "netflix.com", "amazon.com", "poste.it"]

    def estrai_dominio(self, testo_input):
        """
        Usa una REGEX per estrarre solo il dominio principale (es. google.com)
        anche se l'utente incolla un URL lungo come https://www.google.com/login
        """
        if not testo_input:
            return ""

        # Rimuove http, https, www e tutto ciò che viene dopo il dominio
        pattern = r"^(?:https?://)?(?:www\.)?([^/:\?#]+)"
        match = re.search(pattern, testo_input.strip().lower())
        if match:
            dominio = match.group(1)
            # Prende solo le ultime due parti (es. mail.google.com -> google.com)
            parti = dominio.split('.')
            if len(parti) > 2:
                return ".".join(parti[-2:])
            return dominio
        return testo_input.strip().lower()

    def calcola_distanza(self, s1, s2):
        """Algoritmo di Levenshtein per calcolare la somiglianza tra due stringhe."""
        if len(s1) < len(s2):
            return self.calcola_distanza(s2, s1)
        if len(s2) == 0:
            return len(s1)

        linea_precedente = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            linea_corrente = [i + 1]
            for j, c2 in enumerate(s2):
                inserimenti = linea_precedente[j + 1] + 1
                eliminazioni = linea_corrente[j] + 1
                sostituzioni = linea_precedente[j] + (c1 != c2)
                linea_corrente.append(min(inserimenti, eliminazioni, sostituzioni))
            linea_precedente = linea_corrente
        return linea_precedente[-1]

    def verifica_dominio(self, url_utente):
        """Controlla se il dominio assomiglia in modo sospetto a uno protetto."""
        dominio = self.estrai_dominio(url_utente)

        if not dominio:
            return True, "Input vuoto o non valido."

        # Se è identico a un dominio protetto, è sicuro
        if dominio in self.domini_protetti:
            return True, f"Dominio ufficiale e verificato: {dominio}"

        # Controlla typosquatting (somiglianza visiva)
        for protetto in self.domini_protetti:
            distanza = self.calcola_distanza(dominio, protetto)
            # Se la distanza è 1 o 2, le stringhe sono quasi identiche
            if 0 < distanza <= 2:
                return False, f"⚠️ ATTENZIONE PHISHING: Il dominio '{dominio}' è incredibilmente simile a quello ufficiale '{protetto}'!"

        return True, f"Dominio analizzato: {dominio} (Nessun pattern di phishing immediato)"