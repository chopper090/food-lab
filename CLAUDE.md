# CLAUDE.md — Umami (Matrice dei Sapori)

**Scopo.** Esploratore di **accostamenti aromatici** degli ingredienti, basato su dati estratti
e validati da *"La grammatica dei sapori"* (Niki Segnit). 3 motori: Esplora (ruota concentrica),
Ruota a cascata, Matrice sunburst. ~99 ingredienti, ~1090 accostamenti citati per pagina.

**Stack.** **Vanilla JS PWA single-file** (`index.html`, ~1420 righe) + dati statici in
`data/data.js` (571KB, `window.FOODLAB_DATA`). CSS a variabili (light/dark, 12 colori root rosso).
Font WOFF2 (Inter, Fraunces). `sw.js` cache-first. Pipeline Python per rigenerare i dati.

**Mappa file.** `index.html` (app), `data/data.js` + `data.json`, `fonts/`, `sw.js`, `manifest`,
`.nojekyll`. Dev-only (NON spediti): `tools/pipeline/` (stage0-6, build_metadata, rebuild_all),
`LIBRARY/` (PDF sorgente, git-ignored), `mockups/` (prototipi superati v3, da archiviare).

**Dove stanno i dati.** Schema a **layer immutabili**: `book` (1089 archi Segnit, citati) +
`meta` (stagione/tipo/origine) + `ext` (piatti/feste internazionali). Layer `user` = `localStorage`
(preferiti, override). I layer sono separati per tracciabilità e separabilità legale dal libro.

**Come si edita.** I dati si rigenerano con la **pipeline** (`tools/pipeline/`), non a mano.
Output transiente (`tools/pipeline/out/`) **non va versionato** (verificare `.gitignore`).

**Gotcha.** `PIANO_DI_LAVORO.md` (367 righe) è il contesto ricco → migrare in questo CLAUDE.md.
`mockups/` inganna (sembrano file attivi): archiviare. PDF in `LIBRARY/` pesano: fuori repo.

**Deploy.** GitHub Pages (`chopper090.github.io/umami/`). Versionare con `_scripts\Publish-Project.ps1`.
