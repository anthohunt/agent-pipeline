"""
Validateur agent — CONSTRUIRE UN PALIER (étape 2, autonome).

Le nœud est relancé tant que ce contrôle est rouge : chaque lancement traite le palier
courant (le premier de `paliers.json` qui n'est pas en production), ou un tour de
retours. Il n'est vert que quand le palier courant est livré en préversion sur un PASS
du vérificateur qui tient au critère de l'utilisateur, et qu'aucun tour de retours
n'attend.

Contrats :
1. `avancement.json` est au contrat (phase, tour, palier_courant, paliers, maj).
2. Il y a un palier courant, et il est en `preversion` dans `paliers.json`.
3. Son test (`paliers/p<N>/test.jsonl`) est exactement le test de `paliers.json`, et
   chaque ligne est recopiée d'une consigne réelle (même `id`, même `texte`) — jamais
   une phrase générée.
4. Ses données d'entraînement existent et ne contiennent aucune phrase du test.
5. `verification.json` : constructeur et vérificateur nommés et différents, rejoué
   dans l'outil réel, un résultat par consigne du test ; la réussite et les actions à
   tort recalculées depuis les résultats concordent avec celles déclarées, et le
   verdict est PASS au critère de `reponses.json`.
6. La vérification est plus récente que les données et que le dernier tour de retours,
   et que WORKSPACE.txt : elle juge ce qui est livré.
7. `fiche.md` porte « Sait faire » et « Ne sait pas encore ».
8. `versions.json` porte une version du palier courant, en préversion, livrée au tour
   courant (le nombre de tours de revue déjà passés).
9. Aucun tour de retours `a-traiter`.
10. `journal.md` du palier existe et nomme le PASS du vérificateur.
"""
import importlib.util, pathlib, re

_spec = importlib.util.spec_from_file_location('agent_commun', pathlib.Path(__file__).parent / 'agent_commun.py')
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

PHASES = ('palier', 'retours', 'preversion')


def _norm(s):
    return re.sub(r'\s+', ' ', str(s or '')).strip().lower()


def validate(workspace):
    errs = []
    ws = pathlib.Path(workspace)
    d = ws / C.DOCS

    av, e = C.lire_json(d / 'avancement.json')
    if not isinstance(av, dict):
        errs.append(f"C1: `{C.DOCS}/avancement.json` {e or 'pas un objet'} — l'avancement n'est pas tenu")
    else:
        if av.get('phase') not in PHASES:
            errs.append(f"C1: avancement : `phase` `{av.get('phase')}` hors de {list(PHASES)}")
        if not isinstance(av.get('tour'), int):
            errs.append("C1: avancement : `tour` entier absent")
        if not isinstance(av.get('paliers'), list):
            errs.append("C1: avancement : `paliers` absent")
        if not re.match(r'\d{4}-\d{2}-\d{2}', str(av.get('maj') or '')):
            errs.append("C1: avancement : `maj` ISO absente")

    p = C.palier_courant(ws)
    if p is None:
        errs.append("C2: aucun palier à construire dans `paliers.json` (tous en production, ou aucun) — "
                    "rien à livrer ; la revue doit ajouter le palier suivant ou clore")
        return errs
    n = p.get('n')
    if p.get('statut') != 'preversion':
        errs.append(f"C2: palier {n} au statut `{p.get('statut')}` — le nœud se relance jusqu'à sa préversion")
    pd = d / 'paliers' / f'p{n}'

    # C3 — le test : de vraies consignes, celles du palier
    reelles = C.consignes(ws)
    test, terrs = C.lire_jsonl(pd / 'test.jsonl')
    for x in terrs[:3]:
        errs.append(f"C3: `paliers/p{n}/test.jsonl` {x}")
    if not test:
        errs.append(f"C3: `paliers/p{n}/test.jsonl` absent ou vide")
    ids_test = [str(t.get('id')) for t in test]
    if test and set(ids_test) != {str(x) for x in (p.get('test') or [])}:
        errs.append(f"C3: le test de `paliers/p{n}/test.jsonl` n'est pas celui de `paliers.json` — "
                    "le test d'un palier ne change pas en cours de construction")
    for t in test:
        tid = str(t.get('id'))
        r = reelles.get(tid)
        if r is None:
            errs.append(f"C3: consigne de test {tid} absente des consignes réelles — une phrase générée ne teste rien")
        elif _norm(t.get('texte')) != _norm(r.get('texte')):
            errs.append(f"C3: consigne de test {tid} : le texte diffère de la consigne réelle")

    # C4 — les données d'entraînement, sans fuite du test
    ent = pd / 'donnees' / 'entrainement.jsonl'
    lignes, _ = C.lire_jsonl(ent)
    if not lignes:
        errs.append(f"C4: `paliers/p{n}/donnees/entrainement.jsonl` absent ou vide — rien n'a été entraîné")
    else:
        textes_test = {_norm(r.get('texte')) for r in (reelles.get(i) for i in ids_test) if r}
        fuites = [x for x in lignes if _norm(x.get('texte') or x.get('consigne')) in textes_test]
        if fuites:
            errs.append(f"C4: {len(fuites)} phrase(s) du test dans les données d'entraînement — le test ne mesure plus rien")

    # C5 — la vérification
    vp = pd / 'verification.json'
    ver, e = C.lire_json(vp)
    crit = C.critere(ws)
    if not isinstance(ver, dict):
        errs.append(f"C5: `paliers/p{n}/verification.json` {e or 'pas un objet'} — aucun vérificateur n'a rejoué le palier")
    else:
        cons, verif = ver.get('constructeur'), ver.get('verificateur')
        if not C.non_vide(cons) or not C.non_vide(verif):
            errs.append("C5: vérification : `constructeur` et `verificateur` doivent être nommés")
        elif _norm(cons) == _norm(verif):
            errs.append("C5: vérification : le vérificateur est le constructeur — celui qui vérifie n'a jamais construit")
        if not re.match(r'\d{4}-\d{2}-\d{2}', str(ver.get('date') or '')):
            errs.append("C5: vérification : `date` ISO absente")
        if not C.non_vide(ver.get('rejoue_dans')):
            errs.append("C5: vérification : `rejoue_dans` vide — les consignes se rejouent dans le vrai outil")
        res = [x for x in (ver.get('resultats') or []) if isinstance(x, dict)]
        vus = {str(x.get('id')) for x in res}
        manque = [i for i in ids_test if i not in vus]
        if manque:
            errs.append("C5: vérification : consignes du test non rejouées : " + ', '.join(manque[:10]))
        if res:
            ok = sum(1 for x in res if x.get('ok') is True)
            tort = sum(1 for x in res if x.get('a_tort') is True)
            reussite = ok / len(res)
            if not isinstance(ver.get('reussite'), (int, float)) or abs(float(ver['reussite']) - reussite) > 1e-6:
                errs.append(f"C5: vérification : réussite déclarée {ver.get('reussite')} ≠ {reussite:.4f} recalculée")
            if ver.get('actions_a_tort') != tort:
                errs.append(f"C5: vérification : actions à tort déclarées {ver.get('actions_a_tort')} ≠ {tort} recomptées")
            if crit is None:
                errs.append("C5: critère illisible dans `reponses.json` — le verdict ne se juge pas")
            else:
                passe = reussite >= crit[0] - 1e-9 and tort <= crit[1]
                attendu = 'PASS' if passe else 'FAIL'
                if ver.get('verdict') != attendu:
                    errs.append(f"C5: vérification : verdict `{ver.get('verdict')}` alors que le critère donne {attendu} "
                                f"(réussite {reussite:.0%} pour {crit[0]:.0%}, {tort} action(s) à tort pour {crit[1]} au plus)")
                elif not passe:
                    errs.append(f"C5: le palier {n} ne tient pas le critère (réussite {reussite:.0%}, {tort} action(s) à tort) "
                                "— il ne part pas en revue")

        # C6 — fraîcheur
        if vp.exists():
            mv = vp.stat().st_mtime
            ref = (ws / 'WORKSPACE.txt').stat().st_mtime if (ws / 'WORKSPACE.txt').exists() else 0
            if mv < ref:
                errs.append("C6: vérification plus ancienne que WORKSPACE.txt — elle vient d'une autre run")
            if ent.exists() and mv < ent.stat().st_mtime:
                errs.append("C6: données d'entraînement modifiées après la vérification — elle ne juge plus ce qui est livré")
            # le tour se compare par sa date d'écriture (champ `date`) : son statut passe à
            # `traite` APRÈS la vérification, ce qui change son mtime sans rien dire.
            dv = str(ver.get('date') or '')
            for tn, tj, _ in C.tours_retours(ws):
                if isinstance(tj, dict) and tj.get('palier') == n and str(tj.get('date') or '') > dv:
                    errs.append(f"C6: le tour de retours {tn} est plus récent que la vérification — les corrections ne sont pas vérifiées")

    # C7 — la fiche
    fiche = C.txt(pd / 'fiche.md')
    if not fiche.strip():
        errs.append(f"C7: `paliers/p{n}/fiche.md` absent/vide — l'utilisateur ne sait pas ce que la version sait faire")
    else:
        if not re.search(r'^#+\s*sait faire', fiche, re.I | re.M):
            errs.append("C7: fiche sans section « Sait faire »")
        if not re.search(r'^#+\s*ne sait pas encore', fiche, re.I | re.M):
            errs.append("C7: fiche sans section « Ne sait pas encore »")

    # C8 — la version livrée au tour courant
    tour = len(C.tours_revue(ws))
    vs = [v for v in C.versions(ws) if v.get('palier') == n and v.get('tour') == tour]
    if not vs:
        errs.append(f"C8: `versions.json` sans version du palier {n} livrée au tour {tour} — rien de neuf à essayer")
    elif vs[-1].get('statut') != 'preversion' or not C.non_vide(vs[-1].get('emplacement')):
        errs.append(f"C8: la version du palier {n} au tour {tour} doit être en `preversion`, avec son `emplacement`")
    noms = [v.get('version') for v in C.versions(ws)]
    if len(noms) != len(set(noms)):
        errs.append("C8: `versions.json` porte deux fois le même nom de version")

    # C9 — aucun tour en attente
    for tn, tj, te in C.tours_retours(ws):
        if not isinstance(tj, dict):
            errs.append(f"C9: `retours/tour-{tn}.json` illisible ({te})")
        elif tj.get('statut') != 'traite':
            errs.append(f"C9: tour de retours {tn} au statut `{tj.get('statut')}` — le nœud repart en mode retours")

    # C10 — le journal
    j = C.txt(pd / 'journal.md')
    if not j.strip():
        errs.append(f"C10: `paliers/p{n}/journal.md` absent/vide — la construction du palier n'est pas tracée")
    elif not re.search(r'v[ée]rificat\w*[\s\S]{0,300}?\bPASS\b', j, re.I):
        errs.append(f"C10: journal du palier {n} sans PASS du vérificateur")
    return errs
