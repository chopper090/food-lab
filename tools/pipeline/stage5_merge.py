#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FOOD_LAB pipeline - stage 5: MERGE NOTE + QA
Ricompone i file out/notes_by_owner/*.json (uno per ingrediente, prodotti dal workflow)
in un unico out/note.json, e verifica la copertura contro out/archi.json.

QA:
  - ogni key della nota deve corrispondere a un arco esistente (G1-note)
  - copertura: quanti dei 1089 archi hanno una nota
  - validazione campi (kind/confidence ammessi; source_page intero)
"""
import os, sys, json, glob
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
BYOWNER = os.path.join(OUT, "notes_by_owner")

KIND_OK = {"classico", "insolito", "neutro"}
CONF_OK = {"high", "medium", "thin"}


def main():
    edges = json.load(open(os.path.join(OUT, "archi.json"), encoding="utf-8"))
    edge_keys = {f"{e['a']}|{e['b']}" for e in edges}

    files = sorted(glob.glob(os.path.join(BYOWNER, "*.json")))
    notes = {}
    problems = []
    dup = 0
    per_owner = []
    for f in files:
        owner = os.path.splitext(os.path.basename(f))[0]
        try:
            data = json.load(open(f, encoding="utf-8"))
        except Exception as ex:
            problems.append(f"{owner}: JSON illeggibile ({ex})")
            continue
        arr = data.get("notes", []) if isinstance(data, dict) else data
        per_owner.append((owner, len(arr)))
        for nt in arr:
            key = nt.get("key")
            if not key or "|" not in key:
                problems.append(f"{owner}: nota senza key valida -> {nt}")
                continue
            a, b = key.split("|", 1)
            key = f"{min(a,b)}|{max(a,b)}"   # normalizza ordine
            if key not in edge_keys:
                problems.append(f"{owner}: key non corrisponde a un arco -> {key}")
                continue
            if key in notes:
                dup += 1
            kind = nt.get("kind")
            conf = nt.get("confidence")
            if kind not in KIND_OK:
                problems.append(f"{key}: kind non valido '{kind}'")
            if conf not in CONF_OK:
                problems.append(f"{key}: confidence non valida '{conf}'")
            notes[key] = {
                "kind": kind,
                "preparations": nt.get("preparations", []) or [],
                "cuisines": nt.get("cuisines", []) or [],
                "reason": nt.get("reason"),
                "source_page": nt.get("source_page"),
                "confidence": conf,
            }

    covered = sum(1 for k in edge_keys if k in notes)
    missing_edges = sorted(edge_keys - set(notes.keys()))
    owners_present = {os.path.splitext(os.path.basename(f))[0] for f in files}

    out_obj = {
        "_meta": {
            "layer": "book.note_synth (solo fatti)",
            "policy": "Solo fatti estratti (preparazioni/prodotti, cucine, motivo breve originale) + citazione di pagina. NESSUNA prosa originale memorizzata.",
            "page_ref": "source_page = pagina fisica del PDF (1-based)",
            "coverage": f"{covered}/{len(edge_keys)} archi con nota",
        },
        "notes": dict(sorted(notes.items())),
    }
    json.dump(out_obj, open(os.path.join(OUT, "note.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    # report
    print("=" * 64)
    print(f"File per-ingrediente trovati: {len(files)} / 99")
    print(f"Note totali (uniche):         {len(notes)}")
    print(f"Copertura archi:              {covered}/{len(edge_keys)}")
    print(f"Duplicati (coppie doppie):    {dup}")
    print(f"Problemi rilevati:            {len(problems)}")
    conf_counts = Counter(n["confidence"] for n in notes.values())
    print(f"Confidenza:                   {dict(conf_counts)}")
    if len(files) < 99:
        missing_files = sorted({os.path.splitext(os.path.basename(f))[0] for f in
                                glob.glob(os.path.join(BYOWNER, '*.json'))})
        print(f"\n(ATTESI 99 file; presenti {len(files)})")
    if missing_edges:
        print(f"\nArchi SENZA nota ({len(missing_edges)}): {missing_edges[:20]}{' ...' if len(missing_edges)>20 else ''}")
    if problems:
        print("\nPrimi problemi:")
        for p in problems[:15]:
            print("  -", p)
    print("\nScritto:", os.path.join(OUT, "note.json"))


if __name__ == "__main__":
    main()
