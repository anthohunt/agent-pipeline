"""
Validateur agent — REVUE (étape 3 : l'utilisateur essaie la préversion dans son outil).

Le verdict de l'utilisateur est la seule entrée humaine de l'étape : il se garde mot
pour mot. « Bon » met le palier en production et décide la suite ; des retours
deviennent des points qu'un vérificateur peut constater dans l'outil.

Contrats :
1. `revue.json` est au contrat : tours numérotés 1, 2, 3… dans l'ordre, chacun avec
   `palier`, `version`, `verdict` good|retours, `date` ISO et `citation` non vide.
2. Chaque tour juge une version qui existe : `versions.json` porte la version citée,
   du même palier, livrée au tour précédent.
3. Un tour `retours` a son `retours/tour-<N>.json` et son `.md` : `tour` = N, le même
   palier, statut a-traiter|traite, au moins un retour, chacun avec `id` unique, `dit`
   (mots exacts) et `attendu` (vérifiable) non vides.
4. Un tour `good` n'a pas de fichier de retours, porte `suite` palier-suivant|arret,
   et son palier est en production : `production.json` le nomme avec sa version et sa
   fiche, `paliers.json` le met au statut `production`.
5. Après un `good` + `palier-suivant`, `paliers.json` porte le palier suivant avec un
   test non vide fait de consignes réelles. Après un `good` + `arret`, plus aucun tour.
"""
import importlib.util, pathlib, re

_spec = importlib.util.spec_from_file_location('agent_commun', pathlib.Path(__file__).parent / 'agent_commun.py')
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

VERDICTS = ('good', 'retours')
SUITES = ('palier-suivant', 'arret')


def validate(workspace):
    errs = []
    ws = pathlib.Path(workspace)
    d = ws / C.DOCS
    rj, e = C.lire_json(d / 'revue.json')
    if rj is None:
        return [f"C1: `{C.DOCS}/revue.json` {e} — aucun verdict de l'utilisateur n'est enregistré"]
    tours = rj.get('tours') if isinstance(rj, dict) else None
    if not isinstance(tours, list) or not tours:
        return ["C1: `revue.json` doit porter `{\"tours\": [ … ]}` avec au moins un tour"]

    versions = C.versions(ws)
    pal = {p.get('n'): p for p in C.paliers(ws)}
    reelles = C.consignes(ws)
    prod, _ = C.lire_json(d / 'production.json')
    prods = [x for x in ((prod or {}).get('productions') or []) if isinstance(x, dict)] if isinstance(prod, dict) else []

    for i, t in enumerate(tours, 1):
        if not isinstance(t, dict):
            errs.append(f"C1: tour n°{i} n'est pas un objet")
            continue
        if t.get('tour') != i:
            errs.append(f"C1: le tour en position {i} porte `tour: {t.get('tour')!r}` (attendu {i})")
        if t.get('verdict') not in VERDICTS:
            errs.append(f"C1: tour {i} : verdict `{t.get('verdict')}` hors de {list(VERDICTS)}")
        if not re.match(r'\d{4}-\d{2}-\d{2}', str(t.get('date') or '')):
            errs.append(f"C1: tour {i} : `date` ISO absente")
        if not C.non_vide(t.get('citation')):
            errs.append(f"C1: tour {i} : `citation` vide — le verdict se garde avec les mots exacts")
        n = t.get('palier')
        if not isinstance(n, int):
            errs.append(f"C1: tour {i} : `palier` absent")
            continue
        v = next((x for x in versions if x.get('version') == t.get('version')), None)
        if v is None:
            errs.append(f"C2: tour {i} juge la version `{t.get('version')}`, absente de `versions.json`")
        elif v.get('palier') != n or v.get('tour') != i - 1:
            errs.append(f"C2: tour {i} : la version {t.get('version')} est du palier {v.get('palier')} au tour "
                        f"{v.get('tour')} (attendu palier {n}, tour {i - 1})")

        rjf = d / 'retours' / f'tour-{i}.json'
        rmf = d / 'retours' / f'tour-{i}.md'
        if t.get('verdict') == 'retours':
            if not rjf.exists():
                errs.append(f"C3: tour {i} à retours sans `retours/tour-{i}.json` — la construction n'a rien à traiter")
                continue
            if not rmf.exists() or rmf.stat().st_size == 0:
                errs.append(f"C3: `retours/tour-{i}.md` absent/vide")
            r, re_ = C.lire_json(rjf)
            if not isinstance(r, dict):
                errs.append(f"C3: `retours/tour-{i}.json` illisible ({re_ or 'pas un objet'})")
                continue
            if r.get('tour') != i or r.get('palier') != n:
                errs.append(f"C3: `retours/tour-{i}.json` porte tour {r.get('tour')!r}, palier {r.get('palier')!r}")
            if r.get('statut') not in ('a-traiter', 'traite'):
                errs.append(f"C3: `retours/tour-{i}.json` statut `{r.get('statut')}` hors de ['a-traiter', 'traite']")
            lst = r.get('retours')
            if not isinstance(lst, list) or not lst:
                errs.append(f"C3: `retours/tour-{i}.json` ne porte aucun retour")
                continue
            vus = set()
            for x in lst:
                if not isinstance(x, dict):
                    errs.append(f"C3: tour {i} : un retour n'est pas un objet")
                    continue
                rid = x.get('id') or '?'
                if rid in vus:
                    errs.append(f"C3: tour {i} : id de retour en double {rid}")
                vus.add(rid)
                for k in ('id', 'dit', 'attendu'):
                    if not C.non_vide(x.get(k)):
                        errs.append(f"C3: tour {i} retour {rid} : `{k}` vide")
            continue

        if t.get('verdict') != 'good':
            continue
        if rjf.exists():
            errs.append(f"C4: tour {i} `good` avec un `retours/tour-{i}.json` — l'un des deux ment")
        if t.get('suite') not in SUITES:
            errs.append(f"C4: tour {i} `good` sans `suite` parmi {list(SUITES)}")
        pr = next((x for x in prods if x.get('palier') == n and x.get('version') == t.get('version')), None)
        if pr is None:
            errs.append(f"C4: tour {i} `good` mais `production.json` ne nomme pas le palier {n} en version {t.get('version')}")
        elif not (ws / str(pr.get('fiche') or '')).is_file():
            errs.append(f"C4: production du palier {n} : la fiche `{pr.get('fiche')}` est introuvable")
        if (pal.get(n) or {}).get('statut') != 'production':
            errs.append(f"C4: palier {n} validé mais pas au statut `production` dans `paliers.json`")
        if t.get('suite') == 'arret' and i != len(tours):
            errs.append(f"C5: tour {i} clôt la run (`arret`) mais d'autres tours suivent")
        if t.get('suite') == 'palier-suivant':
            s = pal.get(n + 1)
            if s is None:
                errs.append(f"C5: suite `palier-suivant` mais `paliers.json` ne porte pas le palier {n + 1}")
            else:
                test = [str(x) for x in (s.get('test') or [])]
                if not test:
                    errs.append(f"C5: palier {n + 1} sans `test`")
                inconnus = [x for x in test if x not in reelles]
                if inconnus:
                    errs.append(f"C5: test du palier {n + 1} hors des consignes réelles : " + ', '.join(inconnus[:10]))
    return errs
