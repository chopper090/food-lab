#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FOOD_LAB - pulizia preparazioni sospette in note.json (post enrich_thin, pre stage6).
Rimuove: (a) preparazioni mal-assegnate su archi specifici; (b) frasi generiche che
non sono veri piatti. Idempotente.
"""
import os, sys, json
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
HERE = os.path.dirname(os.path.abspath(__file__))
NOTE = os.path.join(HERE, "out", "note.json")

# rimozioni mirate (chiave arco 'a|b' con a<b) -> preparazioni da togliere
REMOVE = {
    "bacon|ostrica": ["prugne ripiene di chutney di mango"],   # mal-assegnata (confusione angels/devils on horseback)
    "avocado|formaggio_fresco": ["insalata estiva"],
    "avocado|nocciola": ["piatti con fagioli"],
    "arancia|peperoncino_piccante": ["olio aromatizzato"],
}
# frasi generiche (match esatto, ovunque) che non sono un piatto specifico
GENERIC = {"insalata estiva","olio aromatizzato","piatti con fagioli","verdure saltate",
           "verdure crude","piatti dolci","insalata mista","contorno","piatto unico","salsa"}


def main():
    doc = json.load(open(NOTE, encoding="utf-8"))
    notes = doc.get("notes", {})
    removed = 0
    for key, n in notes.items():
        preps = n.get("preparations")
        if not preps:
            continue
        kill = set(GENERIC) | set(REMOVE.get(key, []))
        new = [p for p in preps if p not in kill]
        if len(new) != len(preps):
            removed += len(preps) - len(new)
            n["preparations"] = new
    json.dump(doc, open(NOTE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("OK - preparazioni rimosse:", removed)


if __name__ == "__main__":
    main()
