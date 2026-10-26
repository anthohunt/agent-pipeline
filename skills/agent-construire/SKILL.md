---
name: agent-construire
description: Étape 2 « Construire un palier » de la pipeline agent (nœud `construire`, sur un serveur, autonome) — le chef lit l'avancement, choisit le mode (palier ou retours), fait tourner le cycle constructeur → vérificateur indépendant jusqu'au PASS au critère de l'utilisateur, puis livre la préversion et sa fiche « sait faire / ne sait pas encore ». Un lancement = un palier, ou un tour de retours. Jamais de production.
---

# Agent — Construire un palier (le chef)

Nœud `construire` du graphe `agent`. Il tourne **seul sur le serveur** : personne ne répond pendant
qu'il tourne. Tu décides, tu écris pourquoi dans le journal, tu continues.
`tools/agent-lancer.py` le lance et le **relance** tant que son contrôle
(`agent-construire`) n'est pas vert.

Contrat des fichiers : `docs/contrat.md` à la racine du dépôt de la pipeline. Chemins
relatifs au workspace.

## Le chef ne construit pas et ne vérifie pas

Il dispatche, route l'information, tient le journal et l'avancement. Les données et
l'entraînement sont au **constructeur** (`agent-construire.1`) ; la vérification au
**vérificateur indépendant** (`agent-construire.2`), un agent frais qui n'a rien construit.
Celui qui vérifie n'est jamais celui qui construit.

## 2.1 Choisir le mode

1. Un `docs/agent/retours/tour-<N>.json` au statut `a-traiter` → **mode retours** sur le plus ancien (§ 2.7).
2. Sinon le palier courant : le premier de `docs/agent/paliers.json` qui n'est pas en
   `production`. Au statut `a-faire` ou `en-cours` → **mode palier**. Déjà en `preversion` sans
   tour à traiter → rien à faire, la revue attend : terminer.
3. Écrire `docs/agent/avancement.json` (`phase`, `tour` = nombre de tours de `revue.json`,
   `palier_courant`, `paliers` [n, titre, statut], `maj`, `bloque`), passer le palier à
   `en-cours` dans `paliers.json`, ouvrir `docs/agent/paliers/p<N>/journal.md`.

L'état vit dans ces fichiers, jamais dans la mémoire d'un agent : une instance neuve doit pouvoir
reprendre en les lisant.

## 2.2 – 2.3 Données et entraînement (le constructeur)

Dispatcher un constructeur (Task) avec `agent-construire.1`, le palier, les chemins de
`besoin.md`, `reponses.json`, `acces-outil.json`, `catalogue.json`, `consignes-reelles.jsonl`, et
la liste des écarts du dernier vérificateur s'il y en a. Il rend :

- `paliers/p<N>/test.jsonl` — le test du palier, **recopié** des consignes réelles (mêmes `id`,
  même `texte`) ; il ne change pas en cours de palier ;
- `paliers/p<N>/donnees/entrainement.jsonl` — les données du palier seul, phrases évidentes
  d'abord puis situations plus complexes ; aucune phrase du test ;
- l'agent entraîné (harnais, et poids si le projet en entraîne), à son emplacement, dans la
  limite de `reponses.json` → `machine` ;
- ses mesures, écrites au journal.

## 2.4 – 2.5 Vérification et boucle

Dispatcher un vérificateur **frais** (Task) avec `agent-construire.2`, le palier, la version à
vérifier, `acces-outil.json` et le critère. Il rejoue chaque consigne du test dans le vrai outil
et écrit `paliers/p<N>/verification.json`.

- **PASS** au critère → § 2.6.
- **FAIL** → le constructeur repart avec la liste des écarts (jamais avec le test à modifier),
  puis un **nouveau** vérificateur frais rejoue. Trois cycles au plus ; au-delà, écrire `bloque`
  dans l'avancement avec les écarts restants et terminer.

Chaque cycle s'écrit au journal : ce qui a été changé, le verdict, la réussite, les actions à tort.

## 2.6 Livrer la préversion

- La commande `preversion` de `acces-outil.json` — **jamais `production`** : la production
  n'arrive qu'après le « bon » de l'utilisateur, à la revue.
- `paliers/p<N>/fiche.md` : `## Sait faire` (ce que les consignes du test réussies montrent) et
  `## Ne sait pas encore` (les commandes hors palier, les consignes ratées, ce qui reste à venir).
- `docs/agent/versions.json` : une version nouvelle (`V1`, `V2`… sans trou), `palier`, `tour`
  = nombre de tours de `revue.json` à la livraison, `date`, `emplacement`, `statut: preversion`.
- Le palier passe à `preversion` dans `paliers.json` et dans l'avancement (`phase: preversion`).

## 2.7 Mode retours

Le tour porte le palier, et chaque retour son `dit`, sa `consigne` et son `attendu`.

1. Le constructeur corrige sur ces retours ; une consigne essayée par l'utilisateur et absente du
   test y entre si elle est réelle (elle s'ajoute aussi à `consignes-reelles.jsonl`, `source`
   = le tour de revue).
2. Un vérificateur frais rejoue le test du palier **en entier** et chaque `attendu`, dans l'outil.
3. Sur PASS : nouvelle version en préversion (§ 2.6), le tour passe à `traite`.

## Avant de terminer

```bash
python3 "$FLUX_HOME/runtime/validate.py" agent-construire <workspace>
```

Vert seulement si le palier courant est en préversion sur un PASS qui tient au critère. Ne poser
DONE qu'au vert, ou avec `bloque` écrit et motivé.

## Ce qu'on ne fait jamais

- Toucher au test d'un palier pour le faire passer, ou y mettre une phrase générée.
- Mettre en production.
- Laisser le constructeur vérifier, ou un vérificateur rejouer après avoir lu le journal du
  constructeur : il reçoit la version, le test et l'accès, rien d'autre.
- Fixer des quantités de données à l'avance, faire passer un examen scellé ou une porte : le
  palier se juge sur ses vraies consignes, au critère de l'utilisateur.
- Travail lourd en CPU sans le préfixe `$AGENT_LIMITEUR` quand il est réglé (ex. `nice -n 10`).
