#!/usr/bin/env python3
"""Fabrique les données d'un palier d'exemple : un assistant (inventé) pour la « Médiathèque de Valbourg ».

Palier 1 : deux commandes, `ouvrir_prets` (ouvre la page des prêts) et `prolonger_pret` (prolonge un prêt de N jours).
Quatre niveaux (le champ `critere`, du plus évident au plus piégeux) :
  evident  la phrase directe                                          -> executer
  forme    la même demande, familière, abrégée ou avec fautes         -> executer
  proche   une demande d'un palier à venir ou destructive             -> proposer (ne pas agir)
  rien     une phrase qui ne demande rien à l'assistant               -> rien
L'entraînement et la part tenue à part (examen du moteur) sortent des mêmes modèles de phrases avec des tirages
différents et ne partagent jamais une phrase. Déterministe : même graine, mêmes fichiers.
Ce n'est PAS le test du palier : celui-là est fait de consignes réelles, dites par un utilisateur dans le vrai outil.
"""
import json
import os
import random

GRAINE = 20261026
JOURS = [3, 5, 7, 10, 14, 15, 21]
EVIDENT_PRETS = ["ouvre mes prêts", "affiche mes prêts", "montre mes prêts en cours", "va sur la page des prêts",
                 "je veux voir mes prêts", "ouvre la liste de mes emprunts"]
EVIDENT_PROLONGER = ["prolonge mon prêt de {j} jours", "prolonge le livre de {j} jours", "rallonge mon emprunt de {j} jours",
                     "je voudrais garder mon livre {j} jours de plus", "ajoute {j} jours à mon prêt"]
FORME_PRETS = ["mes prets stp", "ouvre mes pret", "kes j'ai emprunté ?", "mes emprunts svp", "dis-moi ce que j'ai emprunté",
               "liste prets", "ou en sont mes emprunts"]
FORME_PROLONGER = ["rallonge de {j}j", "prolonge {j} j stp", "+{j} jours sur mon pret", "garde le bouquin {j} jours de plus",
                   "peux tu prolonger de {j} jours mon emprunt", "decale le retour de {j} jours"]
# demandes d'un palier à venir ou destructives : un verbe + un objet (certains objets contiennent « mes prêts »,
# le piège : l'assistant ne doit pas les prendre pour « ouvre mes prêts »)
VERBES_PROCHES = ["supprime", "efface", "annule", "réserve", "renouvelle", "inscris-moi à", "transfère", "paye"]
OBJETS_PROCHES = ["tous mes prêts", "mon historique d'emprunts", "ma réservation", "mon compte", "ma carte d'abonnée",
                  "le dernier roman de la rentrée", "l'atelier lecture", "mon amende"]
PROCHE = [f"{v} {o}" for v in VERBES_PROCHES for o in OBJETS_PROCHES] + [
    "ouvre les nouveautés", "affiche les nouveautés de la semaine", "montre-moi les nouveautés jeunesse",
    "ouvre l'agenda des animations", "ouvre le catalogue des bandes dessinées", "prolonge tout, sans limite"]
RIEN = ["il fait beau aujourd'hui", "merci beaucoup", "j'adore cette bibliothèque", "bonne journée", "à tout à l'heure",
        "c'est bizarre ce bruit", "quelle heure est-il", "ok", "je réfléchis", "mon voisin lit beaucoup",
        "le café est froid", "super, merci", "j'ai oublié mes lunettes", "il y a du monde ce matin",
        "ce roman m'a bien plu", "à demain", "tiens, il pleut", "c'est calme ici", "je reviens plus tard",
        "ma fille adore les contes", "quel beau bâtiment", "d'accord"]
SUFFIXES = ["", "", " s'il te plaît", " merci", " rapidement"]


def cas(rng, critere, texte, attendu):
    return {"critere": critere, "entree": {"texte": texte}, "corrige": attendu}


def population():
    """Toutes les phrases possibles, par niveau : [(texte, attendu)]."""
    pop = {"evident": [], "forme": [], "proche": [], "rien": []}
    for s in SUFFIXES[1:] + [""]:
        for m in EVIDENT_PRETS:
            pop["evident"].append((m + s, {"action": "executer", "commande": "ouvrir_prets", "args": {}}))
        for m in EVIDENT_PROLONGER:
            for j in JOURS:
                pop["evident"].append((m.format(j=j) + s, {"action": "executer", "commande": "prolonger_pret", "args": {"jours": j}}))
        for m in RIEN:
            pop["rien"].append((m + s, {"action": "rien", "commande": None, "args": None}))
    for m in FORME_PRETS:
        pop["forme"].append((m, {"action": "executer", "commande": "ouvrir_prets", "args": {}}))
    for m in FORME_PROLONGER:
        for j in JOURS:
            pop["forme"].append((m.format(j=j), {"action": "executer", "commande": "prolonger_pret", "args": {"jours": j}}))
    for m in PROCHE:
        pop["proche"].append((m, {"action": "proposer", "commande": None, "args": None}))
    for k in pop:   # sans doublon, dans un ordre stable
        pop[k] = list(dict(pop[k]).items())
    return pop


def tirer(rng, pop, deja, nombres):
    out = []
    for critere, n in nombres.items():
        libres = [(t, a) for t, a in pop[critere] if t not in deja]
        for t, a in rng.sample(libres, n):
            deja.add(t)
            out.append(cas(rng, critere, t, a))
    rng.shuffle(out)
    return out


def ecrire(chemin, lignes, prefixe):
    with open(chemin, "w", encoding="utf-8") as f:
        for i, c in enumerate(lignes, 1):
            c = {"id": f"{prefixe}-{i:03d}", **c}
            f.write(json.dumps(c, ensure_ascii=False, sort_keys=True) + "\n")


def main():
    ici = os.path.dirname(os.path.abspath(__file__))
    rng = random.Random(GRAINE)
    pop, deja = population(), set()
    ecrire(os.path.join(ici, "donnees", "entrainement.jsonl"), tirer(rng, pop, deja, {"evident": 14, "forme": 16, "proche": 22, "rien": 10}), "ent")
    ecrire(os.path.join(ici, "donnees", "examen.jsonl"), tirer(rng, pop, deja, {"evident": 10, "forme": 10, "proche": 20, "rien": 8}), "exa")
    print("donnees/entrainement.jsonl (62) et donnees/examen.jsonl (48) écrits")


if __name__ == "__main__":
    main()
