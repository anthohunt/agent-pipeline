# agent-pipeline

> **In short (English)**: a three-step agent pipeline that builds a specialised agent *by steps* ("paliers"): design the
> need in a short conversation (at most four questions, then the agent proposes step 1 itself), build one step at a
> time — a builder writes the step's data and trains the agent with the [La boucle](#la-boucle-lentraînement) engine,
> an **independent verifier** replays the user's *real* instructions in the *real* tool — and review each preview with
> the user until they say "good", which puts it in production. It runs on the [flux](#le-moteur-flux) pipeline engine
> and Claude Code. Docs are in French.

Une pipeline d'agents en trois étapes qui construit un agent spécialisé **par paliers**, comme un logiciel : une première
version qui sait peu de choses mais les fait bien, puis des versions de plus en plus complètes, chacune essayée par
l'utilisateur dans son vrai outil avant la production.

| # | Étape | Mode | Contrôle de fin d'étape |
|---|---|---|---|
| 1 | **Concevoir** | en conversation, quatre questions au plus | `agent-concevoir` |
| 2 | **Construire un palier** | autonome, sur un serveur, relancée jusqu'au vert | `agent-construire` |
| 3 | **Revue** | en conversation (barrière humaine) | `agent-revue` |

1. **Concevoir** : le besoin (mot pour mot), l'accès à l'outil réel (constaté en rejouant une consigne pour de vrai), les
   **consignes réelles** de l'utilisateur (jamais générées, sauf décision citée), la limite de la machine, ce qui rend un
   palier prêt ; puis l'agent **propose et montre seul** le palier 1 : une dizaine de commandes et son test.
2. **Construire un palier** : un constructeur écrit les données du palier et entraîne l'agent ; un **vérificateur
   indépendant** (agent neuf, qui n'a rien construit) rejoue chaque consigne du test dans le vrai outil, compte ce que
   l'outil a *vraiment* fait, et rend PASS ou FAIL au critère de l'utilisateur ; livraison en **préversion**, avec sa
   fiche « sait faire / ne sait pas encore ». Jamais de production à cette étape.
3. **Revue** : l'utilisateur essaie la préversion. « Bon » la met en production, puis palier suivant (proposé et
   montré) ou arrêt ; des retours, gardés mot pour mot, relancent la construction sur ce palier.

Chaque étape a un **contrôle automatique** (`validators/`) qui juge ses livrables : tant qu'il est rouge, l'étape
suivante ne démarre pas. Le contrôle de la construction recalcule la réussite et les actions à tort depuis les résultats
rejoués : un verdict qui ne concorde pas fait échouer le nœud.

## Contenu du dépôt

| Dossier | Ce qu'il contient |
|---|---|
| `workflows/` | le graphe `agent.json` (les 3 nœuds) |
| `skills/` | les consignes des agents, une par dossier (`<nom>/SKILL.md`) : `agent-concevoir`, `agent-construire` (le chef), `agent-construire.1` (le constructeur), `agent-construire.2` (le vérificateur), `agent-revue`, `agent-start` (chemin de secours) |
| `validators/` | les contrôles de fin d'étape (`agent_concevoir.py`, `agent_construire.py`, `agent_revue.py`, `agent_commun.py`) |
| `tools/` | le lanceur de l'étape 2 (`agent-lancer.py`, qui la relance jusqu'au vert) et son état (`agent-etat.py`, une ligne JSON) |
| `mod/` | un mod de Claude Code : volet de suivi, bande au-dessus de l'invite, décisions de l'utilisateur gardées mot pour mot (`/agent <projet>`) |
| `docs/contrat.md` | le contrat des fichiers entre graphe, outils et module |
| `exemple/` | `demo.sh` (démonstration de bout en bout sans compte) et `palier-1/` (l'entraînement d'un palier avec La boucle, sans modèle d'IA) |
| `tests/` | tests des contrôles (par mutation), du lanceur et de l'état |

## Dépendances : deux dépôts du même auteur

### Le moteur flux

La pipeline ne tourne pas seule : elle est jouée par **flux**, un moteur de pipelines d'agents (dépôt séparé, Apache 2.0).
Il lit les graphes, injecte les consignes, lance les agents dans des sessions Claude Code et passe les contrôles. Ce
dépôt ne le recopie pas : clonez-le dans `vendor/flux` (ou ailleurs, et indiquez son chemin dans `FLUX_HOME`).

### La boucle (l'entraînement)

L'étape 2 entraîne l'agent d'un palier avec le **moteur de La boucle** (dépôt `la-boucle-engine`, Apache 2.0,
bibliothèque standard Python seule, commande publique `python3 -m boucle …`) : mesurer, lire les fautes, essayer une
idée, garder ce qui monte ; une **part tenue à part** des données du palier joue l'examen du moteur, que le chercheur ne
voit jamais. Sans ce dépôt, l'étape « construire » ne peut pas entraîner d'agent ; les étapes 1 et 3, les contrôles, le
lanceur et la démonstration fonctionnent sans lui, sauf la dernière étape de `exemple/demo.sh`. Clonez-le dans
`vendor/la-boucle-engine` (ou indiquez `BOUCLE_HOME`), ou `pip install git+https://github.com/anthohunt/la-boucle-engine`.
Le test du palier (les consignes réelles) n'entre **jamais** dans le moteur : seul le vérificateur le rejoue.

## Installer

Prérequis : Linux ou macOS, `git`, Python 3.10+, `pip`. Pour lancer de vrais agents : `tmux` et Claude Code connecté
à un compte.

```bash
git clone <adresse de agent-pipeline> agent-pipeline
cd agent-pipeline
git clone <adresse de flux> vendor/flux                          # le moteur (voir son propre README)
git clone <adresse de la-boucle-engine> vendor/la-boucle-engine  # l'entraînement
python3 -m pip install -r vendor/flux/requirements.txt           # jsonschema
cp .env.example .env                                             # puis adapter les chemins
set -a; . ./.env; set +a
```

Vérifier l'installation :

```bash
python3 "$FLUX_HOME/runtime/verifier-graphes.py" workflows/*.json   # → GRAPHES CONFORMES
python3 -m unittest discover -s tests                              # contrôles, lanceur, état
python3 -m unittest discover -s mod/programme/tests                 # programme du module
bash exemple/demo.sh                                                # démonstration de bout en bout
```

`exemple/demo.sh` crée une run « assistant-biblio » (projet inventé), écrit le brief du nœud « concevoir » avec ses
consignes, montre le contrôle de l'étape 1 rouge sur une run vide puis vert pour les trois contrôles sur une run
finie d'exemple, lit l'état de la construction, demande au lanceur ce qu'il ferait, puis entraîne un palier avec La boucle.
**Tout cela tourne sans compte.** La suite — la conversation de conception et les agents de construction — exige
Claude Code connecté.

## Utiliser

1. **Nouvelle run** : dans Claude Code, avec le mod, `/agent <projet>` ; sans le mod, le skill `/agent-start`
   (création par `python3 $FLUX_HOME/runtime/new-run.py agent '<projet>'`).
2. **Concevoir** dans la même session : les quatre questions, puis le palier 1 proposé.
3. **Construire** : `python3 tools/agent-lancer.py <workspace>` lance l'étape 2 en détaché (un palier, ou un tour de
   retours) et la relance jusqu'au contrôle vert ; `python3 tools/agent-etat.py <workspace>` dit où elle en est.
4. **Revue** : skill `agent-revue` (ou le volet du mod) ; « bon » met en production, des retours relancent la construction.

## Réglages

Tout ce qui dépend de la machine passe par des variables d'environnement, listées avec des valeurs d'exemple dans
`.env.example` : emplacement des moteurs (`FLUX_HOME`, `BOUCLE_HOME`), ce que flux lit pour jouer cette pipeline
(`FLUX_WORKFLOWS_DIR`, `FLUX_SKILLS_DIR`, `FLUX_VALIDATORS_PATH`), compte des agents (`AGENT_MOTEUR`, un moteur de
`moteurs.json` de flux), préfixe des commandes lourdes (`AGENT_LIMITEUR`).

## Ce que cette pipeline ne fait pas

Elle ne fournit ni l'outil que l'agent doit piloter, ni un modèle : l'utilisateur donne l'accès à **son** outil réel et
la limite de **sa** machine ; un exemple qui appelle un modèle d'IA payant s'arrête à l'étape qui demande un compte.

## Licences

- **Code** (Python, TypeScript, shell, graphe JSON) : [Apache 2.0](LICENSE), voir [NOTICE](NOTICE).
- **Textes, documents et schémas** (consignes `skills/*/SKILL.md`, `docs/`, README, textes du graphe) :
  [CC BY 4.0](LICENSE-docs). Vous pouvez les réutiliser et les adapter en citant l'auteur, Anthony Hunt.
- Dépendances tierces et leurs licences : [THIRD-PARTY.md](THIRD-PARTY.md).

Auteur : Anthony Hunt.
