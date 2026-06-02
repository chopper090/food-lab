#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FOOD_LAB pipeline - stage 4 helper: SPANS_ALL (passata singola, bassa RAM)
Apre il PDF UNA sola volta, estrae il testo pagina per pagina liberando subito gli
oggetti pesanti di pdfplumber (flush_cache), e scrive un file di span per ogni
ingrediente in out/_spans/<owner_id>.txt.
Cosi' gli agenti del workflow leggono semplice testo, SENZA ricaricare il PDF
(evita di avere molti pdfplumber in RAM contemporaneamente).

Memoria: tiene in RAM solo il testo "piatto" (~1-2 MB di stringhe) + una pagina
pdfplumber alla volta. Un solo processo, sequenziale.
"""
import os, sys, re, unicodedata
from collections import defaultdict
import pdfplumber

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PDF = os.environ["FOODPDF"]
CAP = int(os.environ.get("CAP", "900"))
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
SPANS = os.path.join(OUT, "_spans")
SCAN_START, SCAN_END = 17, 607

NAME = r"[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ'’\- ]{1,28}?"
EDGE_RE = re.compile(rf"^\s*({NAME}) & ({NAME}):\s?(.*)$")


def slug(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", s.lower().strip()).strip("_")


def main():
    # --- passata singola: estrai testo piatto e libera la memoria pesante ---
    page_texts = {}
    with pdfplumber.open(PDF) as pdf:
        N = len(pdf.pages)
        for i in range(SCAN_START, min(SCAN_END, N)):
            page = pdf.pages[i]
            page_texts[i] = (page.extract_text() or "").split("\n")
            try:
                page.flush_cache()          # rilascia chars/oggetti pesanti
                page.get_textmap.cache_clear()
            except Exception:
                pass

    # --- testate ---
    headings = []
    for i in sorted(page_texts):
        for j, ln in enumerate(page_texts[i]):
            m = EDGE_RE.match(ln)
            if m:
                kind = "xref" if m.group(3).strip().lower().startswith("vedi") else "full"
                headings.append((i, j, m.group(1).strip(), m.group(2).strip(), kind))

    def span_text(k):
        pi, pj = headings[k][0], headings[k][1]
        if k + 1 < len(headings):
            ei, ej = headings[k + 1][0], headings[k + 1][1]
        else:
            ei, ej = SCAN_END, 0
        out = []
        for pageno in range(pi, ei + 1):
            lines = page_texts.get(pageno, [])
            start = pj if pageno == pi else 0
            end = ej if pageno == ei else len(lines)
            out.extend(lines[start:end])
        return " ".join(s.strip() for s in out).strip()

    by_owner = defaultdict(list)
    for k, (pi, pj, o, p, kind) in enumerate(headings):
        if kind != "full":
            continue
        oid = slug(o)
        a, b = sorted([oid, slug(p)])
        txt = span_text(k)
        if len(txt) > CAP:
            txt = txt[:CAP] + " […]"
        by_owner[oid].append((f"{a}|{b}", pi + 1, slug(p), txt))

    os.makedirs(SPANS, exist_ok=True)
    with open(os.path.join(SPANS, ".gitignore"), "w", encoding="utf-8") as fh:
        fh.write("*\n")   # estratti locali di lavoro: mai versionare/spedire

    total = 0
    for oid, items in by_owner.items():
        lines = []
        for key, page, partner, txt in items:
            lines.append(f"@@ key={key} page={page} partner={partner}")
            lines.append(txt)
            lines.append("")
        with open(os.path.join(SPANS, oid + ".txt"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        total += len(items)

    print(f"Ingredienti con span 'full': {len(by_owner)} / 99")
    print(f"Span 'full' totali:          {total}  (atteso ~1090)")
    print(f"Scritti in: {SPANS}")


if __name__ == "__main__":
    main()
