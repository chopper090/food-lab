#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FOOD_LAB - LAYER ESTERNO 'ext' (Fase 5): piatti + occasioni, internazionali,
collegati ai 99 ingredienti del libro. NON dal libro: conoscenza culinaria
generale, etichettata _source:"ai" e DA VALIDARE; le citazioni a fonti
autorevoli si aggiungono in seguito (modello ibrido).
Output: out/ext.json. Valida che ogni link (ingrediente/piatto/occasione) esista.
"""
import os, sys, json

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

# (id, nome, cucina, paese, categoria, [ingredienti id], [extra non-99], [stagioni], [occasioni id], nota)
DISHES = [
 ("ceviche","Ceviche","Peruviana","Perù","secondo",["pesce_bianco","lime","peperoncino_piccante","cipolla","foglie_di_coriandolo"],["mais","patata dolce"],["estate"],[],"Pesce crudo marinato nel succo di lime (la 'leche de tigre'), con cipolla e coriandolo."),
 ("anticuchos","Anticuchos","Peruviana","Perù","street food",["manzo","aglio","cumino","peperoncino_piccante"],["aceto","ají panca"],[],[],"Spiedini di cuore di manzo marinati e grigliati, street food andino."),
 ("guacamole","Guacamole","Messicana","Messico","salsa",["avocado","lime","foglie_di_coriandolo","cipolla","peperoncino_piccante","pomodoro"],[],["estate"],["cinco_de_mayo"],"Crema di avocado con lime, coriandolo e peperoncino."),
 ("tacos_al_pastor","Tacos al pastor","Messicana","Messico","secondo",["maiale","ananas","cipolla","foglie_di_coriandolo","peperoncino_piccante","lime"],["tortilla di mais"],[],["cinco_de_mayo"],"Maiale marinato e arrostito, servito con ananas, cipolla e coriandolo nella tortilla."),
 ("mole_poblano","Mole poblano","Messicana","Messico","secondo",["cioccolato","peperoncino_piccante","pollo","cannella","mandorla","semi_di_coriandolo"],["semi di sesamo"],[],["cinco_de_mayo","dia_de_muertos"],"Salsa densa e complessa che unisce cacao e peperoncino su carne di pollo."),
 ("hummus","Hummus","Libanese","Libano","antipasto",["aglio","limone","cumino"],["ceci","tahina"],[],[],"Crema di ceci con tahina, aglio e limone; cardine del mezze mediorientale."),
 ("tabbouleh","Tabbouleh","Libanese","Libano","insalata",["prezzemolo","menta","pomodoro","cipolla","limone"],["bulgur"],["estate"],[],"Insalata di prezzemolo e menta con bulgur, pomodoro e limone."),
 ("falafel","Falafel","Mediorientale","Libano","street food",["aglio","prezzemolo","foglie_di_coriandolo","cumino"],["ceci"],[],[],"Polpette fritte di legumi ed erbe speziate."),
 ("baba_ghanoush","Baba ghanoush","Libanese","Libano","antipasto",["melanzana","aglio","limone"],["tahina"],["estate"],[],"Crema affumicata di melanzana arrostita con tahina e limone."),
 ("sushi","Sushi","Giapponese","Giappone","secondo",["pesce_grasso","pesce_bianco"],["riso","alga nori","wasabi"],[],[],"Riso acidulato con pesce crudo; equilibrio fra grasso del pesce e acidità del riso."),
 ("ramen","Ramen","Giapponese","Giappone","zuppa",["maiale","uovo","aglio","zenzero","cipolla"],["noodles","miso","brodo"],["inverno"],[],"Zuppa di noodles in brodo ricco, con maiale e uovo marinato."),
 ("pad_thai","Pad thai","Thailandese","Thailandia","primo",["arachide","lime","peperoncino_piccante","uovo","aglio"],["noodles di riso","tamarindo","germogli di soia"],[],[],"Noodles saltati agrodolci con arachidi, lime e tamarindo."),
 ("green_curry","Curry verde","Thailandese","Thailandia","secondo",["pollo","cocco","basilico","lime","peperoncino_piccante","aglio","zenzero"],["latte di cocco","galanga"],[],[],"Curry al latte di cocco profumato di basilico thai e lime."),
 ("butter_chicken","Butter chicken","Indiana","India","secondo",["pollo","pomodoro","cardamomo","cannella","zenzero","aglio"],["panna","garam masala"],[],["diwali"],"Pollo in salsa cremosa di pomodoro e spezie dolci."),
 ("dal","Dal","Indiana","India","zuppa",["cumino","zenzero","aglio","cipolla"],["lenticchie","curcuma"],[],["diwali"],"Lenticchie speziate, comfort food vegetariano quotidiano."),
 ("biryani","Biryani","Indiana","India","primo",["pollo","zafferano","cardamomo","cannella","chiodi_di_garofano","zenzero"],["riso basmati"],[],["diwali","eid"],"Riso speziato stratificato con carne, profumato allo zafferano."),
 ("paella","Paella","Spagnola","Spagna","primo",["zafferano","frutti_di_mare","pollo","peperone","piselli","pomodoro","aglio"],["riso"],["estate"],[],"Riso allo zafferano con frutti di mare e carne, dalla crosta croccante (socarrat)."),
 ("gazpacho","Gazpacho","Spagnola","Spagna","zuppa",["pomodoro","cetriolo","peperone","aglio","oliva"],["pane","aceto"],["estate"],[],"Zuppa fredda di pomodoro e verdure crude, rinfrescante d'estate."),
 ("tortilla_espanola","Tortilla española","Spagnola","Spagna","secondo",["patata","uovo","cipolla"],[],[],[],"Frittata densa di patate e cipolla, da tapas o piatto unico."),
 ("moussaka","Moussaka","Greca","Grecia","secondo",["melanzana","agnello","pomodoro","cipolla","cannella","noce_moscata"],["besciamella"],[],[],"Sformato di melanzane e agnello con besciamella speziata."),
 ("greek_salad","Insalata greca","Greca","Grecia","insalata",["pomodoro","cetriolo","cipolla","oliva","formaggio_fresco"],["feta","origano"],["estate"],[],"Pomodori, cetrioli e olive con feta e origano."),
 ("ratatouille","Ratatouille","Francese","Francia","contorno",["melanzana","peperone","pomodoro","cipolla","aglio","basilico"],["zucchine","timo"],["estate"],[],"Stufato provenzale di ortaggi estivi."),
 ("bouillabaisse","Bouillabaisse","Francese","Francia","zuppa",["pesce_bianco","frutti_di_mare","pomodoro","zafferano","aglio","oliva"],["finocchio","rouille"],[],[],"Zuppa di pesce provenzale allo zafferano, servita con la rouille all'aglio."),
 ("coq_au_vin","Coq au vin","Francese","Francia","secondo",["pollo","funghi","bacon","cipolla"],["vino rosso"],["autunno","inverno"],[],"Pollo brasato nel vino rosso con funghi e pancetta."),
 ("crepes","Crêpes","Francese","Francia","dolce",["uovo","cioccolato","banana"],["farina","burro"],[],["candelora"],"Cialde sottili dolci; tradizionali alla Chandeleur (Candelora)."),
 ("caponata","Caponata","Siciliana","Italia","contorno",["melanzana","pomodoro","cappero","oliva","sedano","cipolla"],["aceto","zucchero","pinoli"],["estate"],["ferragosto"],"Agrodolce siciliano di melanzane con capperi e olive."),
 ("pasta_alla_norma","Pasta alla Norma","Siciliana","Italia","primo",["melanzana","pomodoro","basilico","formaggio_stagionato"],["pasta"],["estate"],[],"Pasta con melanzane fritte, pomodoro, basilico e ricotta salata."),
 ("pesto_genovese","Pesto alla genovese","Ligure","Italia","salsa",["basilico","aglio","formaggio_stagionato","oliva"],["pinoli","pasta"],["estate"],[],"Salsa cruda di basilico, pinoli, aglio e formaggio con olio d'oliva."),
 ("risotto_milanese","Risotto alla milanese","Lombarda","Italia","primo",["zafferano","cipolla","formaggio_stagionato"],["riso","burro","brodo"],[],[],"Risotto cremoso allo zafferano, dorato e avvolgente."),
 ("carbonara","Carbonara","Romana","Italia","primo",["uovo","bacon","formaggio_stagionato"],["pasta","pepe nero"],[],[],"Pasta mantecata con uovo, guanciale e pecorino."),
 ("caprese","Caprese","Campana","Italia","antipasto",["pomodoro","basilico","formaggio_fresco","oliva"],["mozzarella"],["estate"],[],"Pomodoro e mozzarella con basilico e olio."),
 ("panettone","Panettone","Lombarda","Italia","dolce",["uva","arancia","vaniglia","uovo"],["farina","burro","canditi"],["inverno"],["natale"],"Lievitato natalizio con uvetta e canditi d'arancia."),
 ("cassata_siciliana","Cassata siciliana","Siciliana","Italia","dolce",["formaggio_fresco","cioccolato","arancia","mandorla","vaniglia"],["ricotta","pan di spagna","pistacchio"],[],["pasqua"],"Dolce di ricotta zuccherata con marzapane, canditi e cioccolato."),
 ("colomba","Colomba","Italiana","Italia","dolce",["arancia","mandorla","uovo","vaniglia"],["farina","burro"],["primavera"],["pasqua"],"Lievitato pasquale con canditi e glassa di mandorle."),
 ("turkey_roast","Tacchino arrosto","Americana","USA","secondo",["salvia","timo","rosmarino","cipolla"],["tacchino","ripieno di pane"],["autunno","inverno"],["thanksgiving","natale"],"Tacchino arrosto con erbe, piatto-simbolo delle feste."),
 ("pumpkin_pie","Pumpkin pie","Americana","USA","dolce",["zucca","cannella","zenzero","chiodi_di_garofano","noce_moscata","uovo"],["pasta brisée","panna"],["autunno"],["thanksgiving"],"Crostata di zucca speziata, dolce autunnale delle feste."),
 ("latkes","Latkes","Ebraica","Israele","contorno",["patata","cipolla","uovo"],["farina"],[],["hanukkah"],"Frittelle di patata fritte, tradizionali di Hanukkah."),
 ("mince_pie","Mince pie","Britannica","Regno Unito","dolce",["mela","uva","arancia","cannella","noce_moscata"],["frutta secca","sugna"],["inverno"],["natale"],"Tortine natalizie ripiene di frutta speziata."),
 ("pho","Phở","Vietnamita","Vietnam","zuppa",["manzo","zenzero","cipolla","anice","cannella","lime","foglie_di_coriandolo","basilico"],["noodles di riso","anice stellato"],[],[],"Zuppa di noodles in brodo di manzo profumato ad anice stellato e cannella."),
 ("kimchi","Kimchi","Coreana","Corea","contorno",["cavolo","aglio","zenzero","peperoncino_piccante","cipolla"],["salsa di pesce"],[],[],"Cavolo fermentato piccante, base della tavola coreana."),
 ("bibimbap","Bibimbap","Coreana","Corea","secondo",["uovo","manzo","carota","aglio"],["riso","spinaci","gochujang"],[],[],"Ciotola di riso con verdure, manzo e uovo, condita col gochujang."),
 ("tagine","Tagine d'agnello","Marocchina","Marocco","secondo",["agnello","albicocca","cannella","cumino","zafferano","mandorla","cipolla"],["cuscus"],[],["eid"],"Stufato dolce-speziato di agnello con frutta secca."),
 ("shakshuka","Shakshuka","Mediorientale","Israele","secondo",["uovo","pomodoro","peperone","cipolla","aglio","cumino","peperoncino_piccante"],[],[],[],"Uova in camicia nel sugo speziato di pomodoro e peperoni."),
 ("feijoada","Feijoada","Brasiliana","Brasile","secondo",["maiale","bacon","cipolla","aglio"],["fagioli neri","riso","manioca"],[],[],"Stufato di fagioli neri e maiale, piatto nazionale brasiliano."),
 ("baklava","Baklava","Turca","Turchia","dolce",["noce","mandorla","cannella"],["pasta fillo","miele","pistacchio"],[],["eid"],"Sfoglie sottili con frutta secca e sciroppo di miele."),
 ("jiaozi","Jiaozi","Cinese","Cina","secondo",["maiale","cavolo","zenzero","aglio","cipolla"],["pasta","salsa di soia"],[],["capodanno_cinese"],"Ravioli ripieni, mangiati per il Capodanno cinese (portano fortuna)."),
 ("stinco_crauti","Stinco e crauti","Tedesca","Germania","secondo",["maiale","cavolo","ginepro","cipolla"],["crauti","senape"],["autunno"],["oktoberfest"],"Stinco di maiale con crauti al ginepro, classico dell'Oktoberfest."),
 ("fonduta_cioccolato","Fonduta di cioccolato","Internazionale","—","dolce",["cioccolato","fragola","banana"],["panna"],[],["san_valentino"],"Cioccolato fuso per intingere frutta; dolce conviviale e romantico."),
 ("lenticchie_cotechino","Cotechino e lenticchie","Italiana","Italia","secondo",["maiale","cipolla","sedano","carota"],["lenticchie","cotechino"],["inverno"],["capodanno"],"Lenticchie con cotechino a Capodanno: le lenticchie augurano prosperità."),
 # --- espansione (Fase 5, più dati) ---
 ("arancini","Arancini","Siciliana","Italia","street food",["zafferano","formaggio_stagionato","piselli","manzo","pomodoro"],["riso"],[],[],"Palle di riso allo zafferano fritte, ripiene di ragù o burro; icona dello street food siciliano."),
 ("parmigiana","Parmigiana di melanzane","Siciliana","Italia","secondo",["melanzana","pomodoro","formaggio_fresco","formaggio_stagionato","basilico"],[],["estate"],[],"Melanzane fritte stratificate con pomodoro, mozzarella e basilico, gratinate al forno."),
 ("pesce_spada_ghiotta","Pesce spada alla ghiotta","Siciliana","Italia","secondo",["pesce_grasso","pomodoro","oliva","cappero","sedano","cipolla"],[],["estate"],[],"Pesce spada in umido agrodolce alla messinese, con olive, capperi e sedano."),
 ("pasta_con_le_sarde","Pasta con le sarde","Siciliana","Italia","primo",["pesce_grasso","anice","uva","zafferano"],["pasta","finocchietto","pinoli"],["primavera"],[],"Pasta con sarde, finocchietto selvatico, uvetta e pinoli: dolce-salato palermitano."),
 ("cannoli","Cannoli","Siciliana","Italia","dolce",["formaggio_fresco","cioccolato","arancia"],["ricotta","pistacchio","cialda"],[],["carnevale"],"Cialde croccanti ripiene di ricotta dolce, gocce di cioccolato e canditi."),
 ("granita","Granita","Siciliana","Italia","dolce",["limone","mandorla","caffe"],["zucchero"],["estate"],[],"Ghiaccio tritato aromatizzato (limone, mandorla, caffè) servito con brioche; colazione messinese."),
 ("cacciucco","Cacciucco","Toscana","Italia","zuppa",["pesce_bianco","frutti_di_mare","pomodoro","aglio","peperoncino_piccante"],["pane","vino rosso"],[],[],"Zuppa di pesce livornese, ricca e piccante, servita sul pane abbrustolito."),
 ("ossobuco","Ossobuco","Lombarda","Italia","secondo",["manzo","carota","sedano","cipolla","limone","prezzemolo","aglio"],["vino bianco"],[],[],"Stinco di vitello brasato con gremolata di limone, aglio e prezzemolo."),
 ("vitello_tonnato","Vitello tonnato","Piemontese","Italia","antipasto",["manzo","pesce_grasso","acciuga","cappero","uovo"],[],["estate"],[],"Fettine di vitello fredde con salsa cremosa di tonno, acciughe e capperi."),
 ("saltimbocca","Saltimbocca","Romana","Italia","secondo",["manzo","prosciutto_crudo","salvia"],["vino bianco"],[],[],"Scaloppine di vitello con prosciutto e salvia, saltate in padella."),
 ("tiramisu","Tiramisù","Italiana","Italia","dolce",["caffe","cioccolato","uovo","formaggio_fresco","vaniglia"],["savoiardi","mascarpone"],[],[],"Savoiardi inzuppati nel caffè, crema al mascarpone e cacao."),
 ("panzanella","Panzanella","Toscana","Italia","insalata",["pomodoro","cetriolo","cipolla","basilico","oliva"],["pane"],["estate"],[],"Insalata di pane raffermo e pomodori, estiva e rinfrescante."),
 ("risotto_funghi","Risotto ai funghi","Italiana","Italia","primo",["funghi","cipolla","formaggio_stagionato","prezzemolo"],["riso","brodo"],["autunno"],[],"Risotto cremoso ai funghi, autunnale e avvolgente."),
 ("bagna_cauda","Bagna càuda","Piemontese","Italia","antipasto",["aglio","acciuga","oliva"],["verdure crude"],["inverno"],[],"Salsa calda di aglio e acciughe in olio, per intingere le verdure."),
 ("quiche_lorraine","Quiche lorraine","Francese","Francia","secondo",["uovo","bacon","formaggio_stagionato","cipolla"],["pasta brisée","panna"],[],[],"Torta salata con pancetta, uova e panna."),
 ("soupe_oignon","Soupe à l'oignon","Francese","Francia","zuppa",["cipolla","formaggio_stagionato"],["pane","brodo","vino"],["inverno"],[],"Zuppa di cipolle caramellate gratinata col formaggio."),
 ("tarte_tatin","Tarte Tatin","Francese","Francia","dolce",["mela","vaniglia"],["caramello","pasta sfoglia"],["autunno"],[],"Torta di mele caramellate cotta capovolta."),
 ("nicoise","Salade niçoise","Francese","Francia","insalata",["pesce_grasso","uovo","oliva","pomodoro","acciuga"],["fagiolini"],["estate"],[],"Insalata provenzale con tonno, uova, olive e pomodori."),
 ("patatas_bravas","Patatas bravas","Spagnola","Spagna","antipasto",["patata","pomodoro","aglio","peperoncino_piccante"],["paprika"],[],[],"Patate fritte con salsa piccante di pomodoro, tapas classica."),
 ("pulpo_gallega","Pulpo a la gallega","Spagnola","Spagna","secondo",["frutti_di_mare","patata","peperoncino_piccante","oliva"],["paprika"],[],[],"Polpo con patate, olio e paprika affumicata."),
 ("bacalhau","Bacalhau à brás","Portoghese","Portogallo","secondo",["pesce_bianco","patata","uovo","oliva","cipolla","aglio"],[],[],[],"Baccalà sfilacciato con patate a fiammifero, uova e cipolla."),
 ("caldo_verde","Caldo verde","Portoghese","Portogallo","zuppa",["cavolo","patata","cipolla","aglio"],["chorizo"],["inverno"],[],"Zuppa di cavolo e patate con salsiccia affumicata."),
 ("shawarma","Shawarma","Mediorientale","Libano","street food",["pollo","aglio","cumino","limone"],["pane pita","salsa di yogurt"],[],[],"Carne speziata arrostita allo spiedo, servita nel pane con salse."),
 ("couscous_pesce","Cuscus di pesce","Siciliana","Italia","primo",["pesce_bianco","frutti_di_mare","pomodoro","cipolla","zafferano","prezzemolo"],["cuscus"],[],[],"Cuscus alla trapanese con brodo di pesce, eredità arabo-siciliana."),
 ("fattoush","Fattoush","Libanese","Libano","insalata",["cetriolo","pomodoro","cipolla","menta","prezzemolo"],["pane","sommacco"],["estate"],[],"Insalata libanese con pane tostato e sommacco."),
 ("kofta","Kofta","Mediorientale","Libano","secondo",["agnello","cumino","prezzemolo","cipolla","aglio"],[],[],[],"Polpette di agnello speziate, grigliate allo spiedo."),
 ("tom_yum","Tom yum","Thailandese","Thailandia","zuppa",["frutti_di_mare","lime","peperoncino_piccante","zenzero","funghi"],["citronella"],[],["songkran"],"Zuppa thai acida e piccante di gamberi profumata alla citronella."),
 ("som_tam","Som tam","Thailandese","Thailandia","insalata",["arachide","lime","peperoncino_piccante","aglio","pomodoro"],["papaya verde"],["estate"],[],"Insalata piccante di papaya verde pestata, con arachidi e lime."),
 ("mapo_tofu","Mapo tofu","Cinese","Cina","secondo",["maiale","peperoncino_piccante","aglio","zenzero","cipolla"],["tofu","doubanjiang"],[],[],"Tofu in salsa piccante del Sichuan con maiale macinato."),
 ("char_siu","Char siu","Cinese","Cina","secondo",["maiale","zenzero","aglio"],["miele","salsa hoisin"],[],[],"Maiale glassato e arrostito, dolce e laccato."),
 ("bulgogi","Bulgogi","Coreana","Corea","secondo",["manzo","aglio","zenzero","cipolla","pera"],["salsa di soia"],[],[],"Manzo marinato (anche con pera) e grigliato, dolce-salato."),
 ("tonkatsu","Tonkatsu","Giapponese","Giappone","secondo",["maiale","uovo","cavolo"],["panko"],[],[],"Cotoletta di maiale impanata nel panko e fritta."),
 ("nasi_goreng","Nasi goreng","Indonesiana","Indonesia","primo",["pollo","uovo","aglio","peperoncino_piccante","cipolla"],["riso","kecap manis"],[],[],"Riso saltato indonesiano con uovo e salsa di soia dolce."),
 ("rendang","Rendang","Indonesiana","Indonesia","secondo",["manzo","cocco","zenzero","aglio","peperoncino_piccante","cannella"],["citronella"],[],[],"Manzo brasato a lungo nel latte di cocco e spezie."),
 ("banh_mi","Bánh mì","Vietnamita","Vietnam","street food",["maiale","fegato","foglie_di_coriandolo","cetriolo","carota","peperoncino_piccante"],["baguette"],[],[],"Panino vietnamita con paté, maiale e verdure in agrodolce."),
 ("samosa","Samosa","Indiana","India","street food",["patata","piselli","cumino","zenzero","peperoncino_piccante"],["pasta"],[],["diwali","holi"],"Fagottini fritti ripieni di patate e piselli speziati."),
 ("tikka_masala","Chicken tikka masala","Indiana","India","secondo",["pollo","pomodoro","zenzero","aglio","cardamomo","cannella"],["panna"],[],["diwali","holi"],"Pollo marinato in salsa cremosa e speziata di pomodoro."),
 ("raita","Raita","Indiana","India","salsa",["cetriolo","menta","cumino"],["yogurt"],["estate"],[],"Salsa fresca di yogurt e cetriolo che smorza il piccante."),
 ("chili_con_carne","Chili con carne","Tex-Mex","USA","secondo",["manzo","pomodoro","peperoncino_piccante","cipolla","aglio","cumino"],["fagioli"],["inverno"],[],"Stufato piccante di manzo, pomodoro e fagioli."),
 ("clam_chowder","Clam chowder","Americana","USA","zuppa",["frutti_di_mare","patata","bacon","cipolla"],["panna"],[],[],"Zuppa cremosa di vongole e patate del New England."),
 ("key_lime_pie","Key lime pie","Americana","USA","dolce",["lime","uovo"],["latte condensato","biscotti"],["estate"],[],"Torta cremosa al lime della Florida."),
 ("moqueca","Moqueca","Brasiliana","Brasile","zuppa",["pesce_bianco","cocco","pomodoro","peperone","cipolla","aglio","foglie_di_coriandolo","lime"],["olio di palma"],[],[],"Stufato brasiliano di pesce al latte di cocco e lime."),
 ("empanadas","Empanadas","Argentina","Argentina","street food",["manzo","uovo","oliva","cipolla","cumino"],["pasta"],[],[],"Fagottini ripieni di carne speziata, uova e olive."),
 ("chimichurri","Chimichurri","Argentina","Argentina","salsa",["prezzemolo","aglio","oliva","peperoncino_piccante"],["aceto","origano"],[],[],"Salsa cruda di prezzemolo e aglio per la carne alla griglia."),
 ("borscht","Borscht","Russa","Russia","zuppa",["barbabietola","cavolo","patata","carota","cipolla"],["panna acida"],["inverno"],[],"Zuppa di barbabietola rosso rubino, servita con panna acida."),
 ("gravlax","Gravlax","Nordica","Svezia","antipasto",["pesce_grasso","aneto"],["sale","zucchero"],[],["midsummer"],"Salmone marinato a crudo con aneto, sale e zucchero."),
 ("fish_and_chips","Fish and chips","Britannica","Regno Unito","secondo",["pesce_bianco","patata"],["pastella","aceto"],[],[],"Pesce in pastella fritto con patatine, classico da pub."),
]

# (id, nome, quando, cultura, [piatti id], nota)
OCCASIONS = [
 ("cinco_de_mayo","Cinco de Mayo","5 maggio","Messico",["tacos_al_pastor","guacamole","mole_poblano"],"Festa messicana: street food, salse di avocado e mole."),
 ("dia_de_muertos","Día de Muertos","1–2 novembre","Messico",["mole_poblano"],"Giorno dei morti messicano; pan de muerto e mole sulle offrende."),
 ("natale","Natale","25 dicembre","Cristiana / internazionale",["panettone","turkey_roast","mince_pie"],"Pranzi e dolci delle feste invernali, molto variabili per paese."),
 ("pasqua","Pasqua","primavera","Cristiana",["cassata_siciliana","colomba"],"Agnello, dolci di ricotta e lievitati pasquali."),
 ("thanksgiving","Thanksgiving","4° giovedì di novembre","USA",["turkey_roast","pumpkin_pie"],"Ringraziamento americano: tacchino e dolci di zucca autunnali."),
 ("diwali","Diwali","autunno (ott–nov)","India",["butter_chicken","dal","biryani"],"Festa delle luci indiana: curry, riso speziato e dolci."),
 ("hanukkah","Hanukkah","dicembre","Ebraica",["latkes"],"Festa delle luci ebraica: cibi fritti come le latkes."),
 ("capodanno_cinese","Capodanno cinese","gen–feb","Cina",["jiaozi"],"Capodanno lunare: ravioli e cibi beneauguranti."),
 ("ferragosto","Ferragosto","15 agosto","Italia",["caponata","caprese"],"Pranzi estivi all'aperto, piatti freschi e di stagione."),
 ("eid","Eid","variabile (calendario lunare)","Islamica",["biryani","tagine","baklava"],"Banchetti di fine Ramadan: riso speziato, stufati e dolci."),
 ("san_valentino","San Valentino","14 febbraio","Internazionale",["fonduta_cioccolato"],"Cene romantiche: cioccolato e dolci."),
 ("capodanno","Capodanno","31 dic – 1 gen","Internazionale / Italia",["lenticchie_cotechino"],"Veglione e cibi portafortuna (lenticchie)."),
 ("candelora","Chandeleur (Candelora)","2 febbraio","Francia",["crepes"],"Giorno delle crêpes in Francia."),
 ("oktoberfest","Oktoberfest","set–ott","Germania",["stinco_crauti"],"Festa della birra bavarese: maiale, crauti, salumi."),
 ("carnevale","Carnevale","feb–mar","Internazionale",["crepes","cannoli"],"Dolci fritti e abbondanza prima della Quaresima."),
 ("halloween","Halloween","31 ottobre","USA / internazionale",["pumpkin_pie"],"Notte di zucche e dolci autunnali."),
 ("independencia_mexico","Independencia de México","16 settembre","Messico",["tacos_al_pastor","guacamole","mole_poblano"],"Festa dell'indipendenza messicana, con i piatti nazionali."),
 ("la_tomatina","La Tomatina","ultimo mercoledì d'agosto","Spagna",["gazpacho","paella"],"Battaglia dei pomodori a Buñol; estate spagnola."),
 ("holi","Holi","primavera (marzo)","India",["samosa","tikka_masala"],"Festa dei colori indiana, con street food e dolci."),
 ("songkran","Songkran","13–15 aprile","Thailandia",["pad_thai","tom_yum","green_curry"],"Capodanno thailandese, la festa dell'acqua."),
 ("midsummer","Midsummer","solstizio d'estate (giugno)","Svezia / Nordica",["gravlax"],"Festa di mezza estate scandinava, con pesce marinato."),
 ("hanami","Hanami","primavera (fioritura)","Giappone",["sushi"],"Contemplazione dei ciliegi in fiore, con picnic."),
]

# Abbinamenti ingrediente-ingrediente OLTRE il libro (a,b id; kind classico/insolito/neutro; nota).
# 'novel' (= non presente in Segnit) viene calcolato a runtime confrontando con archi.json.
PAIRINGS = [
 ("avocado","lime","classico","Il lime ravviva la grassezza dell'avocado: base del guacamole e dei poke."),
 ("avocado","mango","insolito","Due polpe cremose e dolci, tropicali, in insalate e cocktail."),
 ("avocado","pesce_grasso","classico","Salmone/tonno e avocado: il grasso buono di entrambi, da sushi e poke."),
 ("mango","peperoncino_piccante","insolito","Dolce tropicale e piccante: chutney, salse, frutta con chili e lime."),
 ("cocco","lime","classico","Latte di cocco e lime: spina dorsale acida-dolce della cucina del sud-est asiatico."),
 ("arancia","anice","classico","Agrume e finocchietto/anice: insalata siciliana di arance e finocchi."),
 ("pomodoro","anguria","insolito","Insalata estiva: dolcezza dell'anguria e acidità del pomodoro."),
 ("anguria","formaggio_fresco","insolito","Anguria e feta con menta: contrasto dolce-salato rinfrescante."),
 ("fragola","basilico","insolito","Fragole e basilico: erba aromatica che esalta il frutto, anche col pepe."),
 ("pesca","prosciutto_crudo","classico","Come il melone col prosciutto: dolcezza succosa contro sapidità."),
 ("zucca","salvia","classico","Zucca e burro e salvia: ripieni e risotti autunnali."),
 ("zucca","mandorla","regionale","Tortelli di zucca con amaretti: dolce-amaro mantovano."),
 ("patata","rosmarino","classico","Patate arrosto al rosmarino: l'erba resinosa profuma l'amido."),
 ("agnello","menta","classico","Agnello con salsa alla menta: freschezza che taglia il grasso (tradizione inglese)."),
 ("maiale","mela","classico","Maiale e mela/sidro: l'acidità dolce sgrassa la carne."),
 ("manzo","rafano","classico","Roast beef e rafano: il piccante pulisce la bocca dalla carne grassa."),
 ("frutti_di_mare","avocado","classico","Gamberi e avocado: cocktail e insalate cremose."),
 ("carota","zenzero","classico","Carota e zenzero: vellutate e centrifughe, dolce e pungente."),
 ("barbabietola","formaggio_di_capra","classico","Barbabietola e caprino: terra dolce contro acidità lattica."),
 ("fico","prosciutto_crudo","classico","Fichi e prosciutto: dolce maturo e salato, fine estate."),
 ("fico","formaggio_erborinato","classico","Fico e gorgonzola: dolcezza che doma il piccante del blu."),
 ("pera","formaggio_erborinato","classico","Pera e gorgonzola: abbinamento da fine pasto."),
 ("uva","formaggio_stagionato","classico","Uva e pecorino: 'al contadino non far sapere...'."),
 ("noce","formaggio_erborinato","classico","Noci e blu: croccante e cremoso, amaro e piccante."),
 ("cioccolato","lampone","classico","Cioccolato e lampone: acidità che alleggerisce il cacao."),
 ("caffe","cardamomo","regionale","Caffè al cardamomo: l'aroma agrumato-balsamico del Medio Oriente."),
 ("pesce_grasso","lime","classico","Lime su salmone/tonno crudo: ceviche, tartare, crudi."),
 ("pollo","mango","insolito","Pollo e mango: curry e insalate dolci-speziate."),
 ("cetriolo","menta","classico","Cetriolo e menta: tzatziki, raita, acque aromatizzate."),
 ("melanzana","menta","regionale","Melanzane e menta: fritto agrodolce alla siciliana e mediorientale."),
]

# Abbinamento vino per ingrediente (id -> (vino, stile, nota)). Per gli altri 99 l'app
# usa un fallback per tipologia. Conoscenza enologica generale, _source:"ai", DA VALIDARE.
WINE = {
 "ostrica": ("Champagne / Chablis","bollicine o bianco secco minerale","Bollicine e mineralità esaltano lo iodio."),
 "frutti_di_mare": ("Vermentino / Falanghina","bianco secco e sapido","Freschezza e sapidità per i frutti di mare."),
 "pesce_bianco": ("Fiano / Soave","bianco secco delicato","Per pesci magri e bianchi."),
 "pesce_grasso": ("Etna Bianco / Riesling","bianco strutturato e acido","L'acidità sgrassa tonno e salmone."),
 "acciuga": ("Vermentino","bianco sapido","Sapidità su sapidità, in equilibrio."),
 "manzo": ("Barolo / Cabernet","rosso corposo e tannico","Tannino e struttura per la carne rossa."),
 "agnello": ("Nero d'Avola / Syrah","rosso caldo e speziato","Rosso generoso per l'agnello."),
 "maiale": ("Pinot Nero / Lambrusco","rosso medio o frizzante","Acidità che pulisce il grasso."),
 "pollo": ("Chardonnay / Pinot Nero","bianco strutturato o rosso leggero","Versatile secondo la ricetta."),
 "fegato": ("Sauternes / passito","bianco dolce","Il dolce contrasta l'amaro (foie gras)."),
 "prosciutto_crudo": ("Franciacorta / Prosecco","bollicine","Bollicine per i salumi."),
 "formaggio_stagionato": ("Rosso strutturato / passito","rosso importante o dolce","Stagionati amano rossi o vini dolci."),
 "formaggio_erborinato": ("Passito / Porto","bianco/rosso dolce","Il dolce bilancia il piccante del blu."),
 "formaggio_di_capra": ("Sauvignon Blanc","bianco aromatico ed erbaceo","Freschezza per il caprino."),
 "cioccolato": ("Passito / Banyuls / Recioto","rosso dolce e potente","Vini dolci reggono il cacao."),
 "tartufo": ("Barolo / Nebbiolo","rosso elegante","Eleganza per l'aroma del tartufo."),
 "funghi": ("Pinot Nero","rosso terroso","Note terrose in sintonia."),
 "oliva": ("Sherry fino / bianco sapido","secco e salino","Sapidità e note ossidative."),
 "pomodoro": ("Rosato / rosso giovane","rosato o rosso fresco","L'acidità chiede vini freschi."),
 "fragola": ("Spumante rosé / Moscato","dolce o bollicine","Frutto rosso e bollicine dolci."),
 "mela": ("Sidro / Riesling","sidro o bianco","Sidro naturale per la mela."),
 "uovo": ("Bollicine / bianco fresco","secco","Vini freschi per i piatti d'uovo."),
}


def main():
    ings = json.load(open(os.path.join(OUT, "ingredienti.json"), encoding="utf-8"))
    ids = {g["id"] for g in ings}
    dish_ids = {d[0] for d in DISHES}
    occ_ids = {o[0] for o in OCCASIONS}

    errors = []
    for d in DISHES:
        for ing in d[5]:
            if ing not in ids:
                errors.append(f"piatto {d[0]}: ingrediente inesistente '{ing}'")
        for oc in d[8]:
            if oc not in occ_ids:
                errors.append(f"piatto {d[0]}: occasione inesistente '{oc}'")
    for o in OCCASIONS:
        for dn in o[4]:
            if dn not in dish_ids:
                errors.append(f"occasione {o[0]}: piatto inesistente '{dn}'")
    for p in PAIRINGS:
        if p[0] not in ids: errors.append(f"pairing: ingrediente inesistente '{p[0]}'")
        if p[1] not in ids: errors.append(f"pairing: ingrediente inesistente '{p[1]}'")
    for k in WINE:
        if k not in ids: errors.append(f"wine: ingrediente inesistente '{k}'")
    if errors:
        print("!! VALIDAZIONE FALLITA")
        for e in errors:
            print("  ", e)
        sys.exit(1)

    dishes = [{
        "id": d[0], "name": d[1], "cuisine": d[2], "country": d[3], "category": d[4],
        "ingredients": d[5], "extra": d[6], "seasons": d[7], "occasions": d[8],
        "note": d[9], "source": "", "_source": "ai",
    } for d in DISHES]
    occasions = [{
        "id": o[0], "name": o[1], "when": o[2], "culture": o[3],
        "dishes": o[4], "note": o[5], "source": "", "_source": "ai",
    } for o in OCCASIONS]

    # archi del libro per marcare gli abbinamenti 'novel' (non presenti in Segnit)
    book_pairs = set()
    archi_path = os.path.join(OUT, "archi.json")
    if os.path.exists(archi_path):
        for e in json.load(open(archi_path, encoding="utf-8")):
            book_pairs.add("|".join(sorted((e["a"], e["b"]))))
    pairings = [{
        "a": p[0], "b": p[1], "kind": p[2], "note": p[3],
        "novel": "|".join(sorted((p[0], p[1]))) not in book_pairs,
        "_source": "ai",
    } for p in PAIRINGS]
    wine = {k: {"wine": v[0], "style": v[1], "note": v[2], "_source": "ai"} for k, v in WINE.items()}

    obj = {
        "_meta": {
            "policy": "Layer NON dal libro: piatti, occasioni, abbinamenti extra e vino da conoscenza generale, internazionali, collegati ai 99 ingredienti. _source:'ai', DA VALIDARE; citazioni a fonti autorevoli da aggiungere (modello ibrido).",
        },
        "dishes": dishes,
        "occasions": occasions,
        "pairings": pairings,
        "wine": wine,
    }
    json.dump(obj, open(os.path.join(OUT, "ext.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    from collections import Counter
    print(f"OK - {len(dishes)} piatti, {len(occasions)} occasioni; tutti i link validi.")
    print("Cucine:", dict(Counter(d['cuisine'] for d in dishes)))
    linked = sum(len(d["ingredients"]) for d in dishes)
    print(f"Collegamenti piatto→ingrediente: {linked}")
    print(f"Abbinamenti extra: {len(pairings)} (di cui novel/non nel libro: {sum(1 for p in pairings if p['novel'])}) · vino: {len(wine)} ingredienti")
    print("Scritto:", os.path.join(OUT, "ext.json"))


if __name__ == "__main__":
    main()
