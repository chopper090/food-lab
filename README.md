# FOOD·LAB — Matrice dei Sapori

App (PWA, single-file, vanilla JS) per esplorare **accostamenti, combinazioni e profili aromatici** degli ingredienti e aiutare la creazione di piatti.

## Funzioni
- **🧪 Esplora** — ruota concentrica degli ingredienti: scegli e vedi a colori cosa si abbina (bianco = escluso), con motore a grafo (completa la selezione · gruppi che funzionano · preparazioni).
- **🎡 Ruota** — ruote in cascata che restringono passo passo verso 3–4 ingredienti che funzionano insieme, con filtri stagione / cucina / tipo di abbinamento.
- **🧬 Matrice** — profilo aromatico per ingrediente (sunburst a raggi variabili) e affinità di profilo.
- **📅 Stagione · 🎉 Feste** — cosa è di stagione e piatti per occasioni internazionali.
- **ℹ️ Fonti** — trasparenza sul dato (verificato / base AI / tuo) e validazione dei metadati in blocco.
- Editor metadati e piatti, preferiti, piatti salvati, export/import — salvati in locale (`localStorage`).

## Fonti & metodo
I dati sugli **accostamenti** derivano da fatti (coppie, preparazioni, cucine, motivo breve **parafrasato**) con **citazione di pagina**, dal libro *La grammatica dei sapori* (Niki Segnit). I **profili aromatici** e l'idea di rappresentazione a sunburst si ispirano a *The Flavor Matrix* (James Briscione).

> **Nessuna prosa o dato proprietario dei libri è riprodotto.** Si usano solo fatti, citazioni di pagina e l'idea di rappresentazione. Metadati, piatti/feste e profili aromatici sono una **base AI da validare**, etichettata come tale. I PDF dei libri e il testo grezzo estratto non fanno parte di questo repository.

## Uso
Apri `index.html` (doppio clic) oppure visita il sito pubblicato (vedi *Pages*). I dati stanno in `data/data.js`. Per rigenerarli dalla pipeline: `python tools/pipeline/rebuild_all.py`.

## Stack
Vanilla JS, single-file `index.html`, dati statici in `data/`, PWA (`manifest.webmanifest` + `sw.js`). Nessun server.
