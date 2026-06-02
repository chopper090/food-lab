#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FOOD_LAB - rigenera TUTTI i layer derivati e il bundle, in ordine, partendo dagli
output strutturali gia' presenti in out/ (famiglie/ingredienti/archi/note/spans).
NON ripassa il PDF (stage1-5): quelli si lanciano a parte solo se cambia l'estrazione.

  build_metadata -> enrich_thin -> build_ext -> build_matrix -> stage6_bundle -> data.js

Uso:  PYTHONUTF8=1 python tools/pipeline/rebuild_all.py
"""
import os, sys, subprocess, json

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "out")
DATA = os.path.join(ROOT, "data")

STEPS = ["build_metadata.py", "enrich_thin.py", "clean_preps.py", "build_ext.py", "build_matrix.py", "stage6_bundle.py"]

# prerequisiti strutturali (dal PDF) che devono esistere
PREREQ = ["famiglie.json", "ingredienti.json", "archi.json", "note.json"]


def main():
    env = dict(os.environ); env["PYTHONUTF8"] = "1"
    missing = [f for f in PREREQ if not os.path.exists(os.path.join(OUT, f))]
    if missing:
        print("!! mancano output strutturali in out/:", missing)
        print("   Esegui prima stage1-5 (estrazione dal PDF).")
        sys.exit(1)

    for s in STEPS:
        print("\n=== %s ===" % s)
        r = subprocess.run([sys.executable, os.path.join(HERE, s)], env=env)
        if r.returncode != 0:
            print("!! %s ha fallito (exit %d) — interrotto." % (s, r.returncode))
            sys.exit(r.returncode)

    # rigenera data/data.js (wrapper per caricamento via file://)
    src = open(os.path.join(DATA, "data.json"), encoding="utf-8").read()
    open(os.path.join(DATA, "data.js"), "w", encoding="utf-8").write("window.FOODLAB_DATA=" + src + ";\n")

    D = json.loads(src)
    print("\n" + "=" * 60)
    print("REBUILD OK. data.json (%d KB) + data.js rigenerati." % (len(src) // 1024))
    print("  layer:", list(D.keys()))
    print("  book: %d famiglie / %d ingredienti / %d archi" % (
        len(D["book"]["families"]), len(D["book"]["ingredients"]), len(D["book"]["edges"])))
    print("  ext: %d piatti / %d occasioni / %d pairings / %d vini" % (
        len(D["ext"].get("dishes", [])), len(D["ext"].get("occasions", [])),
        len(D["ext"].get("pairings", [])), len(D["ext"].get("wine", {}))))
    print("  matrix: %d categorie / %d profili / rules=%s" % (
        len(D["matrix"].get("taxonomy", [])), len(D["matrix"].get("profiles", {})),
        "si" if D["matrix"].get("rules") else "no"))


if __name__ == "__main__":
    main()
