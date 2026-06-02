#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FOOD_LAB pipeline - stage 4 helper: SPANS
Per un dato OWNER, estrae il testo di ogni voce di accostamento 'full' (dalla testata
'Owner & Partner:' alla testata successiva) e lo stampa preceduto da una riga macchina:
    @@ key=<a|b> page=<N> partner=<pid>
Il testo grezzo NON viene salvato su file: serve solo a derivare NOTE di soli FATTI.

Env: OWNER (obbligatorio), CAP (cap caratteri per span, default 900), LIMIT (default 999)
"""
import os, sys, re, unicodedata
import pdfplumber

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PDF = os.environ["FOODPDF"]
OWNER = os.environ.get("OWNER", "")
CAP = int(os.environ.get("CAP", "900"))
LIMIT = int(os.environ.get("LIMIT", "999"))
SCAN_START, SCAN_END = 17, 607

NAME = r"[A-ZÀ-ÖØ-Þ][A-Za-zÀ-ÖØ-öø-ÿ'’\- ]{1,28}?"
EDGE_RE = re.compile(rf"^\s*({NAME}) & ({NAME}):\s?(.*)$")


def slug(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", s.lower().strip()).strip("_")


def main():
    if not OWNER:
        print("ERR: OWNER non impostato"); sys.exit(2)
    pages_lines = {}
    headings = []   # (page_idx, line_idx, owner, partner, kind)
    with pdfplumber.open(PDF) as pdf:
        N = len(pdf.pages)
        for i in range(SCAN_START, min(SCAN_END, N)):
            lines = (pdf.pages[i].extract_text() or "").split("\n")
            pages_lines[i] = lines
            for j, ln in enumerate(lines):
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
            lines = pages_lines.get(pageno, [])
            start = pj if pageno == pi else 0
            end = ej if pageno == ei else len(lines)
            out.extend(lines[start:end])
        return " ".join(s.strip() for s in out).strip()

    owner_id = slug(OWNER)
    count = 0
    for k, (pi, pj, o, p, kind) in enumerate(headings):
        if kind != "full" or o.lower() != OWNER.lower():
            continue
        a, b = sorted([owner_id, slug(p)])
        txt = span_text(k)
        if len(txt) > CAP:
            txt = txt[:CAP] + " […]"
        count += 1
        print(f"@@ key={a}|{b} page={pi+1} partner={slug(p)}")
        print(txt)
        print()
        if count >= LIMIT:
            break
    print(f"## OWNER={owner_id} FULL_SPANS={count}")


if __name__ == "__main__":
    main()
