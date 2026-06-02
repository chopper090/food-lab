#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FOOD_LAB - costruzione LAYER METADATI (esterno al libro)
tipologia / stagione / provenienza per i 99 ingredienti.
NB: dati NON dal libro. Stagione ancorata all'Italia. Provenienza = origine
geografica indicativa. Tutto etichettato _source:"ai" e DA VALIDARE.
Lo script VALIDA che le chiavi coincidano esattamente con i 99 id canonici.

Output: out/meta_ingredients.json
"""
import os, sys, json

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

# id -> (type, [season...], origin)
TY = "type"
META = {
    # Tostati
    "cioccolato": ("dispensa", ["tutto l'anno"], "Americhe"),
    "caffe": ("dispensa", ["tutto l'anno"], "Africa"),
    "arachide": ("frutta secca", ["tutto l'anno"], "Americhe"),
    # Carnosi
    "pollo": ("carne", ["tutto l'anno"], "varie"),
    "maiale": ("carne", ["tutto l'anno"], "varie"),
    "black_pudding": ("carne", ["tutto l'anno"], "Europa"),
    "fegato": ("carne", ["tutto l'anno"], "varie"),
    "manzo": ("carne", ["tutto l'anno"], "varie"),
    "agnello": ("carne", ["tutto l'anno"], "varie"),
    # Caseari
    "formaggio_di_capra": ("latticino", ["tutto l'anno"], "Mediterraneo"),
    "formaggio_con_crosta_lavata": ("latticino", ["tutto l'anno"], "Europa"),
    "formaggio_erborinato": ("latticino", ["tutto l'anno"], "Europa"),
    "formaggio_stagionato": ("latticino", ["tutto l'anno"], "Europa"),
    "formaggio_fresco": ("latticino", ["tutto l'anno"], "Europa"),
    # Di terra
    "funghi": ("verdura", ["autunno"], "Europa"),
    "melanzana": ("verdura", ["estate", "autunno"], "Asia"),
    "cumino": ("spezia", ["tutto l'anno"], "Medio Oriente"),
    "barbabietola": ("verdura", ["autunno", "inverno"], "Europa"),
    "patata": ("verdura", ["tutto l'anno"], "Americhe"),
    "sedano": ("verdura", ["tutto l'anno"], "Mediterraneo"),
    # Senapati
    "crescione": ("verdura", ["primavera", "autunno"], "Europa"),
    "cappero": ("dispensa", ["tutto l'anno"], "Mediterraneo"),
    "rafano": ("spezia", ["autunno", "inverno"], "Europa"),
    # Sulfurei
    "cipolla": ("verdura", ["tutto l'anno"], "Asia"),
    "aglio": ("verdura", ["tutto l'anno"], "Asia"),
    "tartufo": ("altro", ["autunno", "inverno"], "Mediterraneo"),
    "cavolo": ("verdura", ["autunno", "inverno"], "Europa"),
    "navone": ("verdura", ["autunno", "inverno"], "Europa"),
    "cavolfiore": ("verdura", ["autunno", "inverno"], "Mediterraneo"),
    "broccolo": ("verdura", ["autunno", "inverno"], "Mediterraneo"),
    "carciofo_romanesco": ("verdura", ["primavera"], "Mediterraneo"),
    "asparago": ("verdura", ["primavera"], "Mediterraneo"),
    "uovo": ("altro", ["tutto l'anno"], "varie"),
    # Di mare
    "frutti_di_mare": ("pesce", ["tutto l'anno"], "varie"),
    "pesce_bianco": ("pesce", ["tutto l'anno"], "varie"),
    "ostrica": ("pesce", ["autunno", "inverno"], "Europa"),
    "caviale": ("pesce", ["tutto l'anno"], "Asia"),
    "pesce_grasso": ("pesce", ["tutto l'anno"], "varie"),
    # Sale e salamoia
    "acciuga": ("pesce", ["tutto l'anno"], "Mediterraneo"),
    "pesce_affumicato": ("pesce", ["tutto l'anno"], "Europa"),
    "bacon": ("carne", ["tutto l'anno"], "varie"),
    "prosciutto_crudo": ("carne", ["tutto l'anno"], "Mediterraneo"),
    "oliva": ("altro", ["tutto l'anno"], "Mediterraneo"),
    # Erbe e verde
    "zafferano": ("spezia", ["tutto l'anno"], "Medio Oriente"),
    "anice": ("spezia", ["tutto l'anno"], "Mediterraneo"),
    "cetriolo": ("verdura", ["estate"], "Asia"),
    "aneto": ("erba", ["primavera", "estate"], "Asia"),
    "prezzemolo": ("erba", ["tutto l'anno"], "Mediterraneo"),
    "foglie_di_coriandolo": ("erba", ["primavera", "estate"], "Asia"),
    "avocado": ("frutta", ["tutto l'anno"], "Americhe"),
    "piselli": ("verdura", ["primavera"], "Mediterraneo"),
    "peperone": ("verdura", ["estate"], "Americhe"),
    "peperoncino_piccante": ("spezia", ["estate"], "Americhe"),
    # Speziati
    "basilico": ("erba", ["estate"], "Asia"),
    "cannella": ("spezia", ["tutto l'anno"], "Asia"),
    "chiodi_di_garofano": ("spezia", ["tutto l'anno"], "Asia"),
    "noce_moscata": ("spezia", ["tutto l'anno"], "Asia"),
    "pastinaca": ("verdura", ["autunno", "inverno"], "Europa"),
    # Di bosco
    "carota": ("verdura", ["tutto l'anno"], "Asia"),
    "zucca": ("verdura", ["autunno", "inverno"], "Americhe"),
    "castagna": ("frutta secca", ["autunno"], "Mediterraneo"),
    "noce": ("frutta secca", ["autunno"], "Asia"),
    "nocciola": ("frutta secca", ["autunno"], "Mediterraneo"),
    "mandorla": ("frutta secca", ["tutto l'anno"], "Mediterraneo"),
    # Fruttati freschi
    "ciliegia": ("frutta", ["primavera", "estate"], "Asia"),
    "anguria": ("frutta", ["estate"], "Africa"),
    "uva": ("frutta", ["autunno"], "Mediterraneo"),
    "rabarbaro": ("verdura", ["primavera"], "Asia"),
    "pomodoro": ("verdura", ["estate"], "Americhe"),
    "fragola": ("frutta", ["primavera", "estate"], "Europa"),
    "ananas": ("frutta", ["tutto l'anno"], "Americhe"),
    "mela": ("frutta", ["autunno", "inverno"], "Asia"),
    "pera": ("frutta", ["autunno"], "Europa"),
    # Fruttati cremosi
    "banana": ("frutta", ["tutto l'anno"], "Asia"),
    "melone": ("frutta", ["estate"], "Africa"),
    "albicocca": ("frutta", ["estate"], "Asia"),
    "pesca": ("frutta", ["estate"], "Asia"),
    "cocco": ("frutta", ["tutto l'anno"], "Asia"),
    "mango": ("frutta", ["tutto l'anno"], "Asia"),
    # Agrumati
    "arancia": ("frutta", ["inverno"], "Asia"),
    "pompelmo": ("frutta", ["inverno"], "varie"),
    "lime": ("frutta", ["tutto l'anno"], "Asia"),
    "limone": ("frutta", ["tutto l'anno"], "Asia"),
    "zenzero": ("spezia", ["tutto l'anno"], "Asia"),
    "cardamomo": ("spezia", ["tutto l'anno"], "Asia"),
    # Di rovo e siepe
    "rosmarino": ("erba", ["tutto l'anno"], "Mediterraneo"),
    "salvia": ("erba", ["tutto l'anno"], "Mediterraneo"),
    "ginepro": ("spezia", ["autunno"], "Europa"),
    "timo": ("erba", ["tutto l'anno"], "Mediterraneo"),
    "menta": ("erba", ["primavera", "estate"], "Europa"),
    "ribes_nero": ("frutta", ["estate"], "Europa"),
    "mora_di_rovo": ("frutta", ["estate"], "Europa"),
    # Fruttati fioriti
    "lampone": ("frutta", ["estate"], "Europa"),
    "fico": ("frutta", ["estate", "autunno"], "Mediterraneo"),
    "rosa": ("altro", ["primavera", "estate"], "Asia"),
    "mirtillo": ("frutta", ["estate"], "Europa"),
    "semi_di_coriandolo": ("spezia", ["tutto l'anno"], "Mediterraneo"),
    "vaniglia": ("spezia", ["tutto l'anno"], "Americhe"),
    "cioccolato_bianco": ("dispensa", ["tutto l'anno"], "Americhe"),
}

# id -> locality (REPERIBILITA' rispetto a una base in Sicilia/Messina, NON origine
# botanica): "Locale" (Sicilia/km0) | "Italiano" | "Mediterraneo" | "Importato".
# Seed AI da disponibilita' agro-alimentare reale (es. pomodoro="Americhe" di origine
# ma "Locale" di reperibilita'). DA VALIDARE.
LOC = {
    # Tostati
    "cioccolato": "Importato", "caffe": "Importato", "arachide": "Importato",
    # Carnosi
    "pollo": "Italiano", "maiale": "Italiano", "black_pudding": "Italiano",
    "fegato": "Italiano", "manzo": "Italiano", "agnello": "Locale",
    # Caseari
    "formaggio_di_capra": "Locale", "formaggio_con_crosta_lavata": "Italiano",
    "formaggio_erborinato": "Italiano", "formaggio_stagionato": "Locale",
    "formaggio_fresco": "Locale",
    # Di terra
    "funghi": "Italiano", "melanzana": "Locale", "cumino": "Mediterraneo",
    "barbabietola": "Italiano", "patata": "Italiano", "sedano": "Locale",
    # Senapati
    "crescione": "Italiano", "cappero": "Locale", "rafano": "Italiano",
    # Sulfurei
    "cipolla": "Locale", "aglio": "Locale", "tartufo": "Italiano", "cavolo": "Italiano",
    "navone": "Italiano", "cavolfiore": "Locale", "broccolo": "Locale",
    "carciofo_romanesco": "Locale", "asparago": "Italiano", "uovo": "Locale",
    # Di mare
    "frutti_di_mare": "Locale", "pesce_bianco": "Locale", "ostrica": "Italiano",
    "caviale": "Importato", "pesce_grasso": "Locale",
    # Sale e salamoia
    "acciuga": "Locale", "pesce_affumicato": "Italiano", "bacon": "Italiano",
    "prosciutto_crudo": "Italiano", "oliva": "Locale",
    # Erbe e verde
    "zafferano": "Mediterraneo", "anice": "Locale", "cetriolo": "Locale",
    "aneto": "Italiano", "prezzemolo": "Locale", "foglie_di_coriandolo": "Mediterraneo",
    "avocado": "Importato", "piselli": "Locale", "peperone": "Locale",
    "peperoncino_piccante": "Locale",
    # Speziati
    "basilico": "Locale", "cannella": "Importato", "chiodi_di_garofano": "Importato",
    "noce_moscata": "Importato", "pastinaca": "Italiano",
    # Di bosco
    "carota": "Locale", "zucca": "Locale", "castagna": "Locale", "noce": "Italiano",
    "nocciola": "Locale", "mandorla": "Locale",
    # Fruttati freschi
    "ciliegia": "Locale", "anguria": "Locale", "uva": "Locale", "rabarbaro": "Italiano",
    "pomodoro": "Locale", "fragola": "Locale", "ananas": "Importato", "mela": "Italiano",
    "pera": "Italiano",
    # Fruttati cremosi
    "banana": "Importato", "melone": "Locale", "albicocca": "Locale", "pesca": "Locale",
    "cocco": "Importato", "mango": "Importato",
    # Agrumati
    "arancia": "Locale", "pompelmo": "Locale", "lime": "Importato", "limone": "Locale",
    "zenzero": "Importato", "cardamomo": "Importato",
    # Di rovo e siepe
    "rosmarino": "Locale", "salvia": "Locale", "ginepro": "Italiano", "timo": "Locale",
    "menta": "Locale", "ribes_nero": "Italiano", "mora_di_rovo": "Locale",
    # Fruttati fioriti
    "lampone": "Italiano", "fico": "Locale", "rosa": "Mediterraneo", "mirtillo": "Italiano",
    "semi_di_coriandolo": "Mediterraneo", "vaniglia": "Importato",
    "cioccolato_bianco": "Importato",
}


def main():
    ings = json.load(open(os.path.join(OUT, "ingredienti.json"), encoding="utf-8"))
    ids = {g["id"] for g in ings}
    keys = set(META)
    missing = sorted(ids - keys)      # ingredienti canonici senza metadati
    extra = sorted(keys - ids)        # chiavi non corrispondenti a un ingrediente
    loc_missing = sorted(keys - set(LOC))   # voci META senza locality

    if missing or extra or loc_missing:
        print("!! VALIDAZIONE FALLITA")
        if missing:
            print(f"  Senza metadati ({len(missing)}): {missing}")
        if extra:
            print(f"  Chiavi estranee ({len(extra)}): {extra}")
        if loc_missing:
            print(f"  Senza locality ({len(loc_missing)}): {loc_missing}")
        sys.exit(1)

    ingredient_meta = {
        k: {"type": v[0], "season": v[1], "origin": v[2], "locality": LOC[k], "_source": "ai"}
        for k, v in META.items()
    }
    obj = {
        "_meta": {
            "policy": "Dati NON dal libro: tipologia/stagione/origine/reperibilita' (locality) assegnati da conoscenza generale. Stagione ancorata all'ITALIA. Origine = provenienza geografica indicativa (botanica/storica). Locality = reperibilita' rispetto a una base in Sicilia/Messina (Locale/Italiano/Mediterraneo/Importato), NON l'origine. DA VALIDARE; tutti i campi modificabili.",
            "season_anchor": "Italia",
            "locality_anchor": "Messina, Sicilia",
        },
        "ingredient_meta": ingredient_meta,
    }
    json.dump(obj, open(os.path.join(OUT, "meta_ingredients.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    from collections import Counter
    print("OK - 99/99 ingredienti coperti, nessuna chiave estranea.")
    print("Tipologie:", dict(Counter(v[0] for v in META.values())))
    print("Reperibilita':", dict(Counter(LOC.values())))
    print("Scritto:", os.path.join(OUT, "meta_ingredients.json"))


if __name__ == "__main__":
    main()
