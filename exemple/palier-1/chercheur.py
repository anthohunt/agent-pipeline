#!/usr/bin/env python3
"""Un chercheur écrit à la main (sans modèle d'IA) : il lit les fautes de la version parente sur l'entraînement et
ajoute une règle au harnais enfant (BOUCLE_SORTIE/regles.json). Un vrai run remplace cette commande par un agent
(Claude Code, par exemple) qui lit les mêmes entrées et modifie le même dossier.

Familles d'idées : ouvrir (mots qui ouvrent les prêts), prolonger (mots qui prolongent), proposer (demandes à ne pas
exécuter). Le i-ième enfant d'un tour prend la i-ième famille, en sautant celles qui sont en impasse (BOUCLE_IMPASSE).
"""
import json
import os
import re
import unicodedata
from collections import Counter

FAMILLES = ["ouvrir", "prolonger", "proposer"]
CLE = {"ouvrir": "ouvrir_prets", "prolonger": "prolonger_pret", "proposer": "proposer"}
INUTILES = set("pour mes mon une des les ces cette tout avec sans plus dans fait vous nous dis moi toi tes ses sur".split())


def plat(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def mots(texte):
    return [m for m in re.findall(r"[a-z+']{3,}", plat(texte)) if m not in INUTILES and not m.isdigit()]


def candidats(famille, fautes, regles):
    attendu_cmd = CLE[famille]
    pour, contre = Counter(), set()
    for f in fautes:
        corrige = f["corrige"]
        vise = (corrige.get("commande") == attendu_cmd) if famille != "proposer" else corrige.get("action") == "proposer"
        propose = f["proposition"] or {}
        if vise and propose.get("action") != corrige.get("action") or (vise and propose.get("commande") != corrige.get("commande")):
            ms = mots(f["entree"]["texte"])
            pour.update(set(ms))
            if ms:
                pour[ms[0]] += 2          # le premier mot d'une consigne est souvent son verbe : le mieux placé pour généraliser
        elif not vise:
            contre.update(mots(f["entree"]["texte"]))
    deja = [plat(e) for e in regles[attendu_cmd]]
    return [m for m, _ in pour.most_common() if m not in contre and not any(m in d or d in m for d in deja)]


def main():
    sortie = os.environ["BOUCLE_SORTIE"]
    index = int(os.environ.get("BOUCLE_INDEX", "0"))
    impasse = [x for x in os.environ.get("BOUCLE_IMPASSE", "").split(",") if x]
    with open(os.environ["BOUCLE_FAUTES"], encoding="utf-8") as f:
        fautes = json.load(f)
    chemin = os.path.join(sortie, "regles.json")
    with open(chemin, encoding="utf-8") as f:
        regles = json.load(f)
    for k in range(len(FAMILLES)):
        famille = FAMILLES[(index + k) % len(FAMILLES)]
        if famille in impasse:
            continue
        propositions = candidats(famille, fautes, regles)
        if not propositions:
            continue
        ajout = propositions[:3] if famille == "proposer" else propositions[:2]
        regles[CLE[famille]] = regles[CLE[famille]] + ajout
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(regles, f, indent=2, ensure_ascii=False)
        with open(os.path.join(sortie, "noeud.json"), "w", encoding="utf-8") as f:
            json.dump({"famille": famille, "idee": f"ajouter {ajout} à {CLE[famille]}"}, f, ensure_ascii=False)
        return
    with open(os.path.join(sortie, "noeud.json"), "w", encoding="utf-8") as f:
        json.dump({"famille": "aucune-idee", "idee": "rien à essayer"}, f)


if __name__ == "__main__":
    main()
