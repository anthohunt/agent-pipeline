#!/usr/bin/env python3
"""Programme du module « agent » : l'état d'une run de la pipeline agent en 3 étapes (concevoir, construire un
palier, revue).

Contrat des fichiers et des commandes : docs/contrat.md ; graphe : workflows/agent.json (à la racine du dépôt) ;
parcours : programme/parcours.json. Le mod (hooks/) dessine ; ce programme tient l'état,
dans les fichiers de la run sur le serveur, et parle au moteur flux (gate de l'étape 1, lancement et suivi de l'étape 2,
gate de la revue).

Une commande par geste : `agent.py <commande>`, paramètres en JSON sur l'entrée standard, réponse en JSON sur la
dernière ligne de la sortie : {"ok": true, "resultat": …} ou {"ok": false, "refus": "…"}.

Bibliothèque standard seule. Tests : python3 -m unittest discover -s programme/tests
"""
import datetime
import json
import os
import pathlib
import re
import subprocess
import sys

ICI = pathlib.Path(__file__).resolve().parent
DEPOT = ICI.parent.parent    # racine du dépôt agent-pipeline
GRAPHES = pathlib.Path(os.environ.get('AGENT_GRAPHES') or DEPOT / 'workflows')


def _racine_runs():
    """Les runs : AGENT_RUNS, sinon le `workspace_root` du graphe (comme le moteur), sinon ~/agent-runs."""
    if os.environ.get('AGENT_RUNS'):
        return pathlib.Path(os.environ['AGENT_RUNS'])
    try:
        r = json.loads((GRAPHES / 'agent.json').read_text(encoding='utf-8')).get('workspace_root')
    except Exception:
        r = None
    return pathlib.Path(os.path.expandvars(os.path.expanduser(r or '~/agent-runs')))


RUNS = _racine_runs()
# Le moteur flux (dépendance) : FLUX_HOME, sinon le clone conseillé par le README (vendor/flux).
FLUX = pathlib.Path(os.environ.get('FLUX_HOME') or os.environ.get('AGENT_FLUX') or DEPOT / 'vendor' / 'flux')
# Les outils de la pipeline vivent dans ce dépôt ; les tests les remplacent par des faux.
OUTILS = pathlib.Path(os.environ.get('AGENT_OUTILS') or DEPOT / 'tools')
# Le dossier d'état du moteur (FLUX_STATE_DIR, comme socle.dossier_state()).
ETAT_FLUX = pathlib.Path(os.environ.get('FLUX_STATE_DIR') or FLUX / 'state')
WORKFLOW = 'agent'
DOCS = 'docs/agent'
ETAT_MODULE = 'state/module-agent.json'
JOURNAL = 'state/module-agent.jsonl'
LIRE_MAX = 200_000
AVANCABLES = ('E1.2', 'E1.3', 'E1.4', 'E1.5')
SUITES = ('palier-suivant', 'arret')

# Ce qui attend l'utilisateur quand une question de l'étape 1 est en cours (libellés courts du volet et de la bande).
QUESTIONS = {
    'E1.1': 'le besoin : ce que l’agent doit savoir faire, avec tes mots',
    'E1.2': 'donner l’accès à l’outil',
    'E1.3': 'tes consignes réelles',
    'E1.4': 'la limite de la machine',
    'E1.5': 'ce qui rend un palier prêt',
}


class Refus(Exception):
    pass


# ───────────────────────────────────────── fichiers

def maintenant():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def charger_json(chemin, defaut=None):
    try:
        return json.loads(pathlib.Path(chemin).read_text(encoding='utf-8'))
    except Exception:
        return defaut


def ecrire_atomique(chemin, texte):
    chemin = pathlib.Path(chemin)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    tmp = chemin.with_name(chemin.name + '.tmp')
    tmp.write_text(texte, encoding='utf-8')
    os.replace(tmp, chemin)


def ecrire_json(chemin, valeur):
    ecrire_atomique(chemin, json.dumps(valeur, ensure_ascii=False, indent=2) + '\n')


def journaliser(ws, type_, donnees=None):
    p = pathlib.Path(ws) / JOURNAL
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'a', encoding='utf-8') as f:
        f.write(json.dumps({'a': maintenant(), 'type': type_, **(donnees or {})}, ensure_ascii=False) + '\n')


def parcours():
    return json.loads((ICI / 'parcours.json').read_text(encoding='utf-8'))


def toutes_sous_etapes(p=None):
    p = p or parcours()
    return [s for e in p['etapes'] for s in e['sous_etapes']]


def sous_etape(sid):
    for s in toutes_sous_etapes():
        if s['id'] == sid:
            return s
    raise Refus(f'sous-étape inconnue : {sid}')


def ordre_e1():
    return [x['id'] for x in toutes_sous_etapes() if x['id'].startswith('E1.')]


# ───────────────────────────────────────── runs

def slug(texte):
    s = re.sub(r'[^a-z0-9-]+', '-', str(texte or '').lower()).strip('-')
    return s[:40]


def lire_entete(ws):
    """WORKSPACE.txt : « clé: valeur » par ligne (écrit par flux/runtime/new-run.py)."""
    vals = {}
    try:
        for l in (pathlib.Path(ws) / 'WORKSPACE.txt').read_text(encoding='utf-8').splitlines():
            if ':' in l:
                k, v = l.split(':', 1)
                vals[k.strip()] = v.strip()
    except Exception:
        pass
    return vals


def runs_du_projet(projet):
    if not RUNS.is_dir():
        return []
    trouves = []
    for d in RUNS.iterdir():
        if not d.is_dir() or d.name.startswith('_'):
            continue
        ent = lire_entete(d)
        if ent.get('workflow', WORKFLOW) == WORKFLOW and slug(ent.get('projet')) == projet:
            trouves.append((ent.get('ouvert', ''), d))
    return [d for _, d in sorted(trouves)]


def workspace(run):
    if not run or '/' in str(run) or str(run).startswith('.'):
        raise Refus(f'run invalide : {run!r}')
    ws = RUNS / run
    if not (ws / 'WORKSPACE.txt').exists():
        raise Refus(f'run introuvable : {run}')
    return ws


def graphe():
    return charger_json(GRAPHES / f'{WORKFLOW}.json', {}) or {}


def creer_run(projet):
    # new-run.py crée la run sous le workspace_root du graphe, sans autre choix : si AGENT_RUNS pointe ailleurs
    # (essai, test), la run naîtrait là où le module ne la cherche pas — et chez la production. On refuse avant.
    racine = graphe().get('workspace_root')
    if racine and pathlib.Path(racine).resolve() != RUNS.resolve():
        raise Refus(f'le graphe crée ses runs sous {racine}, pas sous {RUNS} (AGENT_RUNS) : création refusée')
    r = subprocess.run([sys.executable, str(FLUX / 'runtime' / 'new-run.py'), WORKFLOW, projet],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise Refus(f'création de la run refusée par le moteur : {(r.stderr or r.stdout).strip()[-400:]}')
    runs = runs_du_projet(projet)
    if not runs:
        raise Refus('la run a été créée mais reste introuvable (WORKSPACE.txt sans « projet: »)')
    return runs[-1]


def noeud(n):
    """L'identifiant du nœud n du graphe (concevoir, construire, revue) : lu dans le graphe, jamais supposé."""
    for nd in graphe().get('nodes') or []:
        if nd.get('n') == n:
            return nd['id']
    return {1: 'concevoir', 2: 'construire', 3: 'revue'}[n]


def etat_noeud_flux(ws, nid):
    return charger_json(ETAT_FLUX / WORKFLOW / pathlib.Path(ws).name / f'{nid}.json', {}) or {}


def run_node(ws, nid, timeout):
    """Le gate d'un nœud par le moteur : (vert, état du nœud, sortie d'erreur)."""
    r = subprocess.run([sys.executable, str(FLUX / 'runtime' / 'run-node.py'), WORKFLOW, nid, '--workspace', str(ws)],
                       capture_output=True, text=True, timeout=timeout)
    st = etat_noeud_flux(ws, nid)
    return r.returncode == 0 and st.get('statut') == 'vert', st, r


def detail_rouge(st, r):
    erreurs = st.get('erreurs') or []
    manques = st.get('livrables_manquants') or []
    detail = '; '.join([str(x) for x in erreurs][:12] + [f'manquant : {m}' for m in manques][:12])
    return detail or (r.stderr or '').strip()[-600:]


# ───────────────────────────────────────── état du module

def etat_module(ws):
    e = charger_json(pathlib.Path(ws) / ETAT_MODULE)
    if e:
        return e
    p = parcours()
    e = {
        'projet': lire_entete(ws).get('projet'),
        'cree': maintenant(),
        'sous_etapes': {s['id']: {'etat': 'a_faire'} for s in toutes_sous_etapes(p)},
        'decisions': [],
        'sessions': [],
        'lance_le': None,
        'lancements': [],
        'close': False,
    }
    e['sous_etapes']['E1.1'] = {'etat': 'en_cours', 'depuis': maintenant()}
    return e


def sauver(ws, e):
    ecrire_json(pathlib.Path(ws) / ETAT_MODULE, e)


def construction(ws):
    """Le suivi de l'étape 2, par le moteur (tools/agent-etat.py, contrat). Jamais d'exception."""
    outil = OUTILS / 'agent-etat.py'
    if not outil.exists():
        return {'indisponible': 'tools/agent-etat.py absent'}
    try:
        r = subprocess.run([sys.executable, str(outil), str(ws)], capture_output=True, text=True, timeout=25)
        ligne = (r.stdout or '').strip().splitlines()[-1] if (r.stdout or '').strip() else ''
        return json.loads(ligne) if ligne else {'indisponible': (r.stderr or '').strip()[-300:] or 'réponse vide'}
    except Exception as exc:
        return {'indisponible': str(exc)[:300]}


def revue_json(ws):
    j = charger_json(pathlib.Path(ws) / DOCS / 'revue.json', {}) or {}
    return j if isinstance(j.get('tours'), list) else {'tours': []}


def run_close(ws, e):
    """Close : le module l'a close, ou le dernier tour de revue est « good » avec la suite « arret »."""
    if e.get('close'):
        return True
    tours = revue_json(ws)['tours']
    d = tours[-1] if tours and isinstance(tours[-1], dict) else {}
    return d.get('verdict') == 'good' and d.get('suite') == 'arret'


def paliers_json(ws):
    j = charger_json(pathlib.Path(ws) / DOCS / 'paliers.json', {}) or {}
    return [p for p in (j.get('paliers') or []) if isinstance(p, dict)]


def version_du_tour(ws, tours):
    """La version livrée pendant ce tour (versions.json : `tour` = tours de revue passés), quel que soit son statut :
    pendant la revue, l'agent la passe en production AVANT d'appeler `revue`, et elle reste celle qu'on juge."""
    vs = (charger_json(pathlib.Path(ws) / DOCS / 'versions.json', {}) or {}).get('versions') or []
    for v in reversed([v for v in vs if isinstance(v, dict)]):
        try:
            if int(v.get('tour') or 0) == tours:
                return v
        except (TypeError, ValueError):
            continue
    return None


def livree(ws, c, tours):
    """La préversion de ce tour est livrée et rien ne tourne : place à l'essai de l'utilisateur."""
    if not c or c.get('indisponible') or c.get('en_cours') or c.get('retours_a_traiter'):
        return None
    v = version_du_tour(ws, tours)
    if not v:
        return None
    p = next((x for x in paliers_json(ws) if x.get('n') == v.get('palier')), None)
    return v if p and p.get('statut') in ('preversion', 'production') else None


def vue(ws, e=None, c=None):
    ws = pathlib.Path(ws)
    e = e or etat_module(ws)
    p = parcours()
    lance = bool(e.get('lance_le'))
    if c is None:
        c = construction(ws) if lance else None
    tours = revue_json(ws)['tours']
    n_tours = len(tours)
    close = run_close(ws, e)
    v_livree = livree(ws, c, n_tours) if lance and not close else None
    decisions = e.get('decisions', [])
    cc = c or {}
    palier_construit = cc.get('palier_courant')
    bloque = cc.get('bloque') if not cc.get('en_cours') else None

    def donnees_pretes(n):
        d = ws / DOCS / 'paliers' / f'p{n}'
        return bool(n) and (d / 'donnees' / 'entrainement.jsonl').is_file() and (d / 'journal.md').is_file()

    def etats_e2():
        if not lance:
            return {'E2.1': 'a_faire', 'E2.2': 'a_faire'}
        if close or v_livree or (cc.get('phase') == 'fini' and not cc.get('en_cours')):
            return {'E2.1': 'validee', 'E2.2': 'validee'}
        e21 = 'validee' if cc.get('phase') != 'retours' and donnees_pretes(palier_construit) else 'en_cours'
        e22 = 'en_cours' if e21 == 'validee' else 'a_faire'
        if bloque:
            if e21 == 'en_cours':
                e21 = 'bloquee'
            else:
                e22 = 'bloquee'
        return {'E2.1': e21, 'E2.2': e22}

    e2 = etats_e2()

    def etat_derive(sid):
        if sid in e2:
            return {'etat': e2[sid]}
        if sid == 'E3.1':
            if close:
                return {'etat': 'validee', 'citation': (tours[-1] if tours else {}).get('citation')}
            return {'etat': 'en_cours' if v_livree else 'a_faire'}
        return e['sous_etapes'].get(sid, {'etat': 'a_faire'})

    etapes = []
    for et in p['etapes']:
        sous = []
        for s in et['sous_etapes']:
            d = etat_derive(s['id'])
            sous.append({
                'id': s['id'], 'titre': s['titre'], 'qui': s['qui'], 'etat': d.get('etat', 'a_faire'),
                'depuis': d.get('depuis'), 'valide_le': d.get('valide_le'), 'citation': d.get('citation'),
                'sorties': [{'chemin': x, 'existe': (ws / x).exists()} for x in s.get('sortie', [])],
                'decisions': [x for x in decisions if x.get('sous_etape') == s['id']],
            })
        faite = all(x['etat'] == 'validee' for x in sous)
        etapes.append({'n': et['n'], 'titre': et['titre'], 'resume': et['resume'], 'sous_etapes': sous,
                       'etat': 'faite' if faite else 'ouverte'})
    for et in etapes:
        if et['etat'] == 'ouverte' and not any(x['etat'] != 'a_faire' for x in et['sous_etapes']):
            et['etat'] = 'fermee'
    courante = next((et['n'] for et in etapes if et['etat'] != 'faite'), 3)

    # Le palier dont on parle : celui qu'on essaie pendant la revue, sinon celui qu'on construit.
    palier = (v_livree or {}).get('palier') or palier_construit
    acces = charger_json(ws / DOCS / 'acces-outil.json', {}) or {}
    fiche = f'{DOCS}/paliers/p{palier}/fiche.md' if palier else None
    liens = {
        'outil': acces.get('url') if isinstance(acces, dict) else None,
        'preversion': (v_livree or {}).get('emplacement') or (cc.get('preversion') or {}).get('emplacement'),
        'fiche': fiche if fiche and (ws / fiche).is_file() else None,
    }
    v = {
        'run': ws.name, 'projet': e.get('projet'), 'workspace': str(ws), 'etape_courante': courante,
        'etapes': etapes, 'liens': liens, 'construction': c, 'tour': n_tours, 'tours': tours,
        'close': close, 'lance_le': e.get('lance_le'), 'palier': palier,
        'version': (v_livree or {}).get('version'),
        'relance_refusee': e.get('relance_refusee'),
    }
    v['regles'] = p['regles_communes']
    v['attend'] = ce_qui_attend(v)
    en = next((s for et in etapes for s in et['sous_etapes'] if s['etat'] in ('en_cours', 'a_valider', 'bloquee')), None)
    v['sous_etape_courante'] = en['id'] if en else None
    v['consigne'] = sous_etape(en['id'])['consigne'] if en else None
    n1 = noeud(1)
    d1 = ETAT_FLUX / WORKFLOW / ws.name / n1
    v['brief'] = {'noeud': n1, 'sys': str(d1 / 'sys.md'), 'brief': str(d1 / 'brief.md')}
    return v


def ce_qui_attend(v):
    if v['close']:
        return None
    toutes = [s for et in v['etapes'] for s in et['sous_etapes']]
    for s in toutes:
        if s['id'].startswith('E1'):
            if s['etat'] == 'a_valider':
                return {'quoi': f'valider {s["titre"][0].lower() + s["titre"][1:]}', 'sous_etape': s['id']}
            if s['etat'] == 'en_cours':
                q = QUESTIONS.get(s['id'])
                return {'quoi': q, 'sous_etape': s['id']} if q else None
            if s['etat'] == 'a_faire':
                return None
    if not v['lance_le']:
        return {'quoi': 'lancer la construction', 'action': 'lancer'}
    c = v['construction'] or {}
    if c.get('en_cours'):
        return None
    if c.get('bloque'):
        return {'quoi': f'construction bloquée : {c["bloque"]}', 'action': 'lancer'}
    if v.get('relance_refusee'):
        return {'quoi': f'relancer la construction ({v["relance_refusee"].get("raison", "")})', 'action': 'lancer'}
    e31 = next(s for s in toutes if s['id'] == 'E3.1')
    if e31['etat'] == 'en_cours':
        return {'quoi': f'essayer la préversion du palier {v["palier"]}', 'sous_etape': 'E3.1'}
    return None


# ───────────────────────────────────────── commandes

def cmd_liste(a):
    out = []
    if RUNS.is_dir():
        for d in sorted(RUNS.iterdir()):
            ent = lire_entete(d)
            if d.is_dir() and not d.name.startswith('_') and ent.get('workflow', WORKFLOW) == WORKFLOW:
                out.append({'run': d.name, 'projet': ent.get('projet'), 'ouvert': ent.get('ouvert'),
                            'module': (d / ETAT_MODULE).exists()})
    return {'runs': out}


def cmd_ouvrir(a):
    projet = slug(a.get('projet'))
    if not projet:
        raise Refus('nom de projet invalide')
    runs = runs_du_projet(projet)
    neuf = not runs
    ws = creer_run(projet) if neuf else runs[-1]
    e = etat_module(ws)
    if not (ws / ETAT_MODULE).exists():
        neuf = True
    sess = a.get('session')
    if sess and sess not in e['sessions']:
        e['sessions'].append(sess)
    sauver(ws, e)
    journaliser(ws, 'ouverture', {'session': sess, 'neuf': neuf})
    preparer_brief(ws)
    v = vue(ws, e)
    v['neuf'] = neuf
    return v


def preparer_brief(ws):
    """Le brief du nœud 1 (objectif, check-list, consignes du graphe) écrit par le moteur, que l'agent lit."""
    try:
        subprocess.run([sys.executable, str(FLUX / 'runtime' / 'run-node.py'), WORKFLOW, noeud(1),
                        '--workspace', str(ws), '--brief-only'], capture_output=True, text=True, timeout=60)
    except Exception:
        pass


def cmd_etat(a):
    return vue(workspace(a.get('run')))


def exiger_citation(a):
    c = str(a.get('citation') or '').strip()
    if not c:
        raise Refus("citation obligatoire : les mots de l'utilisateur, mot pour mot")
    return c


def cmd_besoin(a):
    """E1.1 : le premier message de l'utilisateur après l'ouverture est le besoin ; il se garde mot pour mot."""
    ws = workspace(a.get('run'))
    e = etat_module(ws)
    if e['sous_etapes']['E1.1']['etat'] != 'en_cours':
        return {'deja': True}
    texte = exiger_citation(a)
    cite = f'Reçu le {maintenant()}, mot pour mot :\n\n> ' + texte.replace('\n', '\n> ') + '\n'
    f = ws / DOCS / 'besoin.md'
    try:
        avant = f.read_text(encoding='utf-8')
    except OSError:
        avant = ''
    if avant.strip():
        # Une run préparée d'avance a déjà son besoin.md : la citation se met en tête, le reste se garde.
        section = '## Le besoin, mot pour mot\n\n' + cite + '\n'
        lignes = avant.split('\n')
        if lignes[0].startswith('# '):
            reste = '\n'.join(lignes[1:]).lstrip('\n')
            nouveau = lignes[0] + '\n\n' + section + reste
        else:
            nouveau = section + avant
    else:
        nouveau = '# Le besoin\n\n' + cite
    ecrire_atomique(f, nouveau)
    e['sous_etapes']['E1.1'] = {'etat': 'validee', 'valide_le': maintenant(), 'citation': texte}
    e['sous_etapes']['E1.2'] = {'etat': 'en_cours', 'depuis': maintenant()}
    sauver(ws, e)
    journaliser(ws, 'besoin', {'citation': texte, 'garde': bool(avant.strip())})
    return {'sous_etape': 'E1.1', 'etat': 'validee', 'fichier': f'{DOCS}/besoin.md'}


def cmd_avancer(a):
    ws = workspace(a.get('run'))
    sid = a.get('sous_etape')
    s = sous_etape(sid)
    if sid not in AVANCABLES:
        if sid == 'E1.6':
            raise Refus('E1.6 ne s’avance pas à la main : outil `cloturer`')
        raise Refus(f'{sid} ne s’avance pas à la main : ' + ('le premier message de l’utilisateur la valide' if sid == 'E1.1'
                                                             else 'le programme la constate'))
    cible = a.get('etat')
    if cible not in ('en_cours', 'a_valider', 'validee'):
        raise Refus('etat attendu : en_cours, a_valider ou validee')
    e = etat_module(ws)
    if run_close(ws, e):
        raise Refus('la run est close')
    ordre = ordre_e1()
    i = ordre.index(sid)
    if e['sous_etapes'][ordre[i - 1]]['etat'] != 'validee':
        raise Refus(f'{ordre[i - 1]} n’est pas encore validée')
    manquants = [x for x in s.get('sortie', []) if not (ws / x).exists()]
    if cible in ('a_valider', 'validee') and manquants:
        raise Refus('sorties manquantes : ' + ', '.join(manquants))
    se = {'etat': cible, 'depuis': maintenant()}
    if cible == 'validee':
        se['citation'] = exiger_citation(a)
        se['valide_le'] = maintenant()
        if i + 1 < len(ordre) and e['sous_etapes'][ordre[i + 1]]['etat'] == 'a_faire':
            e['sous_etapes'][ordre[i + 1]] = {'etat': 'en_cours', 'depuis': maintenant()}
    e['sous_etapes'][sid] = se
    sauver(ws, e)
    journaliser(ws, 'avancer', {'sous_etape': sid, 'etat': cible, 'citation': se.get('citation')})
    return {'sous_etape': sid, 'etat': cible}


def cmd_decision(a):
    ws = workspace(a.get('run'))
    sid = a.get('sous_etape')
    sous_etape(sid)
    d = {'a': maintenant(), 'sous_etape': sid, 'resume': str(a.get('resume') or '').strip(),
         'citation': exiger_citation(a), 'option': a.get('option')}
    if not d['resume']:
        raise Refus('resume obligatoire')
    e = etat_module(ws)
    e['decisions'].append(d)
    sauver(ws, e)
    journaliser(ws, 'decision', d)
    return {'decision': d}


def cmd_rouvrir(a):
    ws = workspace(a.get('run'))
    sid = a.get('sous_etape')
    if not str(sid).startswith('E1.'):
        raise Refus('seules les sous-étapes de l’étape 1 se rouvrent ; pour un palier livré, passe par la revue')
    sous_etape(sid)
    raison = str(a.get('raison') or '').strip()
    if not raison:
        raise Refus('raison obligatoire')
    e = etat_module(ws)
    if e.get('lance_le'):
        raise Refus('la construction est lancée : les changements passent par la revue (retours)')
    ordre = ordre_e1()
    for x in ordre[ordre.index(sid) + 1:]:
        if e['sous_etapes'][x]['etat'] != 'validee':
            e['sous_etapes'][x] = {'etat': 'a_faire'}
    e['sous_etapes'][sid] = {'etat': 'en_cours', 'depuis': maintenant(), 'rouvert': raison}
    sauver(ws, e)
    journaliser(ws, 'rouvrir', {'sous_etape': sid, 'raison': raison})
    return {'sous_etape': sid, 'etat': 'en_cours'}


def cmd_cloturer(a):
    """Fin de l'étape 1 : le gate du nœud concevoir, par le moteur. Vert → E1.6 validée."""
    ws = workspace(a.get('run'))
    e = etat_module(ws)
    if e['sous_etapes']['E1.5']['etat'] != 'validee':
        raise Refus('ce qui rend un palier prêt (E1.5) n’est pas validé')
    vert, st, r = run_node(ws, noeud(1), 300)
    journaliser(ws, 'cloturer', {'vert': vert, 'rc': r.returncode, 'erreurs': st.get('erreurs')})
    if not vert:
        raise Refus('contrôle de l’étape 1 rouge — ' + detail_rouge(st, r))
    e['sous_etapes']['E1.6'] = {'etat': 'validee', 'valide_le': maintenant(), 'citation': 'gate vert'}
    sauver(ws, e)
    return {'gate': 'vert'}


def cmd_lancer(a):
    ws = workspace(a.get('run'))
    e = etat_module(ws)
    if run_close(ws, e):
        raise Refus('la run est close')
    if e['sous_etapes']['E1.6']['etat'] != 'validee':
        raise Refus('l’étape 1 n’est pas close (outil `cloturer`)')
    outil = OUTILS / 'agent-lancer.py'
    if not outil.exists():
        raise Refus('tools/agent-lancer.py absent')
    argv = [sys.executable, str(outil), str(ws)] + (['--dry-run'] if a.get('dry_run') else [])
    r = subprocess.run(argv, capture_output=True, text=True, timeout=120)
    ligne = (r.stdout or '').strip().splitlines()[-1] if (r.stdout or '').strip() else ''
    try:
        rep = json.loads(ligne)
    except Exception:
        raise Refus(f'lancement illisible (code {r.returncode}) : {(r.stderr or ligne).strip()[-400:]}')
    if not rep.get('ok'):
        raise Refus(f'lancement refusé : {rep.get("refus") or rep.get("message") or rep}')
    if not a.get('dry_run'):
        e['lance_le'] = e.get('lance_le') or maintenant()
        e.setdefault('lancements', []).append({'a': maintenant(), 'mode': rep.get('mode'), 'palier': rep.get('palier'),
                                               'tmux': rep.get('tmux')})
        e.pop('relance_refusee', None)
        sauver(ws, e)
        journaliser(ws, 'lancer', rep)
    return rep


def en_revue(ws):
    """(vue, version livrée) si l'essai de la préversion est en cours, sinon refus."""
    v = vue(ws)
    if next(s for s in v['etapes'][2]['sous_etapes'] if s['id'] == 'E3.1')['etat'] != 'en_cours':
        raise Refus('pas de revue en cours : aucune préversion livrée pour ce tour')
    ver = version_du_tour(ws, v['tour'])
    return v, ver


def cmd_retours(a):
    ws = workspace(a.get('run'))
    v, ver = en_revue(ws)
    liste = a.get('retours') or []
    if not isinstance(liste, list) or not liste:
        raise Refus('retours : une liste non vide')
    n = v['tour'] + 1
    palier = ver.get('palier')
    propres = []
    for i, r in enumerate(liste, 1):
        r = r if isinstance(r, dict) else {}
        dit = str(r.get('dit') or '').strip()
        attendu = str(r.get('attendu') or '').strip()
        if not dit or not attendu:
            raise Refus(f'retour {i} : « dit » (mots exacts) et « attendu » (critère vérifiable) obligatoires')
        consigne = str(r.get('consigne') or '').strip() or None
        propres.append({'id': f'R{i}', 'dit': dit, 'consigne': consigne, 'attendu': attendu})
    citation = exiger_citation(a)
    doc = {'tour': n, 'palier': palier, 'date': maintenant(), 'statut': 'a-traiter', 'citation': citation,
           'retours': propres}
    base = ws / DOCS / 'retours'
    ecrire_json(base / f'tour-{n}.json', doc)
    md = [f'# Retours — tour {n}, palier {palier}', '',
          f'Reçus le {doc["date"]}, sur la version {ver.get("version")} : « {citation} »', '']
    for r in propres:
        md += [f'## {r["id"]}', f'• Dit : « {r["dit"]} »']
        if r['consigne']:
            md.append(f'• Consigne essayée : « {r["consigne"]} »')
        md += [f'• Attendu : {r["attendu"]}', '']
    ecrire_atomique(base / f'tour-{n}.md', '\n'.join(md))
    journaliser(ws, 'retours', {'tour': n, 'palier': palier, 'nombre': len(propres)})
    return {'tour': n, 'palier': palier, 'fichier': f'{DOCS}/retours/tour-{n}.json', 'retours': propres}


def relancer(ws):
    """Relance l'étape 2 après un verdict ; un refus ne défait pas le verdict, il se garde pour le bouton « Relancer »."""
    try:
        return {'relance': cmd_lancer({'run': ws.name})}
    except Refus as r:
        e = etat_module(ws)
        e['relance_refusee'] = {'a': maintenant(), 'raison': str(r)}
        sauver(ws, e)
        journaliser(ws, 'relance-refusee', {'raison': str(r)})
        return {'relance': None, 'relance_refusee': str(r)}


def cmd_revue(a):
    ws = workspace(a.get('run'))
    verdict = a.get('verdict')
    if verdict not in ('good', 'retours'):
        raise Refus('verdict : good ou retours')
    citation = exiger_citation(a)
    suite = a.get('suite') or None
    if verdict == 'good' and suite not in SUITES:
        raise Refus('verdict good : `suite` obligatoire, palier-suivant ou arret')
    if verdict == 'retours':
        suite = None
    v, ver = en_revue(ws)
    n = v['tour'] + 1
    palier, version = ver.get('palier'), ver.get('version')
    d = ws / DOCS
    fichier_retours = d / 'retours' / f'tour-{n}.json'
    if verdict == 'retours' and not fichier_retours.exists():
        raise Refus(f'enregistre d’abord les retours du tour {n} (outil `retours`)')
    if verdict == 'good':
        if fichier_retours.exists():
            raise Refus(f'{DOCS}/retours/tour-{n}.json existe : un tour « good » n’a pas de retours (retire-le ou rends le verdict retours)')
        prods = (charger_json(d / 'production.json', {}) or {}).get('productions') or []
        if not any(isinstance(x, dict) and x.get('palier') == palier and x.get('version') == version for x in prods):
            raise Refus(f'mets d’abord en production : {DOCS}/production.json doit nommer le palier {palier} en version {version}')
        if suite == 'palier-suivant':
            suivant = next((x for x in paliers_json(ws) if x.get('n') == (palier or 0) + 1), None)
            if not suivant or suivant.get('statut') != 'a-faire':
                raise Refus(f'suite palier-suivant : {DOCS}/paliers.json doit porter le palier {(palier or 0) + 1} au statut a-faire')
    rj = revue_json(ws)
    rj['tours'].append({'tour': n, 'palier': palier, 'version': version, 'verdict': verdict, 'date': maintenant(),
                        'citation': citation, 'suite': suite})
    ecrire_json(d / 'revue.json', rj)
    journaliser(ws, 'revue', {'tour': n, 'palier': palier, 'version': version, 'verdict': verdict, 'suite': suite,
                              'citation': citation})
    res = {'tour': n, 'palier': palier, 'version': version, 'verdict': verdict, 'suite': suite}
    if verdict == 'good' and suite == 'arret':
        e = etat_module(ws)
        e['close'] = True
        e['close_le'] = maintenant()
        sauver(ws, e)
        try:
            vert, st, r = run_node(ws, noeud(3), 120)
            res['gate'] = 'vert' if vert else 'rouge'
            if not vert:
                res['erreurs'] = detail_rouge(st, r)
        except Exception as exc:
            res['gate'] = 'rouge'
            res['erreurs'] = str(exc)[:300]
        journaliser(ws, 'close', {'gate': res['gate']})
        res['close'] = True
        return res
    res.update(relancer(ws))
    return res


def cmd_lire(a):
    ws = workspace(a.get('run'))
    rel = str(a.get('chemin') or '')
    p = (ws / rel).resolve()
    if not str(p).startswith(str(ws.resolve()) + os.sep):
        raise Refus('chemin hors de la run')
    if not p.is_file():
        raise Refus(f'fichier absent : {rel}')
    return {'chemin': rel, 'contenu': p.read_text(encoding='utf-8', errors='replace')[:LIRE_MAX]}


def cmd_evenement(a):
    ws = workspace(a.get('run'))
    journaliser(ws, str(a.get('type') or 'evenement'), a.get('donnees') or {})
    return {}


COMMANDES = {
    'liste': cmd_liste, 'ouvrir': cmd_ouvrir, 'etat': cmd_etat, 'besoin': cmd_besoin, 'avancer': cmd_avancer,
    'decision': cmd_decision, 'rouvrir': cmd_rouvrir, 'cloturer': cmd_cloturer, 'lancer': cmd_lancer,
    'retours': cmd_retours, 'revue': cmd_revue, 'lire': cmd_lire, 'evenement': cmd_evenement,
}


def main(argv):
    if len(argv) < 2 or argv[1] not in COMMANDES:
        print(json.dumps({'ok': False, 'refus': 'commande inconnue ; attendu : ' + ', '.join(COMMANDES)}))
        return 2
    try:
        brut = sys.stdin.read() if not sys.stdin.isatty() else ''
        args = json.loads(brut) if brut.strip() else {}
        res = COMMANDES[argv[1]](args)
        print(json.dumps({'ok': True, 'resultat': res}, ensure_ascii=False))
        return 0
    except Refus as r:
        print(json.dumps({'ok': False, 'refus': str(r)}, ensure_ascii=False))
        return 1
    except Exception as exc:
        print(json.dumps({'ok': False, 'refus': f'erreur du programme : {type(exc).__name__}: {exc}'}, ensure_ascii=False))
        return 3


if __name__ == '__main__':
    sys.exit(main(sys.argv))
