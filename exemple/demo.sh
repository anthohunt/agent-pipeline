#!/usr/bin/env bash
# Démonstration de bout en bout, sans compte Claude ni modèle d'IA : tout ce que la pipeline agent fait AVANT et
# AUTOUR d'un agent, plus l'entraînement d'un palier avec le moteur de La boucle (chercheur écrit à la main).
#
#   bash exemple/demo.sh
#
# 1. crée une run « assistant-biblio » (projet inventé : un assistant pour une médiathèque fictive) avec le moteur flux ;
# 2. écrit le brief du nœud « concevoir » : objectif, check-list et consignes (skills/) injectées ;
# 3. passe le contrôle de fin d'étape 1 sur la run vide : rouge, avec la liste de ce qui manque ;
# 4. remplit un second espace de travail avec les livrables d'une run finie (exemple inventé) et passe les trois
#    contrôles (concevoir, construire, revue) : verts ;
# 5. lit l'état de la construction (tools/agent-etat.py) ;
# 6. demande au lanceur de l'étape 2 ce qu'il ferait (--dry-run) : il refuse, l'étape 1 n'a rien livré ;
# 7. entraîne l'agent du palier 1 avec La boucle (exemple/palier-1) : de 50 à 85 sur la part tenue à part, sans modèle d'IA.
# La suite — la conversation de conception (/agent-start dans Claude Code) et les agents de construction
# (agent-lancer.py sans --dry-run) — exige Claude Code connecté à un compte.
set -euo pipefail
ICI="$(cd "$(dirname "$0")/.." && pwd)"
export AGENT_PIPELINE_HOME="${AGENT_PIPELINE_HOME:-$ICI}"
export FLUX_HOME="${FLUX_HOME:-$ICI/vendor/flux}"
BOUCLE_HOME="${BOUCLE_HOME:-$ICI/vendor/la-boucle-engine}"
export FLUX_WORKFLOWS_DIR="${FLUX_WORKFLOWS_DIR:-$AGENT_PIPELINE_HOME/workflows}"
export FLUX_SKILLS_DIR="${FLUX_SKILLS_DIR:-$AGENT_PIPELINE_HOME/skills}"
export FLUX_VALIDATORS_PATH="${FLUX_VALIDATORS_PATH:-$AGENT_PIPELINE_HOME/validators}"
[ -f "$FLUX_HOME/runtime/run-node.py" ] || { echo "moteur flux introuvable : FLUX_HOME=$FLUX_HOME (voir le README)"; exit 1; }
[ -f "$BOUCLE_HOME/boucle/__main__.py" ] || { echo "moteur La boucle introuvable : BOUCLE_HOME=$BOUCLE_HOME (voir le README)"; exit 1; }

titre() { printf '\n== %s\n' "$1"; }

titre "1. Nouvelle run"
WS="$(python3 "$FLUX_HOME/runtime/new-run.py" agent assistant-biblio | tail -1)"
echo "workspace : $WS"

titre "2. Brief du nœud « concevoir » (étape interactive : le moteur ne la lance pas)"
python3 "$FLUX_HOME/runtime/run-node.py" agent concevoir --workspace "$WS" --brief-only
ETAT="${FLUX_STATE_DIR:-$FLUX_HOME/state}/agent/$(basename "$WS")/concevoir"
echo "brief : $(wc -c < "$ETAT/brief.md") octets ; consignes injectées : $(grep -c '^# Agent — Concevoir' "$ETAT/sys.md" || true) skill(s)"

titre "3. Contrôle de fin d'étape 1 sur la run vide (rouge attendu)"
if python3 "$FLUX_HOME/runtime/validate.py" agent-concevoir "$WS" 2> "$WS/gate.txt"; then
  echo "inattendu : vert"; exit 1
fi
echo "rouge, $(grep -c '^ *[0-9]' "$WS/gate.txt" || true) défaut(s) ; les trois premiers :"
grep '^ *[0-9]' "$WS/gate.txt" | head -3

titre "4. Livrables d'une run finie (exemple inventé), contrôles des trois étapes"
FINI="$(mktemp -d)/assistant-biblio-fini"
python3 -c "import pathlib, sys; sys.path.insert(0, '$AGENT_PIPELINE_HOME/tests'); import test_validateurs as t; t.fabriquer(pathlib.Path('$FINI'))"
for v in agent-concevoir agent-construire agent-revue; do
  python3 "$FLUX_HOME/runtime/validate.py" "$v" "$FINI" 2>/dev/null && echo "$v : vert" || { echo "$v : rouge"; exit 1; }
done

titre "5. État de la construction"
python3 "$AGENT_PIPELINE_HOME/tools/agent-etat.py" "$FINI"

titre "6. Lanceur de l'étape 2, à blanc, sur la run vide"
python3 "$AGENT_PIPELINE_HOME/tools/agent-lancer.py" "$WS" --dry-run || true

titre "7. Entraînement du palier 1 avec La boucle (chercheur écrit à la main, aucun modèle d'IA)"
P="$(mktemp -d)/palier-1"
cp -r "$AGENT_PIPELINE_HOME/exemple/palier-1" "$P"
cd "$P"
export PYTHONPATH="$BOUCLE_HOME${PYTHONPATH:+:$PYTHONPATH}"
python3 -m boucle sceller donnees/entrainement.jsonl > /dev/null
python3 -m boucle sceller donnees/examen.jsonl > /dev/null
python3 -m boucle verifier chantier.json
echo "version de départ (harnais-0), note sur la part tenue à part :"
python3 -m boucle noter chantier.json harnais-0 --examen | grep '"note"'
python3 -m boucle run chantier.json | tail -2
echo "(le test du palier, fait de vraies consignes, n'est PAS entré dans le moteur : il est rejoué par le vérificateur)"

titre "Fin"
echo "Tout ce qui précède tourne sans compte. La suite — la conversation de conception (/agent-start dans Claude Code)"
echo "et les agents de construction (agent-lancer.py sans --dry-run) — exige Claude Code connecté à un compte."
