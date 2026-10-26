---
name: agent-start
description: Ouvre ou reprend une run de la pipeline « agent » (flux `agent`, 3 étapes : concevoir → construire un palier → revue) quand le module `/agent` n'est pas là. Déclencheurs — « /agent-start », « reprends la run agent », « on construit un agent », « joue le nœud concevoir de la pipeline agent ». Point d'entrée normal : le module `/agent <projet>`. Ce skill est le chemin de secours.
---

# agent-start — entrer dans la pipeline agent

## Le point d'entrée normal est le module `/agent <projet>`

Une run se mène dans une session Claude Code sur le serveur des runs (ou reliée à lui par SSH) avec la commande du
module : **`/agent <projet>`**. Le module crée ou reprend la run, ouvre le volet (où on en est,
ce qui t'attend, paliers, préversion et sa fiche), garde le besoin mot pour mot, avance les
sous-étapes, passe le gate de l'étape 1, lance la construction et enregistre la revue. Source :
`$AGENT_PIPELINE_HOME/mod` (README).

**Si `/agent` existe dans la session, utilise-le et arrête-toi ici.**

## La pipeline : trois étapes

| # | Nœud | Mode | Gate |
|---|---|---|---|
| 1 | **Concevoir** | en conversation, quatre questions au plus | `agent-concevoir` |
| 2 | **Construire un palier** | autonome, serveur, relancé par `agent-lancer` | `agent-construire` |
| 3 | **Revue** | en conversation (barrière humaine) | `agent-revue` |

• **Concevoir** : le besoin, l'accès à l'outil réel, les consignes réelles, la limite de la
  machine, ce qui rend un palier prêt ; puis l'agent propose seul le palier 1. Protocole
  `agent-concevoir`.
• **Construire** : un palier par lancement — données du palier, entraînement, vérificateur
  indépendant qui rejoue les vraies consignes dans le vrai outil, préversion et fiche. Protocoles
  `agent-construire`, `agent-construire.1` (constructeur), `agent-construire.2` (vérificateur).
• **Revue** : l'utilisateur essaie la préversion ; « bon » = production, puis palier suivant ou
  arrêt ; des retours relancent la construction sur ce palier. Protocole `agent-revue`.

## Déroulé (sans le module, sur le serveur des runs)

### 1. Résoudre la run

Les runs vivent sous `~/agent-runs/` (une par projet, réglable par le `workspace_root` du graphe). Nouveau projet :

```bash
python3 "$FLUX_HOME/runtime/new-run.py" agent '<nom du projet>'
```

### 2. Sortir le brief

```bash
python3 "$FLUX_HOME/runtime/run-node.py" agent concevoir --workspace ~/agent-runs/<run> --brief-only
```

Il écrit `sys.md` (les protocoles) et `brief.md` (objectif, check-list, livrables) sous
`$FLUX_STATE_DIR/agent/<run>/concevoir/` (par défaut `$FLUX_HOME/state/…`). **Lis les deux en entier avant de parler.**

### 3. Jouer l'étape 1, puis passer le gate

```bash
python3 "$FLUX_HOME/runtime/run-node.py" agent concevoir --workspace ~/agent-runs/<run>
```

Rouge = corriger ce qu'il dit et relancer, dans la même session.

### 4. Lancer et suivre la construction

```bash
python3 "$AGENT_PIPELINE_HOME/tools/agent-lancer.py" ~/agent-runs/<run>      # --dry-run : sans rien lancer
python3 "$AGENT_PIPELINE_HOME/tools/agent-etat.py" ~/agent-runs/<run>
```

### 5. La revue

Quand `agent-etat` dit `phase: preversion` et que rien ne tourne : protocole `agent-revue`.

## Ce qu'il ne faut pas faire

• **Lancer un nœud interactif depuis le flux** : personne ne répondrait.
• **Lancer `run-node.py agent construire` à la main** : sans le lanceur, rien ne le relance et
  le moteur n'est pas forcément celui des agents de construction.

## Références

• Graphe : `$AGENT_PIPELINE_HOME/workflows/agent.json` (la vérité exécutable)
• Contrat des fichiers : `$AGENT_PIPELINE_HOME/docs/contrat.md`
• Validateurs : `$AGENT_PIPELINE_HOME/validators/agent_*.py`
• Module : `$AGENT_PIPELINE_HOME/mod`
• Moteur : flux (`$FLUX_HOME`) ; entraînement : La boucle (`la-boucle-engine`)
