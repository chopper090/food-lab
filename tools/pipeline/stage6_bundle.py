#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FOOD_LAB pipeline - stage 6: BUNDLE
Combina famiglie + ingredienti + archi + note in un unico data.json (layer 'book'
in sola lettura) piu' i layer 'meta' (metadati utente: stagione/origine/tipo) e
'user' (vuoti). E' l'unico file che l'app caricara'.
"""
import os, sys, json
from collections import defaultdict

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
DATADIR = os.path.join(HERE, "..", "..", "data")   # FOOD_LAB/data/
DATADIR = os.path.abspath(DATADIR)


def load(name):
    with open(os.path.join(OUT, name), encoding="utf-8") as fh:
        return json.load(fh)


def main():
    fams = load("famiglie.json")
    ings = load("ingredienti.json")
    edges = load("archi.json")
    note_doc = load("note.json")
    notes = note_doc.get("notes", {})

    meta_path = os.path.join(OUT, "meta_ingredients.json")
    ingredient_meta = {}
    if os.path.exists(meta_path):
        ingredient_meta = json.load(open(meta_path, encoding="utf-8")).get("ingredient_meta", {})

    ext_path = os.path.join(OUT, "ext.json")
    ext = {"dishes": [], "occasions": []}
    if os.path.exists(ext_path):
        ext = json.load(open(ext_path, encoding="utf-8"))

    matrix_path = os.path.join(OUT, "matrix.json")
    matrix = {"taxonomy": [], "profiles": {}}
    if os.path.exists(matrix_path):
        matrix = json.load(open(matrix_path, encoding="utf-8"))

    # grado per ingrediente
    deg = defaultdict(int)
    for e in edges:
        deg[e["a"]] += 1
        deg[e["b"]] += 1

    ingredients = [{
        "id": g["id"], "name": g["name"], "family": g["family"],
        "degree": deg[g["id"]], "source_page": g["source_page"],
    } for g in ings]

    out_edges = []
    for e in edges:
        key = f"{e['a']}|{e['b']}"
        n = notes.get(key, {})
        out_edges.append({
            "a": e["a"], "b": e["b"],
            "owner": e.get("owner"),
            "page": n.get("source_page"),
            "evidence": e.get("evidence"),
            "kind": n.get("kind"),
            "preparations": n.get("preparations", []),
            "cuisines": n.get("cuisines", []),
            "reason": n.get("reason"),
            "confidence": n.get("confidence", e.get("confidence")),
        })

    data = {
        "schema_version": "1.0.0",
        "source": {
            "work": "La grammatica dei sapori",
            "author": "Niki Segnit",
            "edition": "IT, trad. Cristina Pradella",
            "extracted_pages": "17-606",
            "license_note": "Solo fatti (accostamenti, preparazioni/prodotti, cucine, motivo breve originale) + citazione di pagina. Nessuna prosa originale.",
        },
        "book": {
            "families": fams,
            "ingredients": ingredients,
            "edges": out_edges,
        },
        "meta": {
            "ingredient_meta": ingredient_meta,
            "schema": {
                "season": ["primavera", "estate", "autunno", "inverno"],
                "type": ["frutta", "verdura", "carne", "pesce", "latticino", "spezia",
                          "erba", "frutta secca", "dispensa", "altro"],
                "origin": ["Mediterraneo", "Europa", "Asia", "Africa", "Americhe",
                           "Medio Oriente", "varie"],
                "locality": ["Locale", "Italiano", "Mediterraneo", "Importato"],
            },
        },
        "ext": ext,
        "matrix": matrix,
        "user": {
            "base": {"city": "Messina", "region": "Sicilia"},
            "favorites": [], "notes": {}, "saved_combos": [], "meta_overrides": {},
        },
    }

    os.makedirs(DATADIR, exist_ok=True)
    path = os.path.join(DATADIR, "data.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)

    size_kb = os.path.getsize(path) / 1024
    n_prep = sum(len(e["preparations"]) for e in out_edges)
    print("=" * 60)
    print(f"data.json scritto: {path}")
    print(f"  dimensione:     {size_kb:.0f} KB")
    print(f"  famiglie:       {len(fams)}")
    print(f"  ingredienti:    {len(ingredients)}")
    print(f"  archi:          {len(out_edges)}")
    print(f"  preparazioni totali catturate: {n_prep}")
    print(f"  archi con kind: {sum(1 for e in out_edges if e['kind'])}")
    print(f"  ext: {len(ext.get('dishes', []))} piatti, {len(ext.get('occasions', []))} occasioni")


if __name__ == "__main__":
    main()
