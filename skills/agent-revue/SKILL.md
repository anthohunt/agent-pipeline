---
name: agent-revue
description: Étape 3 « Revue » de la pipeline agent (nœud `revue`, en conversation) — l'utilisateur essaie la préversion d'un palier dans son vrai outil ; « bon » la passe en production avec sa fiche affichée, puis palier suivant (proposé et montré par l'agent) ou arrêt ; des retours deviennent un tour de points vérifiables et la construction repart sur ce palier. Citations mot pour mot, une question à la fois.
---

# Agent — la revue d'un palier

Nœud `revue` du graphe `agent`, la barrière humaine. Rien ne se construit dans cette session :
on recueille un verdict, on met en production sur « bon », on écrit des retours vérifiables.

Contrat des fichiers : `docs/contrat.md` à la racine du dépôt de la pipeline.

## 3.1 Donner la préversion à essayer

Montrer la fiche du palier (`docs/agent/paliers/p<N>/fiche.md`) telle quelle, et où essayer la
préversion (`docs/agent/versions.json` → `emplacement`, `acces-outil.json` → `url`). Rien
d'autre : l'utilisateur essaie dans son outil.

## 3.2 Recueillir le verdict, mot pour mot

« Bon » ou des retours. La citation exacte part dans `docs/agent/revue.json` (tour, palier,
version essayée, verdict, date, citation, suite) — jamais une reformulation.

## 3.3 Des retours

Chaque retour : ce qui a été dit (`dit`, mots exacts), la consigne essayée (`consigne`) et un
`attendu` vérifiable dans l'outil. Un retour ambigu se lève par **une** question A/B/C/D. Puis
`docs/agent/retours/tour-<N>.json` et `.md` au statut `a-traiter`, avec le palier, et la
construction repart : outil `revue` du module, ou
`python3 tools/agent-lancer.py <workspace>` (depuis la racine du dépôt de la pipeline).

## 3.4 « Bon »

1. **Production** : la commande `production` de `acces-outil.json`, puis la fiche affichée là où
   `fiche` le dit, et constater qu'elle s'affiche.
2. `docs/agent/production.json` : `{palier, version, date, fiche}` ajouté à `productions` ; le
   palier passe à `production` dans `paliers.json` et la version dans `versions.json`.
3. **La suite**, une question : A palier suivant / B arrêt / D autre chose. Pour A, l'agent
   **propose et montre** le palier suivant en cinq lignes au plus (les commandes qui viennent
   ensuite en utilité, son test tiré des consignes réelles), l'ajoute à `paliers.json` au statut
   `a-faire`, et la construction repart. Si la feuille de route existe déjà, le palier suivant
   est le sien.
4. Verdict `good` avec sa `suite` dans `revue.json` (outil `revue` du module).

## Fin

```bash
python3 "$FLUX_HOME/runtime/validate.py" agent-revue <workspace>
```

## Ce qu'on ne fait jamais

- Mettre en production sans le « bon » de l'utilisateur.
- Reformuler ses mots dans `dit` ou `citation`.
- Corriger l'agent dans cette session : les retours partent à la construction.
