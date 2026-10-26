# Pipeline agent en 3 étapes — contrat entre le graphe, les commandes et le module

Ce fichier fixe ce que chaque morceau lit et écrit, pour que le
graphe (`workflows/agent.json` + skills `agent-*`), les commandes (`tools/agent-lancer.py`, `tools/agent-etat.py`) et
le module Claude Code (`mod/`) se branchent sans se parler. Chemins relatifs au workspace de la
run (`~/agent-runs/<run>/`, réglable par le `workspace_root` du graphe). Un changement de format s'écrit ici d'abord.

Un agent se construit comme un logiciel : par **paliers** (une première version qui sait peu de choses, puis des
versions de plus en plus complètes). Chaque palier est construit en autonomie, livré en **préversion**, essayé par
l'utilisateur dans son vrai outil ; « bon » le passe en **production**, puis on continue au palier suivant ou on
s'arrête.

## Étape 1 — Concevoir (nœud `concevoir`, type `local`, en conversation)

Le moins de questions possible. Seules questions : le besoin, l'accès à l'outil réel, la limite de la machine, ce
qui rend un palier prêt à être présenté. Le reste, l'agent le propose et le montre.

| Fichier | Contenu |
| --- | --- |
| `docs/agent/besoin.md` | le besoin mot pour mot (citation) puis la vision : ce que l'agent final saura faire |
| `docs/agent/reponses.json` | les quatre réponses de l'utilisateur, chacune avec ses mots exacts — voir ci-dessous |
| `docs/agent/acces-outil.json` | `{"outil":"…","url":"https://…","rejouer":"<commande qui rejoue une consigne dans le vrai outil et rend ce qu'il a fait>","preversion":"<commande ou geste>"\|null,"production":"<commande ou geste>"\|null,"fiche":"<où la fiche de version s'affiche dans l'outil>"\|null,"constate":{"date":"<ISO>","resultat":"<ce qu'on a vu en rejouant une consigne>"}}` |
| `docs/agent/consignes-reelles.jsonl` | une ligne par consigne RÉELLE (dite par un utilisateur dans l'outil ; générée seulement si `reponses.json` porte `consignes.generees_autorisees` et la citation de l'utilisateur) : `{"id":"…","texte":"<mots exacts>","contexte":{…}\|null,"attendu":{"action":"executer"\|"proposer"\|"rien","commande":"<id>"\|null,"args":{…}\|null},"source":"seance-<date>"\|"pilote-…"}` |
| `docs/agent/catalogue.json` | `{"commandes":[{"id":"…","titre":"…","args":{…}}]}` — ce que l'agent peut faire dans l'outil, lu dans l'outil réel |
| `docs/agent/paliers.json` | la feuille de route : `{"paliers":[{"n":1,"titre":"…","commandes":["<id>"],"test":["<id consigne>"],"statut":"a-faire"\|"en-cours"\|"preversion"\|"production"}]}` — au moins le palier 1 ; les suivants seulement si l'utilisateur a voulu la feuille de route complète |
| `docs/agent/palier-1.md` | le palier 1 tel qu'il a été montré : ses commandes, ses consignes de test, pourquoi celles-là |

`reponses.json` :

```json
{"besoin":   {"citation":"<mots exacts>"},
 "acces":    {"citation":"<mots exacts>"},
 "machine":  {"citation":"<mots exacts>","taille_max_go":2.4,"latence_max_s":1.0,"machine":"<où il tourne>"},
 "critere":  {"citation":"<mots exacts>","reussite_min":0.9,"actions_a_tort_max":0}}
```

`reussite_min` ∈ ]0, 1] (1 = toutes les consignes du test réussies) ; `actions_a_tort_max` = nombre de consignes
du test où l'agent agit alors qu'il ne fallait pas, ou fait autre chose que l'attendu.

## Étape 2 — Construire un palier (nœud `construire`, type `agent`, serveur)

Un lancement = un palier (le premier de `paliers.json` qui n'est ni en préversion ni en production), ou un tour de
retours. Constructeur (données du palier, entraînement par le moteur de La boucle) puis vérificateur indépendant
(rejoue le test du palier dans le vrai outil). Livré en préversion, jamais en production.

| Fichier | Contenu |
| --- | --- |
| `docs/agent/avancement.json` | `{"phase":"palier"\|"retours"\|"preversion","tour":<tours de revue passés>,"palier_courant":N,"paliers":[{"n":1,"titre":"…","statut":"…"}],"maj":"<ISO>","bloque":null\|"<raison>"}` |
| `docs/agent/paliers/p<N>/donnees/entrainement.jsonl` | les données d'entraînement du palier, phrases évidentes d'abord puis situations plus complexes ; aucune phrase du test |
| `docs/agent/paliers/p<N>/test.jsonl` | les consignes du test du palier, recopiées de `consignes-reelles.jsonl` (mêmes `id`, même `texte`) |
| `docs/agent/paliers/p<N>/journal.md` | la chronologie du palier : données, entraînements lancés, mesures, cycles constructeur → vérificateur |
| `docs/agent/paliers/p<N>/verification.json` | `{"constructeur":"<qui a construit>","verificateur":"<qui vérifie, ≠ constructeur>","rejoue_dans":"<url ou outil réel>","date":"<ISO>","version":"V…","resultats":[{"id":"…","attendu":{…},"obtenu":{…},"ok":bool,"a_tort":bool}],"reussite":0.0,"actions_a_tort":0,"verdict":"PASS"\|"FAIL"}` |
| `docs/agent/paliers/p<N>/fiche.md` | la fiche de version : `## Sait faire` / `## Ne sait pas encore` |
| `docs/agent/versions.json` | `{"versions":[{"version":"V1","palier":1,"tour":<tours de revue passés à la livraison>,"date":"<ISO>","emplacement":"<où est la préversion>","statut":"preversion"\|"production"}]}` |

PASS ⇔ `reussite ≥ critere.reussite_min` ET `actions_a_tort ≤ critere.actions_a_tort_max`. Le contrôle recalcule
les deux nombres depuis `resultats`.

## Étape 3 — Revue (nœud `revue`, type `local`, l'utilisateur)

L'utilisateur essaie la préversion dans son vrai outil.

| Fichier | Contenu |
| --- | --- |
| `docs/agent/revue.json` | `{"tours":[{"tour":1,"palier":1,"version":"V1","verdict":"good"\|"retours","date":"<ISO>","citation":"<mots exacts>","suite":"palier-suivant"\|"arret"\|null}]}` |
| `docs/agent/retours/tour-<N>.json` | `{"tour":N,"palier":P,"date":"<ISO>","statut":"a-traiter"\|"traite","retours":[{"id":"R1","dit":"<mots exacts>","consigne":"<texte essayé>"\|null,"attendu":"<critère vérifiable>"}]}` |
| `docs/agent/retours/tour-<N>.md` | la même liste, lisible |
| `docs/agent/production.json` | `{"productions":[{"palier":P,"version":"V…","date":"<ISO>","fiche":"docs/agent/paliers/p<P>/fiche.md"}]}` |

Verdict `good` → mise en production (commande `production` de `acces-outil.json`), fiche affichée dans l'outil,
`production.json` et `paliers.json` (statut `production`) à jour, puis `suite` : `palier-suivant` (le palier N+1 est
ajouté à `paliers.json`, au statut `a-faire`, et la construction repart) ou `arret` (la run est close).
Verdict `retours` → `construire` repart en mode retours sur le plus ancien tour `a-traiter`.

## Commandes (sur le serveur des runs, une ligne JSON sur stdout)

| Commande | Effet |
| --- | --- |
| `python3 tools/agent-lancer.py <ws> [--dry-run]` | lance l'étape 2 (palier, ou tour de retours) en détaché et la relance jusqu'au contrôle vert ; `{"ok":true,"tmux":"…","mode":"palier"\|"retours","palier":N}` ou `{"ok":false,"refus":"…"}` |
| `python3 tools/agent-etat.py <ws>` | lecture seule : `{"en_cours":bool,"phase":…,"tour":N,"palier_courant":N,"paliers":[…],"preversion":{…}\|null,"production":{…}\|null,"verification":{…}\|null,"bloque":null\|"<raison>","derniere_passe":{…}}` |

## Dépendance : La boucle (entraînement d'un palier)

L'étape 2 entraîne l'agent d'un palier avec le moteur de La boucle (dépôt `la-boucle-engine`, commande
`python3 -m boucle`), dans un **chantier** par palier : `docs/agent/paliers/p<N>/chantier/` (`chantier.json`,
`donnees/entrainement.jsonl`, `donnees/examen.jsonl` = une part tenue à part des données du palier, `harnais-0/`,
`sujet.py`, `chercheur.py`). Le test du palier (`test.jsonl`, consignes réelles) n'entre jamais dans le moteur : il est
rejoué seulement par le vérificateur indépendant. Le détail est dans le skill `agent-construire.1`.
