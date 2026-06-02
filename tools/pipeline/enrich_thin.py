#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FOOD_LAB pipeline - arricchimento note 'thin' / reason vuote.
Gira DOPO stage5_merge (out/note.json) e PRIMA di stage6_bundle.
Per i 36 accostamenti 'thin' con reason vuota, scrive un MOTIVO breve, ORIGINALE
(parafrasi, mai verbatim, <=200 char), derivato dal passo sorgente nello span;
dove la fonte motiva davvero il gusto la confidenza sale a 'medium', altrimenti
resta 'thin' (incluse le coppie che l'autrice giudica mal riuscite). Idempotente.
"""
import os, sys, json

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
NOTE = os.path.join(HERE, "out", "note.json")

# key = "a|b" (a<b, come negli archi). r=reason, c=confidence,
# pa=preparazioni da aggiungere, ca=cucine da aggiungere.
ENRICH = {
 "aglio|cipolla": dict(c="medium", r="Stessa famiglia (Allium) e profilo sulfureo-pungente: insieme sono la base aromatica di mezza cucina. La tradizione li bandisce tra i 'cinque pungenti' (buddismo, jainismo)."),
 "ananas|avocado": dict(c="thin", r="Incontro fra la dolcezza acidula dell'ananas e la grassezza dell'avocado; il libro lo accenna piu' con digressioni storiche che con una vera motivazione di gusto."),
 "anguria|melone": dict(c="medium", r="Stessa famiglia ma generi diversi: l'anguria e' priva degli esteri fruttati dei meloni, percio' si accostano piu' per freschezza e succosita' che per aroma."),
 "arachide|banana": dict(c="medium", r="Il celebre sandwich di Elvis: burro d'arachidi e banana su pane bianco. La grassezza tostata dell'arachide regge la dolcezza morbida della banana."),
 "arachide|vaniglia": dict(c="medium", r="Burro d'arachidi e Marshmallow Fluff alla vaniglia nel sandwich 'fluffernutter': dolce avvolgente contro la nota tostata e salina dell'arachide."),
 "arancia|barbabietola": dict(c="medium", r="Gioco di Heston Blumenthal: gelatine che scambiano colore e sapore tra barbabietola dorata e arancia sanguinella; terrosita' dolce e agrume si rispondono."),
 "arancia|oliva": dict(c="thin", r="Abbinamento d'avanguardia (la cucina futurista di Marinetti, 'Aerocibo'): olive nere e finocchio con kumquat; agrume e oliva in chiave provocatoria."),
 "arancia|rosmarino": dict(c="medium", r="Fiori d'arancio e rosmarino: coppia aromatica collaudata (entrambi simboli nuziali), usata in dolci profumati all'acqua di fiori d'arancio."),
 "avocado|noce_moscata": dict(c="medium", r="Una grattata di noce moscata ravviva l'avocado: su vellutata fredda d'avocado o su avocado farcito di frutti di mare."),
 "bacon|carciofo_romanesco": dict(c="medium", r="Il salato affumicato del bacon esalta il carciofo: insieme in gratin con pangrattato e formaggio o saltati nella pasta."),
 "banana|caviale": dict(c="thin", r="Curiosita' storica: nella Russia degli zar i figli reali univano banana schiacciata e caviale - dolce burroso contro salino."),
 "banana|mandorla": dict(c="medium", r="Una banana split chiede le mandorle tostate: la nota tostata e croccante completa la dolcezza morbida della banana."),
 "banana|pera": dict(c="medium", r="Banana e pera condividono l'estere acetato di isoamile, responsabile del profumo fruttato comune ai dolci che le richiamano."),
 "basilico|uovo": dict(c="medium", r="Il basilico profuma l'uovo senza disperdersi in cottura (a differenza di altri verdi): classico nelle uova strapazzate."),
 "broccolo|noce": dict(c="medium", r="Noce e broccolo insieme nella pasta o tra le verdure saltate: la nota burrosa e amarognola della noce accompagna il broccolo."),
 "caffe|ciliegia": dict(c="medium", r="Coppia da diner americano (la fetta di torta di ciliegie col caffe' di Twin Peaks): l'amaro tostato bilancia il dolce acidulo della ciliegia."),
 "carota|navone": dict(c="medium", r="Spesso serviti insieme: la dolcezza della carota tempera l'amaro del navone (amaro legato alla sensibilita' genetica al composto PROP)."),
 "caviale|pollo": dict(c="thin", r="La carne delicata del pollo fa da base neutra al salino del caviale; accostamento d'alta tavola piu' che di tradizione."),
 "ciliegia|noce": dict(c="medium", r="Coppia all'antica un po' fuori moda: dolci di ciliegie e noci, dove l'amarognolo della noce contrasta il dolce della ciliegia."),
 "ciliegia|pesca": dict(c="thin", r="Due drupe estive affini per dolcezza e acidita'; nel libro l'accostamento e' evocato per immagini (il picnic di Manet) piu' che spiegato."),
 "cioccolato|fragola": dict(c="thin", r="Coppia iconica (la fragola intinta nel cioccolato come pegno d'amore) verso cui l'autrice resta tiepida, preferendole cioccolato e nocciola."),
 "cipolla|menta": dict(c="medium", r="La menta rinfresca la cipolla come il prezzemolo fa con l'aglio (es. nel pane alla cipolla): contrasto fresco al pungente."),
 "fegato|fico": dict(c="medium", r="Abbinamento antichissimo: lo iecur ficatum romano (fegato d'animali ingrassati coi fichi) all'origine della parola 'fegato'; il fico addolcisce il foie gras."),
 "foglie_di_coriandolo|prezzemolo": dict(c="thin", r="Due erbe dalla comune nota verde-erbacea: si possono unire, anche se il coriandolo tende a prevalere."),
 "formaggio_con_crosta_lavata|patata": dict(c="medium", r="Il fruttato Vacherin Mont d'Or fuso sulle patate: grande classico alpino, cremoso e avvolgente."),
 "lampone|mora_di_rovo": dict(c="medium", r="Stesso genere (Rubus) e profili affini; la mora aggiunge note muschiate e di cedro. Da incroci tra i due nasce la loganberry."),
 "maiale|pompelmo": dict(c="medium", ca=["Caraibi"], r="In chiave caraibica: maiale speziato (roti col peperoncino Scotch bonnet) col pompelmo (la bibita Ting); l'amaro acidulo sgrassa la carne."),
 "maiale|tartufo": dict(c="medium", r="Grande classico: l'aroma intenso del tartufo (anche su cinghiale) nobilita le carni grasse di maiale; va usato freschissimo, perche' si ossida in fretta."),
 "manzo|navone": dict(c="medium", pa=["pie"], r="Tipico dei pie rustici: strati di navone e patata sotto il manzo brasato e tenero, che il navone insaporisce assorbendone i succhi."),
 "manzo|pomodoro": dict(c="medium", r="Classico confortante, dal ragu' al Pot Noodle 'Beef and Tomato': l'acidita' del pomodoro alleggerisce la sapidita' grassa del manzo."),
 "melone|zenzero": dict(c="thin", r="Abbinamento tradizionale (lo zenzero 'digestivo' col melone) che pero' l'autrice, dopo un tasting, giudica fallito: peggiora ogni tipo di melone."),
 "oliva|patata": dict(c="medium", pa=["patate in umido","insalata di patate novelle"], r="L'oliva da' sapidita' all'amido neutro della patata: in umido con olio, pomodoro e aglio, o in insalata di patate novelle."),
 "ostrica|peperoncino_piccante": dict(c="thin", r="L'ostrica cruda ravvivata da salse piccanti (alla maniera di New Orleans): il piccante stuzzica la mineralita' iodata."),
 "pastinaca|patata": dict(c="thin", r="Due radici pallide dal ruolo simile in cucina; la patata, arrivata in Europa nel '500, soppianto' la pastinaca, dal sapore piu' dolce e terroso."),
 "pesce_grasso|piselli": dict(c="medium", ca=["New England"], r="Tradizione del New England: salmone bollito con piselli e patate novelle per il 4 luglio; il dolce dei piselli alleggerisce il pesce grasso."),
 "rabarbaro|zenzero": dict(c="thin", r="Accoppiata tradizionale (per presunti benefici digestivi) che l'autrice trova poco riuscita, benche' alcuni chef la propongano (gelato di rabarbaro, brioche allo zenzero)."),
}


def main():
    doc = json.load(open(NOTE, encoding="utf-8"))
    notes = doc.get("notes", {})
    missing = [k for k in ENRICH if k not in notes]
    toolong = [(k, len(v["r"])) for k, v in ENRICH.items() if len(v["r"]) > 200]
    if missing or toolong:
        print("!! VALIDAZIONE FALLITA")
        if missing: print("  chiavi assenti in note.json:", missing)
        if toolong: print("  reason > 200 char:", toolong)
        sys.exit(1)

    bumped = 0
    for k, v in ENRICH.items():
        n = notes[k]
        n["reason"] = v["r"]
        if n.get("confidence") != v["c"]:
            bumped += 1
        n["confidence"] = v["c"]
        if v.get("pa"):
            preps = n.get("preparations") or []
            for p in v["pa"]:
                if p not in preps:
                    preps.append(p)
            n["preparations"] = preps
        if v.get("ca"):
            cui = n.get("cuisines") or []
            for c in v["ca"]:
                if c not in cui:
                    cui.append(c)
            n["cuisines"] = cui

    json.dump(doc, open(NOTE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"OK - arricchiti {len(ENRICH)} accostamenti (reason scritte); confidenza thin->medium su {bumped}.")
    print(f"  lunghezza reason: max {max(len(v['r']) for v in ENRICH.values())} char")


if __name__ == "__main__":
    main()
