#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FOOD_LAB - LAYER 'matrix' (Fase 6): profilo aromatico per ingrediente, ispirato
alla rappresentazione di "The Flavor Matrix" (sunburst a raggi di lunghezza variabile).
NB: NON dati del libro (immagine, non estraibile; valori proprietari). Qui:
  - TASSONOMIA dei sapori (categorie + descrittori) trascritta dalla ruota di copertina;
  - PROFILI = base AI DERIVATA dai nostri metadati (famiglia + tipologia) + override
    per gli ingredienti caratteristici. _source:"ai", DA VALIDARE, modificabile.
Output: out/matrix.json  ({taxonomy, profiles}).
"""
import os, sys, json

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

# (id, nome, colore, [(descrittore, peso 0-1), ...])
CATS = [
 ("fruttato","Fruttato","#c0345b",[("agrumato",1.0),("frutti di bosco",.8),("frutta arborea",.9),("tropicale",.7),("melone",.6)]),
 ("frutta_essiccata","Frutta essiccata","#7a2e43",[("uvetta",.8),("fico secco",.7),("dattero",.6)]),
 ("floreale","Floreale","#d98aa8",[("fiori bianchi",.8),("miele",.7),("camomilla",.6),("rosa",.7)]),
 ("erbaceo","Erbaceo","#7fb04f",[("basilico/menta",1.0),("prezzemolo",.8),("aneto/finocchio",.7),("coriandolo",.7)]),
 ("vegetale","Vegetale","#4f8f3f",[("verde",.9),("brassica",.7),("terroso",.7),("fungo",.6)]),
 ("agrumato","Agrumato","#cdb52e",[("limone",1.0),("arancia",.9),("bergamotto",.7)]),
 ("caseario","Caseario","#5b8bc0",[("burro",.9),("panna",.8),("yogurt",.7),("formaggio",.8)]),
 ("marino","Marino","#2f9c9c",[("pesce",.9),("mollusco",.7),("alga/salino",.7)]),
 ("legnoso","Legnoso","#6b4a2b",[("legno",.8),("resina",.6),("vaniglia",.8)]),
 ("terpenico","Terpenico","#3f6f4a",[("pino/balsamico",.8),("eucalipto",.6)]),
 ("speziato","Speziato","#d9822b",[("spezie dolci",1.0),("spezie calde",.9),("semi",.7)]),
 ("pungente","Pungente","#c79a2e",[("allium",1.0),("senape/rafano",.8),("peperoncino",.8)]),
 ("affumicato","Affumicato/Tostato","#8a5a3c",[("affumicato",.8),("tostato",.9),("bruciato",.6)]),
 ("maillard","Maillard/Carnoso","#9c4a3a",[("carne",1.0),("brodo/umami",.9),("pane",.7)]),
 ("caramello","Caramello/Dolce","#cf9a3a",[("caramello",.9),("malto",.7),("vaniglia dolce",.8)]),
 ("cioccolato","Cioccolato/Caffe","#4a2f25",[("cacao",1.0),("caffe",.8),("tostato dolce",.7)]),
 ("frutta_guscio","Frutta a guscio","#c9b48e",[("mandorla",.9),("nocciola",.8),("noce",.8)]),
 ("alcolico","Alcolico","#7d4a6b",[("vino",.8),("distillato",.6),("birra",.6)]),
]
CAT_IDS = {c[0] for c in CATS}

# tipologia -> pesi categoria
TYPE_W = {
 "frutta": {"fruttato":1.0,"floreale":.4,"agrumato":.3},
 "verdura": {"vegetale":1.0,"erbaceo":.3},
 "carne": {"maillard":1.0,"affumicato":.4},
 "pesce": {"marino":1.0,"maillard":.3},
 "latticino": {"caseario":1.0,"maillard":.2},
 "spezia": {"speziato":1.0,"terpenico":.5,"pungente":.3},
 "erba": {"erbaceo":1.0,"terpenico":.6},
 "frutta secca": {"frutta_guscio":1.0,"caramello":.3,"cioccolato":.2},
 "dispensa": {"cioccolato":.7,"caramello":.5,"maillard":.3},
 "altro": {"vegetale":.3,"maillard":.3},
}
# famiglia (nome minuscolo) -> pesi categoria
FAM_W = {
 "tostati": {"cioccolato":1.0,"caramello":.5,"frutta_guscio":.4,"affumicato":.3},
 "carnosi": {"maillard":1.0,"affumicato":.4},
 "caseari": {"caseario":1.0},
 "di terra": {"vegetale":.9,"terpenico":.2},
 "senapati": {"pungente":1.0,"vegetale":.4},
 "sulfurei": {"pungente":1.0,"vegetale":.4},
 "di mare": {"marino":1.0},
 "sale e salamoia": {"marino":.6,"maillard":.4,"pungente":.2},
 "erbe e verde": {"erbaceo":1.0,"terpenico":.5,"vegetale":.4},
 "speziati": {"speziato":1.0,"terpenico":.4},
 "di bosco": {"frutta_guscio":.6,"vegetale":.5,"legnoso":.4},
 "fruttati freschi": {"fruttato":1.0,"agrumato":.3},
 "fruttati cremosi": {"fruttato":.9,"caramello":.3,"caseario":.2},
 "agrumati": {"agrumato":1.0,"fruttato":.6,"floreale":.2},
 "di rovo e siepe": {"erbaceo":.7,"fruttato":.6,"terpenico":.4},
 "fruttati fioriti": {"fruttato":.8,"floreale":.7},
}
# override per ingredienti caratteristici (id -> pesi categoria)
OVR = {
 "cioccolato":{"cioccolato":1.0,"caramello":.6,"frutta_guscio":.3},
 "cioccolato_bianco":{"caramello":1.0,"caseario":.6,"floreale":.4},
 "caffe":{"cioccolato":.9,"affumicato":.6,"caramello":.3},
 "vaniglia":{"caramello":1.0,"floreale":.5,"legnoso":.4},
 "limone":{"agrumato":1.0,"fruttato":.5},"lime":{"agrumato":1.0,"terpenico":.4},
 "arancia":{"agrumato":1.0,"fruttato":.6,"floreale":.3},"pompelmo":{"agrumato":1.0,"pungente":.3},
 "pomodoro":{"vegetale":.7,"fruttato":.5,"maillard":.5},
 "basilico":{"erbaceo":1.0,"terpenico":.6,"floreale":.3},"menta":{"erbaceo":1.0,"terpenico":.7},
 "anice":{"erbaceo":.7,"speziato":.7,"terpenico":.6},"rosmarino":{"terpenico":.9,"erbaceo":.6,"legnoso":.4},
 "zenzero":{"speziato":1.0,"terpenico":.5,"pungente":.4},"cannella":{"speziato":1.0,"caramello":.5},
 "aglio":{"pungente":1.0},"cipolla":{"pungente":.9,"caramello":.3},
 "funghi":{"vegetale":.7,"maillard":.7},"tartufo":{"vegetale":.5,"maillard":.6,"pungente":.4},
 "fragola":{"fruttato":1.0,"floreale":.5},"mango":{"fruttato":1.0,"floreale":.3},
 "cocco":{"fruttato":.6,"caseario":.4,"frutta_guscio":.4},"banana":{"fruttato":1.0,"floreale":.3},
 "mandorla":{"frutta_guscio":1.0,"floreale":.3,"caramello":.3},
 "oliva":{"vegetale":.5,"fruttato":.4,"marino":.3},
 "pesce_grasso":{"marino":1.0,"maillard":.3},"acciuga":{"marino":1.0,"maillard":.4},
 "manzo":{"maillard":1.0,"affumicato":.3},"maiale":{"maillard":1.0,"caramello":.3},
 "fico":{"fruttato":.9,"frutta_essiccata":.6,"floreale":.3},
 "uva":{"fruttato":.9,"alcolico":.5},"mela":{"fruttato":1.0,"floreale":.3},
 "zafferano":{"speziato":.8,"floreale":.5,"legnoso":.4},
 "miele":{"floreale":1.0,"caramello":.6},  # non-ingredient safeguard (ignorato se assente)
}


def main():
    ings = json.load(open(os.path.join(OUT, "ingredienti.json"), encoding="utf-8"))
    fams = {f["id"]: f["name"] for f in json.load(open(os.path.join(OUT, "famiglie.json"), encoding="utf-8"))}
    meta = json.load(open(os.path.join(OUT, "meta_ingredients.json"), encoding="utf-8")).get("ingredient_meta", {})

    # validazione: tutte le categorie citate esistono
    bad = set()
    for tbl in (TYPE_W, FAM_W, OVR):
        for d in tbl.values():
            bad |= (set(d) - CAT_IDS)
    if bad:
        print("!! categorie inesistenti nei pesi:", sorted(bad)); sys.exit(1)

    profiles = {}
    for g in ings:
        iid = g["id"]; fam = fams.get(g["family"], "").lower(); typ = (meta.get(iid, {}) or {}).get("type", "")
        raw = {}
        def add(d, k):
            for c, w in (d or {}).items(): raw[c] = raw.get(c, 0) + k * w
        add(TYPE_W.get(typ), 0.45); add(FAM_W.get(fam), 0.55); add(OVR.get(iid), 1.0)
        if not raw:
            continue
        m = max(raw.values())
        prof = {c: round(100 * v / m) for c, v in raw.items() if 100 * v / m >= 8}
        profiles[iid] = prof

    taxonomy = [{"id": c[0], "name": c[1], "color": c[2],
                 "descriptors": [{"name": d[0], "w": d[1]} for d in c[3]]} for c in CATS]
    obj = {
        "_meta": {"policy": "NON dal libro: tassonomia dalla ruota di copertina; profili = base AI derivata da famiglia+tipologia (+override), _source:'ai', DA VALIDARE. Le 'rules' permettono il ricalcolo live nell'app (così gli edit ai metadati si propagano)."},
        "taxonomy": taxonomy,
        "rules": {"type_w": TYPE_W, "fam_w": FAM_W, "ovr": OVR},
        "profiles": profiles,
    }
    json.dump(obj, open(os.path.join(OUT, "matrix.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    from collections import Counter
    cov = Counter(len(p) for p in profiles.values())
    print(f"OK - {len(taxonomy)} categorie, profili per {len(profiles)}/{len(ings)} ingredienti.")
    print("categorie attive medie/ingrediente:", round(sum(len(p) for p in profiles.values())/max(1,len(profiles)),1))
    print("Scritto:", os.path.join(OUT, "matrix.json"))


if __name__ == "__main__":
    main()
