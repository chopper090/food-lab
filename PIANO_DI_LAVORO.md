# FOOD_LAB — Piano di lavoro

App per estrarre la conoscenza sugli accostamenti di sapori dal libro
*"La grammatica dei sapori"* (Niki Segnit, ed. italiana, trad. Cristina Pradella)
e usarla come **suggeritore di combinazioni** di ingredienti.

> Documento di metodo e architettura. È la "fonte di verità" del progetto:
> va aggiornato quando cambiano decisioni o risultati.
> Stato: **Fase 1 (dati) COMPLETATA** — 16 famiglie · 99 ingredienti · 1089 archi · 1089 note (copertura 100%, 0 problemi; confidenza **high 841 / medium 231 / thin 17** dopo arricchimento M4). Bundle in `data/data.json`. Pipeline in `tools/pipeline/` (stage0–6 + `build_metadata` + `enrich_thin`).
>
> **Fasi 2–4 (app) IN CORSO** — `index.html` single-file (carica `data/data.js` via `file://`):
> - **Selezione & filtri**: ricerca + filtri famiglia/tipo/stagione/**reperibilità**; i filtri restringono sia l'elenco-ingredienti sia i risultati.
> - **Motore a grafo (M1)**: *Completa la selezione*, *Corrispondenze parziali*, **Gruppi che funzionano** (clique via Bron–Kerbosch sui vicini comuni, cap 6, con guardrail onesto se la selezione non è già tutta-con-tutta), *Preparazioni possibili* (aggregate dalle coppie interne), ricerca live nei risultati; drawer di dettaglio con **confidenza** + citazione di pagina + etichetta "sintesi, non testo originale".
> - **Metadati & utente (M2)**: editor metadati (tipo/stagione/origine/reperibilità) per ingrediente, **persistenza `localStorage`** (layer `user`, mai `book`) con override `_source:"user"` e ripristino AI; **preferiti** e **piatti salvati**; export/import JSON; **base geografica** (default *Messina, Sicilia*, modificabile).
>
> Nuova dimensione metadati **`locality`** = *reperibilità* rispetto alla base (Locale/Italiano/Mediterraneo/Importato), distinta dall'`origin` botanico (es. pomodoro: origin Americhe, locality Locale). Seed AI in `build_metadata.py` (`LOC`), DA VALIDARE. Schema+base in `stage6_bundle.py`. Distribuzione seed: Locale 47 · Italiano 30 · Importato 17 · Mediterraneo 5.
>
> Verificato in browser (1 giu 2026): 12 controlli d'integrità dati verdi; gruppi = clique valide (0 archi inventati); editor/persistenza/preferiti/salvati ok end-to-end; 0 errori console.
>
> **Audit G6 (M4) SUPERATO** (1 giu 2026): su tutte le 1089 note — coppia esiste 100% · `reason` parafrasata non letterale 100% (0 copie verbatim, overlap 6-gram ~0% → firewall copyright tenuto) · pagina citata corretta 30/30 nel campione PDF (≥98%) · preparazioni ancorate al testo 98% (52 non letterali, per lo più piatti noti reali tipo BLT/mocha/tzatziki; ~10 generiche o sospette da rivedere, es. `bacon & ostrica`).
>
> **Arricchimento "thin" (M4, fatto)**: le 36 `reason` vuote (tutte thin) riscritte con sintesi originali ≤200 char dai passi sorgente (`enrich_thin.py`); audit copyright sui 36 → 0 verbatim, overlap 6-gram ≤19%. 25 portate a `medium`, 11 tenute `thin` (incl. coppie che l'autrice boccia, es. melone+zenzero). Ora **thin 17 · reason vuote 0**. Resta da fare in M4: pulizia ~10 preparazioni sospette, mappatura pagine stampate, validazione `locality` (utente).
>
> **Fase 5 (conoscenza esterna + creazione piatti + restyle) AVVIATA** — nuovo layer **`ext`** separato e citabile (parallelo a `book`/`meta`/`user`): **49 piatti** internazionali (Perù→Corea→Sicilia) e **15 occasioni/feste** (Cinco de Mayo, Diwali, Natale, Ferragosto…), ogni piatto collegato ai 99 ingredienti (231 link, validati da `build_ext.py`). Seed AI `_source:"ai"` DA VALIDARE; citazioni a fonti autorevoli da aggiungere (modello **ibrido**, scelto 1 giu 2026). App: **navigazione a schede** (🧪 Esplora · 📅 Stagione · 🎉 Feste), vista **Stagione** (stagione corrente da `Date`, ingredienti+piatti di stagione), vista **Feste** (occasione→piatti→ingredienti), **dettaglio piatto** con "usa gli ingredienti nella selezione", sezione **"Piatti che puoi fare"** dalla selezione, cross-link **"Piatti con questo ingrediente"**, restyle (nav a pillole, hero stagione con gradienti, card piatto con bandiere, animazioni). Verificato in browser, 0 errori console.
>
> **🎡 Ruota dei sapori (cascata)** — scheda dedicata che reinterpreta la ruota di copertina: ruote radiali SVG **in serie**. Ruota 1 = tutti i 99 ingredienti (16 spicchi colorati per famiglia); scegliendo un ingrediente la ruota successiva mostra **solo i vicini comuni** a tutta la catena (= costruzione di una clique sul grafo del libro), restringendo il cerchio (es. 99→40→10). Filtri a cascata: **stagione** (metadati), **cucina** (ingredienti usati nei piatti `ext`), **tipo di abbinamento** (`kind` classico/insolito/neutro). Output: 3–4 ingredienti che funzionano insieme → "apri nel motore". Correttezza verificata (ruota N = vicini comuni reali nel grafo).
>
> **Fase 5 — completati i 3 fronti dati/abbinamenti/editor (1 giu 2026):**
> - **Più dati**: `ext` ampliato a **96 piatti · 22 occasioni · 35 cucine** (440 link piatto→ingrediente), da Perù a Corea a Sicilia/Italia (build_ext.py).
> - **Abbinamenti estesi + vino**: nuove collezioni `ext.pairings` (30 abbinamenti ingrediente-ingrediente oltre il libro, con flag **`novel`** calcolato vs archi Segnit → 5 davvero nuovi) ed `ext.wine` (22 ingredienti + fallback per tipologia). In UI: sezioni **🍷 Vino** e **Abbinamenti extra** nel dettaglio ingrediente; toggle **"oltre il libro"** nella Ruota che estende l'adiacenza (verificato: Anguria 13→14 col partner novel).
> - **Editor `ext`**: form **"➕ Nuovo piatto"** (ricerca ingredienti dai 99, stagioni, occasioni, nota) → salva in `localStorage` (`user.ext_dishes`), compare ovunque (Esplora/Stagione/Feste/Ruota); **elimina** piatti utente; **valida** piatti baked (`user.ext_validated`, _source ai→user); export/import aggiornati. Tutto verificato end-to-end, 0 errori console.
> - *Nota tecnica:* su Windows le 🇮🇹 emoji-bandiera non si rendono → **rimosse** (resta il badge cucina).
>
> **La ruota come identità (1 giu 2026):** decisione di rendere la ruota di copertina il marchio e la struttura base.
> - **Logo** = mini-ruota SVG a 16 colori-famiglia accanto al wordmark (spin su hover).
> - **Home (scheda Esplora)** = grande **ruota concentrica a 2 anelli** (anello interno = 16 famiglie con nome, cliccabili = filtro; anello esterno = 99 ingredienti) con la logica delle ruote del vino: **colore = selezionato/compatibile, bianco = escluso**. Selezionando, il cerchio si restringe a vista (Pomodoro→58 bianchi; +Basilico→87 bianchi, 12 colorati), centro = conteggio/azzera. Transizioni di colore animate.
> - **Albero testuale** della selezione (`tree-bar`) sopra i risultati; gruppi/piatti/preparazioni restano testuali sotto (= opzioni avanzate). La scheda 🎡 Ruota (cascata in serie) resta come strumento guidato.
>
> **Hardening — affidabilità & coerenza (1 giu 2026):** dopo una revisione critica.
> - **Validatore `data.json`** al caricamento (shape book/meta + archi→ingredienti): un dato corrotto mostra un errore chiaro invece di rompere in silenzio (criterio d'uscita Fase 2 finalmente soddisfatto).
> - **Profili Matrice calcolati live**: `build_matrix` ora emette le *regole* (`type_w/fam_w/ovr`) e l'app calcola `profileOf(id)` dai metadati **correnti** → gli edit dell'utente si propagano alla matrice (incoerenza risolta).
> - **Pagina ℹ️ Fonti & metodo**: legenda fonti (verificato dal libro / base AI da validare / tuo), tabella layer-per-layer, nota firewall copyright (libri NON riprodotti), e chiarimento delle 3 ruote (Esplora/Ruota/Matrice).
> - **Tono onesto sulla Matrice**: "Affini per profilo" etichettato come *stima AI, non dal libro*, con caveat esplicito.
> - **Fix vino fuorviante**: niente più fallback per `frutta/verdura/...` (es. avocado→Moscato eliminato); vino solo se voce esplicita o tipologia affidabile (carne/pesce/latticino/frutta secca).
> - **`rebuild_all.py`**: un solo comando rigenera tutti i layer derivati + `data.js` (riduce la fragilità della pipeline a 11 script). *Scelta consapevole:* resta single-file (apertura via doppio clic), niente modularizzazione.
>
> **Batch "procedi con tutto" (2 giu 2026):**
> - **Mobile / PWA (M3)**: layout **responsive** (≤880px: sidebar → drawer col bottone ☰, nav scrollabile, ruote/card adattive) + `manifest.webmanifest` + `sw.js` (cache-first offline, registrato solo su http/s) + `icon.svg` (ruota). Installabile e usabile in cucina.
> - **Validazione metadati in blocco**: nella pagina Fonti, tabella dei 99 con select tipo/reperibilità + ✓ valida (singolo o "tutti i filtrati"): marca `_source:"user"` → il dato AI diventa *tuo*.
> - **Unificazione abbinamenti (punto di consumo)**: il dettaglio ingrediente mostra ora i 3 segnali insieme, etichettati: *accostamenti del libro* (verificati, con pagina) · *abbinamenti extra* (ext) · **Affinità di profilo (stima AI)** dalla matrice.
> - **Citazioni**: campo "Fonte" nell'editor piatti + visualizzazione nel dettaglio (infrastruttura per il "dopo" del modello ibrido).
> - **Pulizia dati**: rimosse 12 preparazioni generiche/mal-assegnate (`clean_preps.py`, in `rebuild_all`).
> - *Rinviato:* mappatura pagine fisiche→stampate (valore basso) e unificazione del *motore* (Esplora/Ruota restano book-based per onestà; l'unificazione è al punto di consumo).
>
> **Fase 6 — Matrice dei sapori (1 giu 2026):** ispirata a *The Flavor Matrix* (Briscione). Il libro nella `LIBRARY/` è **immagine (JBIG2), non estraibile** e i suoi valori sono proprietari → **non riprodotti**. Approccio scelto (utente): **base AI modificabile**. Nuovo layer **`matrix`** (`build_matrix.py`): **tassonomia** di 18 famiglie aromatiche (categoria→descrittori, dalla ruota di copertina) + **profilo aromatico per i 99 ingredienti** derivato in modo trasparente da *famiglia + tipologia* (+ override), `_source:"ai"`, DA VALIDARE. Scheda dedicata **🧬 Matrice**: selettore ingrediente + **sunburst a raggi di lunghezza variabile** (descrittore = raggio, lunghezza = affinità; le famiglie più presenti occupano più arco → "non tutto dritto"), filtro **enfasi** per categoria (cambia lunghezze e grandezze), legenda, e **"Affini per profilo aromatico"** (nuovo segnale di abbinamento = sovrapposizione di profili). Verificato in browser, 0 errori console.
>
> Prossimo (roadmap): **M3** mobile + PWA + deploy · **M4** rifinitura dati (audit G6, mappatura pagine stampate, revisione 42 "thin", validazione metadati AI a partire da `locality`).

---

## 1. Obiettivo e decisioni prese

Selezionare ingredienti (per famiglia di sapore, e in prospettiva per stagione/
origine/tipologia) e ottenere **quali ingredienti combinano bene tra loro**,
incluse combinazioni a 3+ elementi, tramite logica a grafo.

Decisioni dell'utente (1 giu 2026):

| Tema | Scelta | Conseguenza |
|---|---|---|
| **Uso** | Ibrido | Si parte come tool privato, ma i dati *derivati da Segnit* restano separati e sostituibili → resta pubblicabile in futuro. |
| **Metadati** (stagione/origine/tipo) | Layer separato | Non sono nel libro: vivono in un livello a parte, etichettato "non-libro" e modificabile dall'utente. |
| **Motore** | Suggeritore di combinazioni (grafo) | Niente generatore di ricette AI per ora. Il "browser accostamenti" è la base-dati sottostante. |
| **Stack** | Scelta tecnica delegata | → vanilla-JS PWA, riuso scaffold FOODCOST (vedi §7). |
| **"Provenienza"** (chiarita 1 giu 2026) | **Reperibilità/sourcing**, non solo origine botanica | Nuova dimensione `locality` (Locale/Italiano/Mediterraneo/Importato) relativa a una **base** geografica utente, default *Messina, Sicilia*; l'`origin` botanico resta separato. |
| **Conoscenza esterna** (Fase 5, 1 giu 2026) | Sì, in **layer `ext` separato** | Piatti/feste/stagionalità oltre il libro. Sourcing **ibrido** (seed AI ora, citazioni dopo). Focus **internazionale**. Restyle nel single-file. |

---

## 2. Fatti verificati sul PDF (non stime)

Estratti dal file reale, non dalla memoria del modello:

| Quantità | Valore verificato | Come è stato verificato |
|---|---|---|
| Pagine totali | **620** | conteggio pagine |
| Famiglie di sapori | **16** (esatto) | intestazioni MAIUSCOLE, font size 30 |
| Ingredienti | **99** (esatto) | intestazioni Capitalizzate, font size 30 (p18–p603) |
| Intestazioni accostamento (direzionali) | **2176** = 1090 complete + 1086 rimandi | regex a inizio riga |
| Accostamenti distinti (archi non orientati) | **~1090** | dedup non orientato |
| Nomi-estremo distinti | **100**: 99 corrispondenti esatti + 1 variante di maiuscola, **0 non risolti** | match esatto su vocabolario chiuso |
| Indice alfabetico finale | **NON esiste** (il libro finisce con Bibliografia/Ringraziamenti) | scansione ultime pagine |

**Implicazione chiave:** gli estremi degli accostamenti puntano a un **vocabolario
chiuso di 99 ingredienti, con 0 nomi "orfani"**. Questo trasforma l'estrazione da
problema fuzzy di NLP a problema di *parsing con verifica per corrispondenza
esatta* → gran parte del rischio di allucinazione cade prima di iniziare.

Struttura del documento:
```
p0            copertina (immagine, 0 caratteri)
p1–p7         frontespizio, dedica, epigrafe
p8–p16        Introduzione
p17–p606      CORE: 16 famiglie → ingredienti → accostamenti
p607–p616     Bibliografia, Altri testi, Ringraziamenti  (NON dati)
```
Ogni **famiglia** = 1 pagina-intestazione (nome MAIUSCOLO + elenco ingredienti) +
N sezioni-ingrediente. Ogni **ingrediente** = nome (size 30) + paragrafo introduttivo
+ voci di accostamento, ognuna a inizio riga `Ingrediente & Partner:`.
Ogni coppia è descritta **per intero una sola volta**; l'altro lato è un rimando
`… & …: vedi <Partner> & <Ingrediente>, qui` (il "qui" era un link, ora testo
morto **senza numero di pagina** → la pagina si recupera per struttura, non dal testo).

---

## 3. I miei limiti — dove NON garantisco affidabilità

1. **Legale/copyright.** Non sono un consulente legale. I *fatti* (A si abbina a B)
   non sono protetti; *prosa, ricette, aneddoti, arrangiamento editoriale* sì. Il PDF
   proviene da fonte non ufficiale. Mitigazione: §6 (firewall copyright).
2. **Fedeltà d'estrazione.** La **struttura** (nodi, archi, pagine) è ancorata al font
   ed è immune dagli errori di testo. La **prosa** ha artefatti di glifo localizzati
   (es. *attraverso*→`auraverso`): impatta solo le note sintetizzate, che vengono
   comunque parafrasate e riviste a mano.
3. **Dati assenti dal libro.** Stagionalità, origine, tipologia **non ci sono**. Il
   layer metadati li aggiunge da conoscenza generale: meno affidabile, e la
   stagionalità varia per clima/regione. Vanno validati da te.
4. **Interpretazione.** "Classico" vs "azzardato", intensità, dosi: giudizi in parte
   soggettivi (lo dichiara l'autrice). Strutturabili, ma da validare.
5. **Note sintetizzate.** La qualità/fedeltà di ogni parafrasi è giudizio umano →
   audit a campione (§5, G6) e coda di revisione.
6. **Memoria del modello.** Inaffidabile per definizione: per questo ogni dato porta
   la **citazione di pagina** e nasce dal PDF, non dalla mia memoria.

---

## 4. Pipeline di estrazione (deterministica)

Tre rilevatori, validati su campione con tasso di errore misurato:

- **R1 — Intestazioni (geometria del font).** Token con `size ≥ 27` su p8–p606.
  `MAIUSCOLO` → famiglia (+ elenco membri dai token `18 ≤ size < 27`); altrimenti →
  inizio sezione-ingrediente. *Risultato sull'intero libro: 16 famiglie + 99
  ingredienti, 0 errori di classificazione.*
- **R2 — Voci di accostamento (regex a inizio riga).** `^Nome & Partner: …`
  *Risultato: 2176 match, 0 falsi positivi* (la sequenza ` & …:` a inizio riga è
  un'àncora ad altissima precisione).
- **R3 — Completa vs rimando.** Se il resto inizia con `vedi` → rimando; altrimenti →
  voce completa (la prosa parafrasabile inizia qui). *Risultato: 1090 complete +
  1086 rimandi, separati nettamente.*

**Risoluzione dei rimandi.** Si costruisce `complete[(owner,partner)] = pagina`; ogni
rimando `(A,B): "vedi B & A, qui"` si risolve in `complete[(B,A)]`, salvando l'arco
**una sola volta** (non orientato) con la pagina dove vive la trattazione completa.
Validato end-to-end anche su nomi multi-parola (*Cioccolato & Noce moscata*).

**Canonicalizzazione nomi.** Vocabolario chiuso: i 99 titoli di sezione sono
l'autorità. Regola: *case-fold + accent-fold + collassa spazi → match esatto* nella
tabella dei 99. Ciò che non risolve = errore → coda di revisione (oggi: 0 casi, salvo
1 variante di maiuscola gestita da una mini-mappa alias).

Stadi (ognuno idempotente e rieseguibile):
```
stage0_probe   mappa pagine/font/conteggi        (fatto: questo report)
stage1_struct  → famiglie.json, ingredienti.json (R1)
stage2_edges   → archi_raw.json                  (R2+R3)
stage3_resolve → archi.json  (rimandi + canonicalizzazione + dedup)
stage4_notes   → note_synth per arco            (parafrasi + revisione umana)
stage5_qa      → report_qa.json + coda_revisione (gate G0–G7)  ← cancello obbligatorio
stage6_bundle  → data.json  (l'unico file statico caricato dalla PWA)
```

---

## 5. QA anti-allucinazione (ogni dato tracciabile)

| Gate | Controllo | Se fallisce |
|---|---|---|
| **G0 Provenienza** | Ogni nodo ha `source_page`; ogni arco ha `writeup_page`; ogni nota ha `source_pages[]`. Nessun dato senza pagina. | Record rifiutato. |
| **G1 Vocabolario chiuso** | Ogni estremo ∈ 99 nomi canonici. | → coda revisione (oggi 0). |
| **G2 Reciprocità** | Ogni arco completo `(A,B)` ha rimando reciproco `(B,A)` e viceversa. | → coda revisione. |
| **G3 Conteggio per famiglia** | Elenco membri della pagina-intestazione == sezioni-ingrediente trovate fino alla famiglia successiva. (Sostituisce l'indice alfabetico mancante.) | → revisione. |
| **G4 Invariante conteggi** | `complete ≈ rimandi`; `archi ≈ complete`. Numeri finali bloccati e riasseriti a ogni run. | build fallisce. |
| **G5 Font sporco** | Nota la cui prosa-fonte fallisce l'euristica di italiano valido → `dirty_font_suspect`. | `needs_review:true`. |
| **G6 Audit a campione** | N=50 archi: rilettura umana della pagina citata → la coppia esiste? la nota è parafrasi fedele e non letterale? la pagina è giusta? Soglia ≥98%. | sotto soglia → campione più ampio + fix sistemico. |
| **G7 Separazione layer** | Validatore: nel file pubblicato `book.*` solo da pipeline; `meta`/`user` vuoti. | build fallisce. |

**Confidenza** per arco: `high` (completo, reciproco pulito, font pulito) /
`medium` (solo rimando, o nota breve auto-generata) / `needs_review` (qualunque
anomalia G1–G5). I `needs_review` sono visibili nel tool privato ma **esclusi** da un
eventuale rilascio pubblico finché non risolti.

---

## 6. Firewall copyright

- **Mai testo letterale nel datato pubblicato.** La prosa-fonte serve solo a *derivare*
  l'arco e a *innescare* una parafrasi; il paragrafo originale resta in memoria
  transitoria e **non** viene scritto nel file finale.
- Ogni arco porta `note_synth` (sintesi breve, parafrasata, registro fattuale, ≤200
  caratteri) + `source_pages` per la citazione. La nota è generata con istruzione
  esplicita "parafrasa, non citare", poi **rivista a mano** (G6).
- Eventuali span grezzi per audit stanno in `_provenance/` **escluso dal versionamento**
  e mai incluso nella PWA.
- In UI: citazione di pagina + etichetta "sintesi — non testo originale".

---

## 7. Schema dati

Tre layer con namespace nello stesso file, così il core derivato da Segnit è
meccanicamente separabile da metadati e contenuti futuri. La PWA tratta `book` come
immutabile; solo `meta`/`user` sono scrivibili (localStorage, pattern `store.js` di FOODCOST).

```jsonc
{
  "schema_version": "1.0.0",
  "source": { "work":"La grammatica dei sapori", "author":"Niki Segnit",
              "edition":"IT, trad. Pradella", "extracted_pages":"17-606" },

  "book": {                                   // SOLA LETTURA, generato dalla pipeline
    "families":    [ { "id":"tostati","name":"Tostati",
                       "members":["cioccolato","caffe","arachide"],"source_page":17 } ],
    "ingredients": [ { "id":"cioccolato","name":"Cioccolato","family":"tostati",
                       "source_page":18,"degree":39 } ],
    "edges":       [ { "a":"cioccolato","b":"noce_moscata","owner":"cioccolato",
                       "writeup_page":24,"source_pages":[24],
                       "note_synth":"Spezia e cacao: la noce moscata accentua il cacao e smorza il dolce.", // ESEMPIO parafrasato
                       "evidence":"full","confidence":"high","needs_review":false } ]
  },

  "meta": {                                   // LAYER ESTERNO (seed AI), editabile dall'utente
    "ingredient_meta": {
      // type/origin = stringa, season = lista, locality = reperibilità vs base
      "pomodoro": { "type":"verdura","season":["estate"],"origin":"Americhe","locality":"Locale","_source":"ai" }
    },
    "schema": { "season":["primavera","estate","autunno","inverno"],
                "type":["frutta","verdura","carne","pesce","latticino","spezia","erba","frutta secca","dispensa","altro"],
                "origin":["Mediterraneo","Europa","Asia","Africa","Americhe","Medio Oriente","varie"],
                "locality":["Locale","Italiano","Mediterraneo","Importato"] }
  },

  // 'ext' = LAYER ESTERNO (Fase 5), separabile e citabile: piatti/occasioni oltre il libro
  "ext": {
    "dishes":    [ { "id":"ceviche","name":"Ceviche","cuisine":"Peruviana","country":"Perù",
                     "category":"secondo","ingredients":["pesce_bianco","lime","peperoncino_piccante"],
                     "extra":["mais"],"seasons":["estate"],"occasions":[],
                     "note":"…","source":"","_source":"ai" } ],
    "occasions": [ { "id":"cinco_de_mayo","name":"Cinco de Mayo","when":"5 maggio","culture":"Messico",
                     "dishes":["tacos_al_pastor","guacamole"],"note":"…","_source":"ai" } ]
  },

  // 'user' = solo localStorage (mai spedito popolato). meta_overrides[id] sovrascrive
  // i campi di meta.ingredient_meta marcandoli _source:"user". base = ancora geografica.
  "user": { "base":{"city":"Messina","region":"Sicilia"},
            "favorites":[], "saved_combos":[], "meta_overrides":{}, "notes":{} }
}
```

Nota: il libro **non** gradua numericamente gli accostamenti → `strength` resta `null`
(niente dati inventati). Proxy onesto e derivabile: `evidence = "full" | "xref"`.

---

## 8. Motore suggeritore (grafo)

Grafo non orientato pesato: **99 nodi / ~1090 archi**, grado medio ≈ 22 — piccolo e
denso. In JS: `adj: Map<id,Set<id>>` (build < 5 ms). Tutto lato client, nessun server.

- **"Completa il piatto" (bridge):** dato un set S, ordina i candidati `Y∉S` per
  quanti membri di S abbina (mutual-fit); evidenzia chi abbina **tutti**.
- **"Terzetti" (triangoli):** per coppia `A,B` → `adj(A) ∩ adj(B)` = trio garantito.
- **"Gruppi che funzionano" (clique):** Bron–Kerbosch limitato a `S ∪ N(S)`, cap a
  5–6 elementi → gruppi in cui tutti si abbinano con tutti.
- **Filtri** (famiglia + metadati) = sottoinsieme di nodi ammessi; le query lavorano
  sul sottografo indotto → famiglia e metadati "si impilano" senza toccare il motore.
- **Guardrail onestà:** il motore non inventa mai un arco. Se S non ha vicino comune,
  lo dice e propone i più vicini ("abbina con 2 di 3"), senza fabbricare un match.

---

## 9. Architettura app & stack

**Stack: vanilla-JS PWA + `data.json` statico + motore a grafo lato client.**
Motivazione: il grafo è minuscolo (nessun bisogno di DB/framework); resta statico e
pubblicabile su GitHub Pages (coerente con l'uso ibrido); riusa l'infrastruttura
FOODCOST (moduli IIFE, hash-router, `utils.el()`, `store.js`, tema CSS a variabili,
service worker, `tools/release.py` + workflow GitHub). Unica deviazione: i dati si
caricano via `fetch('./data.json')` (non inline) per separazione/rigenerabilità.

```
FOOD_LAB/
  index.html  manifest.webmanifest  sw.js  VERSION  CHANGELOG.md
  css/   base.css  theme.css  components.css      (base+theme riusati da FOODCOST)
  data/  data.json
  js/    version.js  utils.js  store.js
         data.js     (fetch+valida data.json)
         graph.js    (adiacenza; pair/partners/commonNeighbors)
         engine.js   (bridge/triangoli/clique + ranking + filtri)
         modules/    selector.js  suggestions.js  pairing.js  ingredient.js  metadata.js  settings.js
         app.js      (router + shell, clonato da FOODCOST)
  tools/ pipeline/   (stage0..stage6, solo dev, NON spedito)
         release.py
  .github/workflows/release.yml
```

Schermate: 1) Selettore ingredienti + filtri · 2) Risultati (Completa il piatto /
Terzetti / Gruppi) · 3) Dettaglio accostamento (nota + citazione pagina + confidenza)
· 4) Scheda ingrediente + editor metadati · 5) Impostazioni / Fonti & metodo.

---

## 10. Fasi di esecuzione

| Fase | Deliverable | Criterio di uscita (verificabile) |
|---|---|---|
| **1. Estrazione + verifica** | pipeline stage0–6; famiglie/ingredienti/archi JSON; report QA; coda revisione svuotata; `data.json` (solo `book`) | G0–G7 verdi; G3 ok su tutte le 16 famiglie; G6 ≥98% su N=50; conteggi = 16/99/~1090 |
| **2. Shell app + browser accostamenti** | scaffold da FOODCOST; `data.js`+`graph.js`; sfoglia 99 ingredienti, vedi partner reali, dettaglio con pagina; offline | navigazione completa; validatore rifiuta un `data.json` corrotto |
| **3. Motore combinazioni** | `engine.js` + schermata Risultati + filtro famiglia | trio/gruppi corretti su 10 casi a mano; < 10 ms |
| **4. Metadati + rifinitura** | editor metadati; filtri stagione/tipo/origine; export/import; pagina Fonti; tema | i metadati persistono e non mutano `book`; G7 verde |

---

## 11. Rischi principali

| Rischio | Gravità | Mitigazione |
|---|---|---|
| Copyright (prosa letterale spedita) | Alta | parafrasi + cap lunghezza + revisione (G6); span grezzi mai versionati; citazione + etichetta "sintesi"; build pubblica con cancello |
| Citazione di pagina errata | Alta | pagine ancorate alla struttura, non indovinate; G0 vieta dati senza pagina; G6 rilegge |
| Varianti di nome | Bassa (1 caso) | vocabolario chiuso + mini-alias; G1 forza 0 non risolti |
| Glifi sporchi nelle note | Media | confinati alla prosa; rilevatore → `needs_review`; la parafrasi li neutralizza |
| Conteggio archi ≠ stima inglese (980) | Bassa | non è un errore: l'ed. italiana ha ~1090; si blocca il numero *reale* come invariante |
| Stagionalità imprecisa | Media | layer separato, etichettato, editabile da te; mai mescolato al `book` |

---

*Aggiornato: 1 giu 2026 — M1 (gruppi/clique, preparazioni aggregate, ricerca risultati) + M0 (confidenza, Esc, a11y); M2 (editor metadati + persistenza localStorage, preferiti, piatti salvati, export/import) + dimensione `locality`/reperibilità con base Messina/Sicilia + filtro geografico. M4: audit G6 superato (copyright/fedeltà/pagina) + arricchite le 36 note thin/vuote (thin 42→17, reason vuote→0). Fase 5: layer `ext` (49 piatti + 15 feste internazionali), schede Esplora/Stagione/Feste, integrazione piatti↔ingredienti↔motore, restyle. Aggiunta la 🎡 Ruota dei sapori a cascata (ruote SVG in serie, filtri stagione/cucina/tipo). Poi: +dati (96 piatti/22 feste), abbinamenti estesi + vino, editor piatti utente (localStorage). Infine: ruota come identità — logo a ruota + home a ruota concentrica (colore=compatibile / bianco=escluso) + albero testuale. Fase 6: scheda 🧬 Matrice — sunburst del profilo aromatico (base AI dai metadati, libro non estraibile/non riprodotto) + affinità di profilo. Hardening: validatore dati, profili matrice live, pagina Fonti&metodo, fix vino, rebuild_all. 2 giu 2026: mobile/PWA (responsive+manifest+sw), validazione metadati in blocco, unificazione abbinamenti nel dettaglio, citazioni nell'editor, pulizia 12 preparazioni.*
