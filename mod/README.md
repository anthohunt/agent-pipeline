# Agent — module Claude Code

Conduit une run de la pipeline agent en 3 étapes, du besoin au dernier palier en production (fichiers et commandes :
`docs/contrat.md` ; graphe : `workflows/agent.json`, à la racine du dépôt). Un agent se construit par paliers : chaque palier est construit seul, livré en
préversion, essayé dans le vrai outil ; « bon » le passe en production, puis palier suivant ou arrêt.

1. **Concevoir**, en conversation, quatre questions au plus : le besoin, l'accès à l'outil réel, les consignes réelles,
   la limite de la machine, ce qui rend un palier prêt ; puis l'agent propose et montre seul le palier 1.
2. **Construire un palier**, sur le serveur : données, entraînement, vérificateur indépendant qui rejoue les vraies
   consignes dans le vrai outil, préversion et sa fiche « sait faire / ne sait pas encore ».
3. **Revue** : l'utilisateur essaie la préversion dans son outil. « Bon » la passe en production, puis palier suivant
   (la construction repart) ou arrêt (la run est close) ; ses retours relancent la construction sur ce palier.

## Utiliser

Installer le mod dans Claude Code depuis le dossier `mod/` (les mods de Claude Code sont en accès anticipé : leur API
peut changer). Deux réglages : `programme` (chemin de `mod/programme/agent.py` sur le serveur des runs) et `hote`
(`utilisateur@machine`, quand la session ne tourne pas sur ce serveur).

Dans une session Claude Code : `/agent <projet>`. Le volet s'ouvre à droite, la bande
au-dessus de l'invite dit où on en est et ce qui t'attend. Le message suivant est le besoin. `/agent` seul rouvre le
volet ; `/agent off` détache la session.

Le volet : ce qui t'attend en tête (avec le bouton « Lancer la construction » / « Relancer », ou « C'est bon » /
« J'ai des retours » pendant la revue), les liens de l'outil et de la préversion, la fiche de la préversion, puis les 3
étapes et leurs sous-étapes ; sous « Données et entraînement », les paliers et la dernière vérification.

## Comment c'est fait

- `programme/agent.py` : l'état de la run, dans ses fichiers (`<run>/state/module-agent.json`, journal
  `module-agent.jsonl`, `docs/agent/besoin.md`, `docs/agent/revue.json`, `docs/agent/retours/tour-N.json`). Il parle
  au moteur flux : création de la run (`runtime/new-run.py`), brief et gate des nœuds concevoir et revue
  (`runtime/run-node.py`), lancement et suivi de l'étape 2 (`tools/agent-lancer.py`, `tools/agent-etat.py`). L'état
  de l'étape 2 et de la revue se déduit à chaque lecture, il n'est jamais stocké. Une commande par geste, JSON sur
  l'entrée standard. Racines : `AGENT_RUNS` (défaut : le `workspace_root` du graphe, `~/agent-runs`), `FLUX_HOME` (le
  moteur flux, défaut `vendor/flux`), `AGENT_GRAPHES` et `AGENT_OUTILS` (défauts : `workflows/` et `tools/` du dépôt) ;
  une création de run est refusée si `AGENT_RUNS` n'est pas le `workspace_root` du graphe.
  Tests : `python3 -m unittest discover -s programme/tests` (faux moteur flux dans un dossier temporaire).
- `programme/parcours.json` : les étapes, sous-étapes, sorties et consignes de l'agent. Rien de propre à une run.
- `hooks/` : le mod (volet, bande, consignes et outils `mcp__agent__*` de la seule session rattachée ; le programme est
  joint en local sur le serveur des runs, par SSH ailleurs). Tests : `claude plugin test .` (vues fabriquées par le
  vrai programme : `python3 tests/fabriquer-fixtures.py`). Les types de l'API des mods (`.claude-plugin/types/`) sont
  générés par Claude Code et ne sont pas fournis ici.
