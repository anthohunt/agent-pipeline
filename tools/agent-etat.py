#!/usr/bin/env python3
"""Où en est l'étape 2 (« construire un palier ») d'une run de la pipeline agent — une ligne JSON sur stdout.

    python3 agent-etat.py <ws>

Contrat : docs/contrat.md (commandes). Le module /agent
(mod/programme/agent.py) lit en_cours, phase, tour, palier_courant, paliers[{n,titre,statut}],
preversion, production, verification, bloque ; le reste (derniere_passe, lanceur, revue, retours_a_traiter) est du
détail pour qui veut comprendre.

LECTURE PURE : rien ne s'écrit, nulle part. Ni validate.py (son hook réécrit run-report-bundle/) ni
socle.dossier_run (il crée le dossier d'état) ne sont appelés.

Sources : docs/agent/avancement.json et paliers.json (tenus par le nœud, skill agent-construire), versions.json,
production.json, la vérification du palier courant, state/lanceur.json (tools/agent-lancer.py) et l'état du nœud
construire dans le dossier d'état du moteur flux.
"""
import json, os, pathlib, re, subprocess, sys

ICI = pathlib.Path(__file__).resolve().parent
DEPOT = ICI.parent    # racine du dépôt agent-pipeline
# Le moteur flux est une dépendance : FLUX_HOME, sinon le clone conseillé par le README (vendor/flux).
FLUX = pathlib.Path(os.environ.get('FLUX_HOME') or DEPOT / 'vendor' / 'flux')
sys.path.insert(0, str(FLUX / 'runtime'))
import socle  # noqa: E402

WF = 'agent'
NOEUD = 'construire'
DOCS = 'docs/agent'


def lire_json(p, defaut=None):
    try:
        return json.loads(pathlib.Path(p).read_text(encoding='utf-8'))
    except Exception:
        return defaut


def tmux_vivant(sess):
    if not sess:
        return False
    try:
        return subprocess.call(['tmux', 'has-session', '-t', str(sess)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
    except Exception:
        return False


def dossier_etat(ws):
    """Le dossier d'état du moteur pour cette run, SANS le créer (socle.dossier_run fait mkdir)."""
    nom = pathlib.Path(ws).name
    if socle.run_confinee(ws):
        return socle.racine_runs_mesure() / 'state' / WF / nom
    return socle.dossier_state() / WF / nom


def tours_retours(ws):
    d = pathlib.Path(ws) / DOCS / 'retours'
    out = []
    for f in (sorted(d.glob('tour-*.json')) if d.is_dir() else []):
        m = re.fullmatch(r'tour-(\d+)\.json', f.name)
        if m:
            out.append((int(m.group(1)), lire_json(f, {}) or {}))
    return sorted(out, key=lambda x: x[0])


def etat(ws):
    ws = pathlib.Path(ws).resolve()
    if not (ws / 'WORKSPACE.txt').is_file():
        return {'indisponible': f'workspace introuvable : {ws}'}
    d = ws / DOCS
    noeud = lire_json(dossier_etat(ws) / f'{NOEUD}.json', {}) or {}
    passages = noeud.get('passages') or []
    lanceur = lire_json(ws / 'state' / 'lanceur.json', {}) or {}
    av = lire_json(d / 'avancement.json') or {}
    retours = tours_retours(ws)
    a_traiter = [n for n, j in retours if j.get('statut') == 'a-traiter']
    rv = (lire_json(d / 'revue.json', {}) or {}).get('tours') or []

    paliers = [{'n': p.get('n'), 'titre': p.get('titre') or '', 'statut': p.get('statut') or 'a-faire',
                'commandes': len(p.get('commandes') or []), 'test': len(p.get('test') or [])}
               for p in ((lire_json(d / 'paliers.json', {}) or {}).get('paliers') or []) if isinstance(p, dict)]
    courant = next((p for p in sorted(paliers, key=lambda x: x['n'] if isinstance(x['n'], int) else 10 ** 6)
                    if p['statut'] != 'production'), None)

    versions = [v for v in ((lire_json(d / 'versions.json', {}) or {}).get('versions') or []) if isinstance(v, dict)]
    prev = next((v for v in reversed(versions) if v.get('statut') == 'preversion'), None)
    prods = [x for x in ((lire_json(d / 'production.json', {}) or {}).get('productions') or []) if isinstance(x, dict)]

    verification = None
    if courant:
        ver = lire_json(d / 'paliers' / f"p{courant['n']}" / 'verification.json')
        if isinstance(ver, dict):
            res = [x for x in (ver.get('resultats') or []) if isinstance(x, dict)]
            verification = {'verdict': ver.get('verdict'), 'reussite': ver.get('reussite'),
                            'actions_a_tort': ver.get('actions_a_tort'), 'rejouees': len(res),
                            'version': ver.get('version'), 'date': ver.get('date')}

    phase = av.get('phase')
    if a_traiter:
        phase = 'retours'
    elif courant is None:
        phase = 'fini' if paliers else None
    elif phase is None:
        phase = 'preversion' if courant['statut'] == 'preversion' else 'palier'

    lanceur_vivant = lanceur.get('statut') == 'en-cours' and tmux_vivant(lanceur.get('tmux'))
    dernier = passages[-1] if passages else {}
    agent_vivant = bool(dernier) and not dernier.get('ended') and tmux_vivant(dernier.get('session') or noeud.get('tmux'))
    en_cours = bool(lanceur_vivant or agent_vivant)

    bloque = None
    if not en_cours:
        if lanceur.get('statut') == 'bloque':
            bloque = lanceur.get('raison') or 'bloqué (sans raison écrite)'
        elif lanceur.get('statut') == 'en-cours':
            bloque = "le lanceur s'est arrêté sans conclure — relancer"
        elif av.get('bloque'):
            bloque = str(av['bloque'])
        elif noeud.get('statut') == 'bloque-entree':
            bloque = 'livrables amont manquants : ' + ', '.join(map(str, (noeud.get('manques_amont') or [])[:6]))
        elif noeud.get('statut') == 'panne' and noeud.get('rc') != 0:
            cause = ((dernier.get('panne') or {}).get('cause')) or '; '.join(map(str, (noeud.get('erreurs') or [])[:2]))
            bloque = f'panne du moteur : {cause or "inconnue"}'

    derniere_passe = None
    if dernier:
        derniere_passe = {
            'n': dernier.get('n'), 'debut': dernier.get('started'), 'fin': dernier.get('ended'),
            'duree_s': dernier.get('duree_s'), 'verdict': dernier.get('verdict'),
            'comment': dernier.get('fin'), 'compte': dernier.get('compte'), 'modele': dernier.get('modele'),
            'erreurs': (dernier.get('erreurs') or [])[:5], 'panne': (dernier.get('panne') or {}).get('cause'),
        }

    return {
        'run': ws.name, 'workspace': str(ws),
        'en_cours': en_cours, 'phase': phase, 'tour': len(rv),
        'palier_courant': (courant or {}).get('n'), 'paliers': paliers,
        'preversion': prev, 'production': prods[-1] if prods else None,
        'verification': verification, 'bloque': bloque,
        'derniere_passe': derniere_passe, 'passes': len(passages),
        'retours_a_traiter': a_traiter,
        'revue': {'tours': len(rv), 'dernier': rv[-1] if rv else None},
        'lanceur': ({k: lanceur.get(k) for k in ('statut', 'mode', 'palier', 'tmux', 'debut', 'fin', 'plafond', 'raison', 'moteur')}
                    | {'passes': len(lanceur.get('passes') or [])}) if lanceur else None,
    }


def main(argv):
    if len(argv) != 2 or argv[1].startswith('-'):
        print(json.dumps({'indisponible': 'usage : agent-etat.py <workspace>'}, ensure_ascii=False))
        return 2
    try:
        r = etat(argv[1])
    except Exception as exc:  # le module ne doit jamais recevoir autre chose qu'une ligne JSON
        r = {'indisponible': f'{type(exc).__name__}: {exc}'}
    print(json.dumps(r, ensure_ascii=False))
    return 0 if 'indisponible' not in r else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
