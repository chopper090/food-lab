#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FOOD_LAB pipeline - stage 2: EDGES (raw)
Rileva le TESTATE di accostamento "Nome & Partner:" a inizio riga nelle pagine core.
NON memorizza prosa: salva solo (owner, partner, pagina, tipo full|xref).
Il tipo: se il resto della riga inizia con 'vedi' -> rimando (xref); altrimenti full.

Output: out/archi_raw.json  (lista di testate direzionali)
"""
import os, sys, json, re
import pdfplumber

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PDF = os.environ["FOODPDF"]
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

SCAN_START, SCAN_END = 17, 607   # pagine core (0-based), 607 escluso

# Testata accostamento: <Nome> & <Partner>:  (nomi anche multi-parola, accentati)
NAME = r"[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ'’\- ]{1,28}?"
EDGE_RE = re.compile(rf"^\s*({NAME}) & ({NAME}):\s?(.*)$")


def main():
    raw = []
    n_pages_with_edges = 0
    with pdfplumber.open(PDF) as pdf:
        n = len(pdf.pages)
        for i in range(SCAN_START, min(SCAN_END, n)):
            text = pdf.pages[i].extract_text() or ""
            hits = 0
            for line in text.split("\n"):
                m = EDGE_RE.match(line)
                if not m:
                    continue
                owner, partner, rest = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
                kind = "xref" if rest.lower().startswith("vedi") else "full"
                raw.append({"owner_raw": owner, "partner_raw": partner,
                            "page": i, "kind": kind})
                hits += 1
            if hits:
                n_pages_with_edges += 1

    with open(os.path.join(OUT, "archi_raw.json"), "w", encoding="utf-8") as fh:
        json.dump(raw, fh, ensure_ascii=False, indent=2)

    n_full = sum(1 for r in raw if r["kind"] == "full")
    n_xref = sum(1 for r in raw if r["kind"] == "xref")
    owners = sorted({r["owner_raw"] for r in raw})
    print("=" * 60)
    print(f"Testate accostamento trovate: {len(raw)}")
    print(f"  full (trattazione completa): {n_full}")
    print(f"  xref (rimando 'vedi ...'):   {n_xref}")
    print(f"Pagine con accostamenti: {n_pages_with_edges}")
    print(f"Owner distinti (atteso ~99): {len(owners)}")
    print("Output:", os.path.join(OUT, "archi_raw.json"))


if __name__ == "__main__":
    main()
