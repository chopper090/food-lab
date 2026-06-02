#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FOOD_LAB pipeline - stage 3: RESOLVE + QA
- Canonicalizza owner/partner contro i 99 ingredienti (slug case/accent-fold).
- Risolve i rimandi: ogni xref (A,B) corrisponde all'arco completo (B,A); la pagina
  della trattazione si recupera per struttura (dove vive il full), non dal testo.
- Deduplica in archi NON orientati.
- QA: G1 (vocabolario chiuso), G2 (reciprocita'), G4 (invariante conteggi).

Input:  out/ingredienti.json, out/archi_raw.json
Output: out/archi.json, out/qa_edges.json
"""
import os, sys, json, re, unicodedata
from collections import defaultdict

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def slug(name: str) -> str:
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def load(name):
    with open(os.path.join(OUT, name), encoding="utf-8") as fh:
        return json.load(fh)


def main():
    ingredients = load("ingredienti.json")
    raw = load("archi_raw.json")
    canonical = {ing["id"]: ing["name"] for ing in ingredients}  # id -> name

    # --- Canonicalizzazione estremi ---
    unmatched = []          # (owner_raw|partner_raw, page) non risolti -> G1
    directed = []           # {o, p, page, kind}
    for r in raw:
        oid, pid = slug(r["owner_raw"]), slug(r["partner_raw"])
        bad = [x for x, raw_name in ((oid, r["owner_raw"]), (pid, r["partner_raw"]))
               if x not in canonical]
        if bad:
            unmatched.append({"owner_raw": r["owner_raw"], "partner_raw": r["partner_raw"],
                              "page": r["page"], "kind": r["kind"],
                              "missing": [r["owner_raw"] if oid not in canonical else None,
                                          r["partner_raw"] if pid not in canonical else None]})
            continue
        directed.append({"o": oid, "p": pid, "page": r["page"], "kind": r["kind"]})

    # --- Mappa archi completi (owner,partner)->pagina ---
    full_map = {}
    full_dups = []
    for d in directed:
        if d["kind"] != "full":
            continue
        key = (d["o"], d["p"])
        if key in full_map:
            full_dups.append({"pair": key, "pages": [full_map[key], d["page"]]})
        else:
            full_map[key] = d["page"]

    xref_set = {(d["o"], d["p"]) for d in directed if d["kind"] == "xref"}

    # --- G2 reciprocita' ---
    # ogni full (A,B) dovrebbe avere xref (B,A); ogni xref (A,B) un full (B,A)
    full_without_xref = [k for k in full_map if (k[1], k[0]) not in xref_set]
    xref_without_full = [k for k in xref_set if (k[1], k[0]) not in full_map]

    # --- Costruzione archi NON orientati ---
    edges = {}   # frozenset{a,b} -> record
    for (o, p), page in full_map.items():
        key = frozenset((o, p))
        a, b = sorted((o, p))
        if key not in edges:
            edges[key] = {"a": a, "b": b, "owner": o, "writeup_page": page,
                          "evidence": "full",
                          "confidence": "high", "needs_review": False}
    # xref-only: coppia nota solo da rimando senza full reciproco
    xref_only = 0
    for (o, p) in xref_set:
        key = frozenset((o, p))
        if key in edges:
            continue
        if (p, o) in full_map:   # il full reciproco esiste -> gia' coperto
            continue
        a, b = sorted((o, p))
        edges[key] = {"a": a, "b": b, "owner": None, "writeup_page": None,
                      "evidence": "xref", "confidence": "needs_review",
                      "needs_review": True}
        xref_only += 1

    edge_list = sorted(edges.values(), key=lambda e: (e["a"], e["b"]))

    # --- Grado per ingrediente ---
    degree = defaultdict(int)
    for e in edge_list:
        degree[e["a"]] += 1
        degree[e["b"]] += 1

    # --- Scrittura ---
    with open(os.path.join(OUT, "archi.json"), "w", encoding="utf-8") as fh:
        json.dump(edge_list, fh, ensure_ascii=False, indent=2)

    qa = {
        "n_raw_directed": len(raw),
        "n_unmatched_G1": len(unmatched),
        "unmatched": unmatched,
        "n_full": len(full_map),
        "n_xref": len(xref_set),
        "n_full_duplicate_headers": len(full_dups),
        "full_dups": full_dups,
        "G2_full_without_xref": [list(k) for k in full_without_xref],
        "G2_xref_without_full": [list(k) for k in xref_without_full],
        "n_undirected_edges": len(edge_list),
        "n_xref_only_edges": xref_only,
        "degree_min": min(degree.values()) if degree else 0,
        "degree_max": max(degree.values()) if degree else 0,
        "degree_top": sorted(((canonical[k], v) for k, v in degree.items()),
                             key=lambda kv: -kv[1])[:8],
    }
    with open(os.path.join(OUT, "qa_edges.json"), "w", encoding="utf-8") as fh:
        json.dump(qa, fh, ensure_ascii=False, indent=2)

    # --- Report ---
    print("=" * 64)
    print(f"Testate grezze:            {qa['n_raw_directed']}")
    print(f"  full:                    {qa['n_full']}")
    print(f"  xref:                    {qa['n_xref']}")
    print(f"ARCHI non orientati:       {qa['n_undirected_edges']}")
    print(f"  di cui solo-xref:        {qa['n_xref_only_edges']}")
    print("-" * 64)
    print(f"G1 estremi non risolti:    {qa['n_unmatched_G1']}   (atteso 0)")
    print(f"G2 full senza xref recipr: {len(full_without_xref)}")
    print(f"G2 xref senza full recipr: {len(xref_without_full)}")
    print(f"   testate full duplicate: {qa['n_full_duplicate_headers']}")
    print(f"Grado min/max:             {qa['degree_min']} / {qa['degree_max']}")
    print(f"Piu' connessi: " + ", ".join(f"{n}({v})" for n, v in qa["degree_top"]))
    if unmatched:
        print("\nESEMPI estremi non risolti (G1):")
        for u in unmatched[:12]:
            print(f"  p{u['page']} [{u['kind']}] {u['owner_raw']} & {u['partner_raw']}"
                  f"  -> manca: {[x for x in u['missing'] if x]}")
    print("\nOutput:", os.path.join(OUT, "archi.json"))


if __name__ == "__main__":
    main()
