---
name: agent-concevoir
description: Étape 1 « Concevoir » de la pipeline agent (nœud `concevoir`, en conversation) — fixer le besoin en quatre questions au plus (le besoin, l'accès à l'outil réel, la limite de la machine, ce qui rend un palier prêt), enregistrer les consignes réelles de l'utilisateur, puis proposer et montrer seul le palier 1. Injecté par le graphe `agent` ; joué dans la session ouverte par `/agent <projet>` (secours `/agent-start`).
---

# Agent — Concevoir

Nœud `concevoir` du graphe `agent` (concevoir → construire un palier → revue). Un agent se
construit comme un logiciel : un premier palier qui sait peu de choses mais les fait bien, puis
des paliers de plus en plus complets, chacun essayé par l'utilisateur avant la production. Cette
étape ne fixe que ce qu'il faut pour que le palier 1 parte en construction **sans rien demander**.

Contrat des fichiers : `docs/contrat.md` à la racine du dépôt de la pipeline. Tous les
chemins ci-dessous sont relatifs au workspace de la run.

## La règle qui commande tout : le moins de questions possible

**Quatre questions au plus, et seulement celles-ci** :

1. le besoin — c'est le premier message de l'utilisateur, on ne le lui demande pas ;
2. l'accès à l'outil réel — seulement si on ne le retrouve pas ;
3. la limite de la machine — taille et temps de réponse ;
4. ce qui rend un palier prêt à être présenté.

Tout le reste, l'agent le **propose et le montre** : la vision, le catalogue, le palier 1, son
test. Jamais de question dont la réponse n'est qu'un « oui » : la réponse à une question vaut
validation de ce qu'elle tranche, citée mot pour mot.

Chaque question : une seule par message, en A/B/C avec une option D « autre chose, précise-moi »
écrite parmi les autres. L'option A est ce que l'agent recommande, d'après ce qu'il a trouvé.

**Chercher avant de demander** : dossiers du projet, configs, dépôts, notes du sujet. Ce qui se retrouve ne se demande pas ; on dit en une ligne ce
qu'on a trouvé et où.

## Déroulé

### 1.1 Le besoin et la vision → `docs/agent/besoin.md`

Le premier message est le besoin : il se garde mot pour mot (citation en `> `). Dessous, la
**vision** en points : ce que l'agent final saura faire, ce qu'il ne fera pas. La vision se
déduit, elle ne se fait pas valider.

### 1.2 L'accès à l'outil réel → `docs/agent/acces-outil.json`

Sans accès à l'outil, aucun palier ne se vérifie. Champs : `outil`, `url`, `rejouer` (la
commande qui rejoue UNE consigne dans le vrai outil et rend ce qu'il a fait), `preversion` et
`production` (la commande ou le geste qui livre une version ; `null` si à construire au
palier 1), `fiche` (où la fiche de version s'affiche dans l'outil), `constate`.

**`constate` s'écrit après avoir rejoué une consigne pour de vrai** : sa date, et ce que l'outil
a fait. Un accès décrit mais jamais essayé n'est pas un accès.

### 1.3 Les consignes réelles → `docs/agent/consignes-reelles.jsonl` + `docs/agent/catalogue.json`

Le test de TOUS les paliers est fait de consignes **dites pour de vrai**, jamais générées. Une
phrase générée mesure la ressemblance avec le générateur, pas l'usage.

Exception : l'utilisateur peut décider que l'agent génère les consignes (« tu les génères »). On
l'écrit dans `reponses.json`, clé `consignes` : `{"generees_autorisees": true, "citation": "<ses mots>"}` ;
chaque ligne générée porte une `source` qui le dit. Le contrôle ne les accepte qu'avec cette citation.

- Des consignes réelles existent déjà pour ce projet : les reprendre, dire combien et d'où, et
  proposer en A/B/C/D de s'en servir telles quelles, d'y ajouter une séance, ou de les remplacer.
- Sinon, la **séance d'usage réel** : l'utilisateur se sert de son outil une dizaine de minutes en
  parlant à l'agent ; chaque consigne s'enregistre avec ce qu'il attendait.
- Une ligne : `id`, `texte` (mots exacts), `contexte` (écran, sélection…), `attendu`
  (`action` executer | proposer | rien, `commande`, `args`), `source` (la séance ou le pilote).
- `catalogue.json` : les commandes que l'agent peut faire, **lues dans l'outil réel**. Chaque
  commande attendue par une consigne y figure ; une consigne impossible avec le catalogue est un
  trou du catalogue, pas une erreur de l'agent.

### 1.4 La limite de la machine → `reponses.json`, clé `machine`

Où l'agent tournera, sa taille maximale (`taille_max_go`), son temps de réponse maximal
(`latence_max_s`). Une limite déjà connue pour ce projet est l'option A.

### 1.5 Ce qui rend un palier prêt → `reponses.json`, clé `critere`

C'est la règle que le vérificateur appliquera seul à chaque palier. Options type : A toutes ses
consignes de test réussies / B 9 sur 10 sans aucune action à tort / C 8 sur 10 avec au plus une
action à tort / D autre chose. S'écrit en `reussite_min` (]0, 1]) et `actions_a_tort_max`.

`reponses.json` porte aussi `besoin` et `acces`, chacun avec la citation de l'utilisateur.

### 1.6 Le palier 1 → `docs/agent/paliers.json` + `docs/agent/palier-1.md`

L'agent le choisit seul et le **montre** en cinq lignes au plus :

- **une dizaine de commandes**, les plus utiles d'après les consignes réelles (les plus
  fréquentes, celles dont dépendent les autres) ;
- son **test** : les consignes réelles qui appellent ces commandes, plus des consignes
  « proposer » et « rien » proches, pour qu'un agent qui agit à tort se voie ;
- chaque consigne du test qui exécute appelle une commande du palier.

Une dernière ligne propose l'option de la **feuille de route complète** : seulement si
l'utilisateur la veut, les paliers suivants s'écrivent avec lui (`paliers.json`, statut
`a-faire`, chacun avec ses commandes et son test).

`palier-1.md` : ses commandes, ses consignes de test, pourquoi celles-là.

## Fin de l'étape

Le contrôle `agent-concevoir` doit être vert :

```bash
python3 "$FLUX_HOME/runtime/validate.py" agent-concevoir <workspace>
```

Rouge = corriger ce qu'il dit, jamais le contourner. Vert = la construction peut partir : le
module la lance (outil `lancer`), en secours `python3 tools/agent-lancer.py <workspace>` (depuis la racine du dépôt de la pipeline).

## Ce qu'on ne fait jamais

- Une question de plus que les quatre, ou une question qui ne sert qu'à faire dire « oui ».
- Une consigne générée dans `consignes-reelles.jsonl`, ou dans un test, sans décision citée de l'utilisateur.
- Fixer des seuils, des quantités de données ou une étude statistique : le palier se juge sur ses
  vraies consignes, au critère de l'utilisateur.
- Lancer un entraînement depuis cette étape.
