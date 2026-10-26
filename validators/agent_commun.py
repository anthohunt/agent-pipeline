"""
Lectures communes aux contrôles de la pipeline agent (contrat :
docs/contrat.md à la racine du dépôt).

Aucun contrat ne vit ici : seulement la façon de lire les fichiers de la run, pour
que les trois validateurs lisent la même chose de la même manière.
"""
import json, pathlib

DOCS = 'docs/agent'
ACTIONS = ('executer', 'proposer', 'rien')
STATUTS_PALIER = ('a-faire', 'en-cours', 'preversion', 'production')


def txt(p):
    try:
        return pathlib.Path(p).read_text(encoding='utf-8', errors='replace')
    except OSError:
        return ''


def lire_json(p):
    """(valeur, erreur) — erreur non nulle si absent ou illisible."""
    p = pathlib.Path(p)
    if not p.exists() or p.stat().st_size == 0:
        return None, 'absent/vide'
    try:
        return json.loads(txt(p)), None
    except json.JSONDecodeError as e:
        return None, f'JSON invalide : {e}'


def lire_jsonl(p):
    """(lignes, erreurs) — chaque ligne non vide doit être un objet JSON."""
    lignes, errs = [], []
    for i, l in enumerate(txt(p).splitlines(), 1):
        if not l.strip():
            continue
        try:
            v = json.loads(l)
        except json.JSONDecodeError as e:
            errs.append(f'ligne {i} : JSON invalide ({e})')
            continue
        if not isinstance(v, dict):
            errs.append(f'ligne {i} : pas un objet')
            continue
        lignes.append(v)
    return lignes, errs


def non_vide(v):
    return isinstance(v, str) and v.strip() != ''


def consignes(ws):
    """{id: consigne} des consignes réelles (les lignes illisibles sont ignorées ici)."""
    lst, _ = lire_jsonl(pathlib.Path(ws) / DOCS / 'consignes-reelles.jsonl')
    return {str(c.get('id')): c for c in lst if c.get('id') is not None}


def critere(ws):
    """(reussite_min, actions_a_tort_max) de reponses.json, ou None."""
    r, _ = lire_json(pathlib.Path(ws) / DOCS / 'reponses.json')
    c = (r or {}).get('critere') if isinstance(r, dict) else None
    if not isinstance(c, dict):
        return None
    rm, am = c.get('reussite_min'), c.get('actions_a_tort_max')
    if not isinstance(rm, (int, float)) or isinstance(rm, bool) or not (0 < rm <= 1):
        return None
    if not isinstance(am, int) or isinstance(am, bool) or am < 0:
        return None
    return float(rm), am


def paliers(ws):
    j, _ = lire_json(pathlib.Path(ws) / DOCS / 'paliers.json')
    lst = (j or {}).get('paliers') if isinstance(j, dict) else None
    return [p for p in lst if isinstance(p, dict)] if isinstance(lst, list) else []


def palier_courant(ws):
    """Le palier en construction ou livré en préversion : le premier qui n'est pas en
    production. None si tous le sont (ou s'il n'y en a pas)."""
    for p in sorted(paliers(ws), key=lambda x: x.get('n') if isinstance(x.get('n'), int) else 10 ** 6):
        if p.get('statut') != 'production':
            return p
    return None


def tours_revue(ws):
    j, _ = lire_json(pathlib.Path(ws) / DOCS / 'revue.json')
    t = (j or {}).get('tours') if isinstance(j, dict) else None
    return [x for x in t if isinstance(x, dict)] if isinstance(t, list) else []


def tours_retours(ws):
    """[(N, json|None, erreur|None)] triés par N."""
    import re
    d = pathlib.Path(ws) / DOCS / 'retours'
    out = []
    for f in (sorted(d.glob('tour-*.json')) if d.is_dir() else []):
        m = re.fullmatch(r'tour-(\d+)\.json', f.name)
        if m:
            j, e = lire_json(f)
            out.append((int(m.group(1)), j, e))
    return sorted(out, key=lambda x: x[0])


def versions(ws):
    j, _ = lire_json(pathlib.Path(ws) / DOCS / 'versions.json')
    v = (j or {}).get('versions') if isinstance(j, dict) else None
    return [x for x in v if isinstance(x, dict)] if isinstance(v, list) else []
