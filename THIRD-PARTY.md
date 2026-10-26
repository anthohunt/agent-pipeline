# Dépendances tierces

Ce dépôt ne redistribue aucune bibliothèque tierce. Les composants ci-dessous sont installés à part, par
l'utilisateur, quand il en a besoin.

| Composant | Rôle | Licence | Obligatoire |
|---|---|---|---|
| flux (moteur de pipelines, dépôt séparé du même auteur) | joue le graphe, lance les agents, passe les contrôles | Apache 2.0 | oui |
| la-boucle-engine (moteur d'entraînement, dépôt séparé du même auteur) | entraîne l'agent d'un palier, juge sur une part tenue à part | Apache 2.0 | pour l'étape « construire » |
| Python 3.10+ (bibliothèque standard) | outils, contrôles, programme du module | PSF | oui |
| jsonschema | vérification des graphes par le moteur flux | MIT | oui (via flux) |
| tmux | sessions détachées du lanceur de l'étape 2 | ISC | pour lancer des agents |
| Claude Code (Anthropic) | les agents ; le module `mod/` est un mod de Claude Code | conditions d'Anthropic (non libre) | pour lancer des agents |

Toutes ces licences sont compatibles avec la licence Apache 2.0 du code de ce dépôt : rien n'est recopié ni lié
statiquement.
