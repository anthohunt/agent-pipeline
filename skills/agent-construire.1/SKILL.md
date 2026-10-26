---
name: agent-construire.1
description: Le constructeur de la pipeline agent — écrit les données d'UN palier (phrases évidentes puis situations complexes, bonne réponse fixée par le catalogue ou l'outil réel), recopie son test des consignes réelles, entraîne l'agent du palier avec le moteur de La boucle (dépôt `la-boucle-engine` : moteur, juge, harnais) dans la limite de la machine. Sous-skill de agent-construire ; ne vérifie jamais son propre travail.
---

# Agent — le constructeur d'un palier

Tu reçois du chef : le numéro du palier, ses commandes et les `id` de son test, les chemins de
`besoin.md`, `reponses.json`, `acces-outil.json`, `catalogue.json`, `consignes-reelles.jsonl`
(sous `docs/agent/`), et parfois la liste des écarts du dernier vérificateur. Tu rends les
fichiers ci-dessous et un compte rendu au journal du palier. **Tu ne vérifies pas** : un autre
agent rejouera le test dans le vrai outil.

## 1. Le test → `docs/agent/paliers/p<N>/test.jsonl`

Recopier, ligne pour ligne, les consignes réelles dont les `id` sont dans le test du palier
(`paliers.json`). Mêmes `id`, même `texte`, même `attendu`. Rien d'autre : ni reformulation, ni
phrase ajoutée. Le test ne change pas pendant le palier.

## 2. Les données → `docs/agent/paliers/p<N>/donnees/entrainement.jsonl`

- **Les commandes du palier seules** — plus des exemples « proposer » et « rien » proches, pour
  que l'agent apprenne aussi à ne pas agir.
- **Des plus évidentes aux plus complexes** : d'abord la phrase directe (« ouvre le fichier »),
  puis le contexte qui change (autre écran, sélection, mémoire), la forme qui change (familier,
  fautes, abrégé), les cas proches qu'il ne faut pas confondre.
- **La bonne réponse est fixée par le catalogue ou par l'outil réel**, jamais par celui qui écrit
  la phrase.
- **Aucune phrase du test**, ni recopiée ni à un mot près.
- **Chaque lot est relu sur un échantillon avant de servir** (une dizaine tirées au hasard :
  phrase naturelle ? étiquette juste ?) ; le résultat de la relecture s'écrit au journal. Une
  donnée mauvaise de base fait un agent mauvais quel que soit l'entraînement.
- Les consignes réelles hors test peuvent servir de graines, jamais celles du test.

La quantité n'est pas fixée d'avance : on commence petit, on mesure, on ajoute là où l'agent se
trompe.

## 3. L'entraînement

L'agent = un petit modèle (ou un simple programme) + son harnais (consignes, règles, programme autour). On l'entraîne
avec le **moteur de La boucle**, dépôt séparé du même auteur : `la-boucle-engine`, commande publique
`python3 -m boucle …` (Python ≥ 3.10, bibliothèque standard seule ; installation :
`pip install git+https://github.com/anthohunt/la-boucle-engine`, ou `PYTHONPATH=$BOUCLE_HOME`). Cette pipeline ne le
recopie pas : sans lui, l'étape « construire » s'arrête ici.

On en prend la petite boucle : mesurer, lire les fautes, essayer une idée, garder ce qui monte, jeter ce qui baisse.
Un **chantier** par palier, dans `docs/agent/paliers/p<N>/chantier/` :

- `donnees/entrainement.jsonl` : les données du palier (§ 2), une ligne `{"id","critere","entree","corrige"}` ; `critere` =
  le niveau (évident, contexte, forme, cas proche), `entree` = `{"texte","contexte"}`, `corrige` = `{"action","commande","args"}`
  fixé par le catalogue ou l'outil réel.
- `donnees/examen.jsonl` : **une part tenue à part de ces mêmes données** (une phrase sur cinq, tirée au hasard, jamais
  une phrase du test du palier). Le moteur exige un banc d'examen ; c'est celui-ci. Il ne sert qu'au juge du moteur :
  le chercheur ne le voit jamais. `python3 -m boucle sceller` sur les deux bancs.
- `harnais-0/` : la version de départ (le harnais du palier précédent en production, ou un harnais vide au palier 1).
- `sujet.py` : lit `{"harnais","entree"}` sur l'entrée standard, écrit la proposition en JSON
  (`{"action","commande","args"}`). C'est l'agent, tel que le harnais le configure.
- `comparateur` : `egalite` avec une matrice d'erreurs. Agir à tort (« executer » attendu « rien » ou « proposer ») est
  une erreur **interdite** ; « proposer » à la place d'« executer » est tolérée.
- `chercheur.py` : la commande qui écrit une nouvelle version du harnais (un agent, ou un script) ; une idée par essai.
- `chantier.json` : réglages (voir la documentation du moteur) ; `objectif.examen_min` = la `reussite_min` de
  `reponses.json` exprimée sur 100.

`python3 -m boucle verifier chantier.json`, puis `python3 -m boucle run chantier.json`. Codes de sortie : 0 objectif atteint ;
3 pause (deux échecs de suite à l'examen : le chef écrit `bloque`) ; 4 arrêt (passes ou budget épuisés).

**Le test du palier n'entre jamais dans le moteur.** La seule épreuve finale est ce test, rejoué par le vérificateur
indépendant dans le vrai outil ; la part tenue à part n'est qu'un garde-fou contre l'apprentissage par cœur des données.

**La limite de la machine** (`reponses.json` → `machine`) se mesure à chaque version gardée : taille, temps de réponse.
Une version qui la dépasse ne se garde pas.

Travail lourd en CPU : préfixer par `$AGENT_LIMITEUR` quand il est réglé (ex. `nice -n 10`). Ne lance jamais un modèle
local sans que le projet le prévoie (`acces-outil.json`, journal des paliers précédents).

## 4. Le compte rendu → `docs/agent/paliers/p<N>/journal.md`

Ajouter, sans réécrire le passé : les lots écrits (combien, de quel niveau), la relecture de
l'échantillon, chaque entraînement (commande, version, mesures), la version proposée et son
emplacement, ce qui reste faible. Rendre au chef la version proposée et son emplacement.

## Sur une liste d'écarts

Chaque écart du vérificateur dit la consigne, l'attendu et l'obtenu. Corriger par les données et
le harnais — **jamais en touchant au test**, jamais en écrivant une règle qui ne reconnaît que la
phrase du test.
