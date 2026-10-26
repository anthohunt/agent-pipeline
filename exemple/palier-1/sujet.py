#!/usr/bin/env python3
"""Le sujet de l'exemple : un interpréteur de consignes à base de règles, piloté par un harnais.

Entrée : {"harnais": "<dossier>", "entree": {"texte": "..."}}      (avec --lot : un objet par ligne, plus "id")
Sortie : {"action": "executer"|"proposer"|"rien", "commande": "<id>"|null, "args": {...}|null}
         (avec --lot : {"id", "proposition"} par ligne)

Le harnais est un fichier, regles.json : pour chaque commande, des mots ou expressions qui la déclenchent ;
`proposer` : expressions qui demandent quelque chose que l'assistant ne sait pas encore faire (ou de destructif) ;
`jours_defaut` : durée d'une prolongation quand la phrase n'en donne pas.
Un vrai agent remplacerait ce programme par un petit modèle ; le moteur, le juge et le chercheur ne changent pas.
"""
import json
import re
import sys
import unicodedata


def plat(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def contient(texte, expressions):
    return any(plat(e) in texte for e in expressions)


def interpreter(texte, regles):
    t = plat(texte)
    if contient(t, regles.get("proposer", [])):
        return {"action": "proposer", "commande": None, "args": None}
    if contient(t, regles.get("prolonger_pret", [])):
        m = re.search(r"(\d+)\s*(?:jours?|j\b)", t)
        return {"action": "executer", "commande": "prolonger_pret",
                "args": {"jours": int(m.group(1)) if m else regles.get("jours_defaut", 7)}}
    if contient(t, regles.get("ouvrir_prets", [])):
        return {"action": "executer", "commande": "ouvrir_prets", "args": {}}
    return {"action": "rien", "commande": None, "args": None}


def un_cas(demande):
    with open(demande["harnais"].rstrip("/") + "/regles.json", encoding="utf-8") as f:
        regles = json.load(f)
    return interpreter(demande["entree"]["texte"], regles)


if __name__ == "__main__":
    if "--lot" in sys.argv:
        for ligne in sys.stdin:
            if ligne.strip():
                d = json.loads(ligne)
                print(json.dumps({"id": d["id"], "proposition": un_cas(d)}, ensure_ascii=False))
    else:
        print(json.dumps(un_cas(json.load(sys.stdin)), ensure_ascii=False))
