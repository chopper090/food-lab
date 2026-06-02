#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FOOD_LAB pipeline - stage 1: STRUCTURE
Estrae famiglie (intestazioni MAIUSCOLE size>=27) e ingredienti (intestazioni
Capitalizzate size>=27) dal PDF di "La grammatica dei sapori".
Output deterministico, ancorato al FONT (immune dagli artefatti di glifo della prosa).

NB: i numeri di pagina qui sono l'indice 0-based di pdfplumber (pdf.pages[i]),
    NON il numero stampato sul libro. La mappatura all'eventuale pagina stampata
    sara' gestita in uno stadio successivo.

Uso:
    export FOODPDF="...La grammatica dei sapori....pdf"
    export PYTHONUTF8=1
    python stage1_struct.py
"""
import os, sys, json, re, unicodedata
import pdfplumber

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PDF = os.environ["FOODPDF"]
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

# Range pagine da scansionare (0-based). Le famiglie iniziano a p17; partiamo da p8
# (dopo il frontespizio) ed escludiamo esplicitamente l'header "Introduzione".
SCAN_START, SCAN_END = 8, 607        # 607 escluso -> fino a p606
SIZE_HEADER = 27.0                   # famiglia/ingrediente
SIZE_MEMBER_MIN, SIZE_MEMBER_MAX = 18.0, 27.0   # elenco membri nelle pagine-famiglia
EXCLUDE_HEADERS = {"introduzione"}


def slug(name: str) -> str:
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s


def group_lines(words, ytol=3.5):
    """Raggruppa le parole in righe per coordinata 'top'; ritorna righe ordinate
    dall'alto, ognuna con testo (parole in ordine x) e size massima."""
    lines = []
    for w in words:
        placed = False
        for ln in lines:
            if abs(ln["top"] - w["top"]) <= ytol:
                ln["words"].append(w)
                ln["top"] = min(ln["top"], w["top"])
                placed = True
                break
        if not placed:
            lines.append({"top": w["top"], "words": [w]})
    for ln in lines:
        ln["words"].sort(key=lambda w: w["x0"])
        ln["text"] = " ".join(w["text"] for w in ln["words"]).strip()
        ln["size"] = max(w["size"] for w in ln["words"])
    lines.sort(key=lambda ln: ln["top"])
    return lines


def is_all_caps(text: str) -> bool:
    alpha = [c for c in text if c.isalpha()]
    return bool(alpha) and all(c.isupper() for c in alpha)


def main():
    sections = []   # {page, kind, name, header_size, members_raw:[...]}
    print(f"PDF: {PDF}")
    with pdfplumber.open(PDF) as pdf:
        n = len(pdf.pages)
        print(f"Pagine totali: {n}\n")
        for i in range(SCAN_START, min(SCAN_END, n)):
            page = pdf.pages[i]
            words = page.extract_words(extra_attrs=["size", "fontname"])
            if not words:
                continue
            big = [w for w in words if w.get("size", 0) >= SIZE_HEADER]
            if not big:
                continue
            hlines = group_lines(big)
            header = hlines[0]["text"]
            hsize = hlines[0]["size"]
            if slug(header) in EXCLUDE_HEADERS:
                continue
            if is_all_caps(header):
                # pagina-famiglia: raccogli i membri (size 18..27) come righe
                mwords = [w for w in words
                          if SIZE_MEMBER_MIN <= w.get("size", 0) < SIZE_MEMBER_MAX]
                mlines = [ln["text"] for ln in group_lines(mwords) if ln["text"]]
                sections.append({"page": i, "kind": "family", "name": header,
                                 "header_size": round(hsize, 1), "members_raw": mlines})
            else:
                sections.append({"page": i, "kind": "ingredient", "name": header,
                                 "header_size": round(hsize, 1), "members_raw": []})

    # --- Costruzione famiglie e assegnazione ingredienti per intervallo di pagine ---
    sections.sort(key=lambda s: s["page"])
    families = []           # {id,name,source_page,members_byrange:[ids],members_listed:[ids]}
    ingredients = []        # {id,name,family,source_page}
    canonical = {}          # slug -> name (autorita': i titoli di sezione ingrediente)

    # primo giro: raccogli i nomi canonici degli ingredienti
    for s in sections:
        if s["kind"] == "ingredient":
            canonical.setdefault(slug(s["name"]), s["name"])

    def match_member(raw):
        """Normalizza un nome-membro letto dalla pagina-famiglia contro il vocabolario
        canonico. Ritorna (id|None)."""
        sg = slug(raw)
        if sg in canonical:
            return sg
        # tolleranza: rimuovi eventuali residui (numeri di pagina, trattini)
        sg2 = re.sub(r"_?\d+$", "", sg)
        if sg2 in canonical:
            return sg2
        return None

    cur_family = None
    for s in sections:
        if s["kind"] == "family":
            fid = slug(s["name"])
            listed = []
            unmatched = []
            for raw in s["members_raw"]:
                mid = match_member(raw)
                (listed if mid else unmatched).append(mid or raw)
            cur_family = {"id": fid, "name": s["name"].title(),
                          "name_raw": s["name"], "source_page": s["page"],
                          "members_listed": listed, "members_unmatched": unmatched,
                          "members_byrange": []}
            families.append(cur_family)
        else:
            iid = slug(s["name"])
            fam = cur_family["id"] if cur_family else None
            ingredients.append({"id": iid, "name": s["name"],
                                "family": fam, "source_page": s["page"]})
            if cur_family is not None:
                cur_family["members_byrange"].append(iid)

    # --- G3: confronto elenco-membri (pagina-famiglia) vs sezioni trovate (intervallo) ---
    g3 = []
    for f in families:
        listed = set(f["members_listed"])
        byrange = set(f["members_byrange"])
        g3.append({
            "family": f["name"], "source_page": f["source_page"],
            "n_listed": len(f["members_listed"]),
            "n_byrange": len(f["members_byrange"]),
            "only_listed": sorted(listed - byrange),
            "only_byrange": sorted(byrange - listed),
            "unmatched_raw": f["members_unmatched"],
            "ok": listed == byrange and not f["members_unmatched"],
        })

    # --- Scrittura output ---
    fam_out = [{"id": f["id"], "name": f["name"], "source_page": f["source_page"],
                "members": f["members_byrange"]} for f in families]
    with open(os.path.join(OUT, "famiglie.json"), "w", encoding="utf-8") as fh:
        json.dump(fam_out, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(OUT, "ingredienti.json"), "w", encoding="utf-8") as fh:
        json.dump(ingredients, fh, ensure_ascii=False, indent=2)
    with open(os.path.join(OUT, "qa_g3_struct.json"), "w", encoding="utf-8") as fh:
        json.dump(g3, fh, ensure_ascii=False, indent=2)

    # --- Report a video ---
    print("=" * 64)
    print(f"FAMIGLIE: {len(families)}    INGREDIENTI: {len(ingredients)}")
    print("=" * 64)
    for f, q in zip(families, g3):
        flag = "OK" if q["ok"] else "!!"
        names = [next((g["name"] for g in ingredients if g["id"] == mid), mid)
                 for mid in f["members_byrange"]]
        print(f"\n[{flag}] {f['name']} (p{f['source_page']}, size {f['header_size'] if 'header_size' in f else '?'})"
              f"  -- {len(names)} ingredienti")
        print("     " + ", ".join(names))
        if not q["ok"]:
            if q["only_listed"]:
                print(f"     solo in elenco-pagina: {q['only_listed']}")
            if q["only_byrange"]:
                print(f"     solo per intervallo:   {q['only_byrange']}")
            if q["unmatched_raw"]:
                print(f"     membri non risolti:    {q['unmatched_raw']}")

    n_ok = sum(1 for q in g3 if q["ok"])
    print("\n" + "=" * 64)
    print(f"G3 (riconciliazione elenco vs intervallo): {n_ok}/{len(g3)} famiglie OK")
    print(f"Atteso: 16 famiglie / 99 ingredienti.  Trovato: {len(families)} / {len(ingredients)}")
    print("Output in:", OUT)


if __name__ == "__main__":
    main()
