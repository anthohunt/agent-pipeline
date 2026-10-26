"""
Validateur agent — CONCEVOIR (l'étape en conversation, la plus courte possible).

Le nœud fixe le besoin en quatre réponses de l'utilisateur, enregistre ses consignes
réelles et propose le palier 1. Il n'est vert que si la construction peut partir sans
rien demander : un test fait de vraies consignes, un accès à l'outil constaté, un
critère qu'un vérificateur sait appliquer seul.

Contrats :
1. Les livrables sont présents et non vides.
2. `reponses.json` porte les quatre réponses (`besoin`, `acces`, `machine`, `critere`),
   chacune avec la citation exacte de l'utilisateur ; `critere` porte `reussite_min`
   dans ]0, 1] et `actions_a_tort_max` entier ≥ 0 ; `machine` porte au moins une limite.
3. `besoin.md` reprend la citation du besoin mot pour mot.
4. `acces-outil.json` nomme l'outil, une URL http(s), la commande qui rejoue une
   consigne, et un `constate` daté : on a rejoué une consigne pour de vrai.
5. `consignes-reelles.jsonl` : au moins une consigne ; chacune avec un `id` unique, un
   `texte`, un `attendu.action` parmi executer/proposer/rien (et sa `commande` quand il
   faut exécuter), une `source` — jamais une source générée, sauf si l'utilisateur l'a
   décidé : `reponses.json` porte alors `consignes.generees_autorisees: true` et sa citation.
6. `catalogue.json` porte des commandes ; chaque commande attendue par une consigne
   réelle existe au catalogue.
7. `paliers.json` porte le palier 1 : un titre, des commandes du catalogue, un test non
   vide fait d'id de consignes réelles, dont chaque consigne à exécuter appelle une
   commande du palier.
"""
import importlib.util, pathlib, re

_spec = importlib.util.spec_from_file_location('agent_commun', pathlib.Path(__file__).parent / 'agent_commun.py')
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

LIVRABLES = ['besoin.md', 'reponses.json', 'acces-outil.json', 'consignes-reelles.jsonl',
             'catalogue.json', 'paliers.json', 'palier-1.md']
REPONSES = ('besoin', 'acces', 'machine', 'critere')
SOURCES_INTERDITES = re.compile(r'g[ée]n[ée]r', re.I)


def _norm(s):
    return re.sub(r'\s+', ' ', str(s or '')).strip()


def validate(workspace):
    errs = []
    ws = pathlib.Path(workspace)
    d = ws / C.DOCS

    for f in LIVRABLES:
        p = d / f
        if not p.exists() or p.stat().st_size == 0:
            errs.append(f"C1: `{C.DOCS}/{f}` absent/vide — le nœud n'a pas produit ce qu'il annonce")

    # C2 — les quatre réponses
    rep, e = C.lire_json(d / 'reponses.json')
    if isinstance(rep, dict):
        for k in REPONSES:
            v = rep.get(k)
            if not isinstance(v, dict) or not C.non_vide(v.get('citation')):
                errs.append(f"C2: réponse `{k}` sans citation — chaque réponse se garde dans les mots de l'utilisateur")
        if C.critere(ws) is None:
            errs.append("C2: `critere` doit porter `reussite_min` dans ]0, 1] et `actions_a_tort_max` entier ≥ 0 — "
                        "sans eux, le vérificateur ne sait pas quand un palier est prêt")
        m = rep.get('machine') if isinstance(rep.get('machine'), dict) else {}
        if not any(isinstance(m.get(k), (int, float)) and not isinstance(m.get(k), bool)
                   for k in ('taille_max_go', 'latence_max_s')):
            errs.append("C2: `machine` ne porte ni `taille_max_go` ni `latence_max_s` — la limite n'est pas chiffrée")
    elif e != 'absent/vide':
        errs.append(f"C2: `reponses.json` {e}")

    # C3 — le besoin mot pour mot
    if isinstance(rep, dict) and isinstance(rep.get('besoin'), dict) and C.non_vide(rep['besoin'].get('citation')):
        cit = _norm(rep['besoin']['citation'])
        if cit and cit not in _norm(C.txt(d / 'besoin.md').replace('> ', ' ')):
            errs.append("C3: `besoin.md` ne reprend pas la citation du besoin mot pour mot")

    # C4 — l'accès constaté
    acc, e = C.lire_json(d / 'acces-outil.json')
    if isinstance(acc, dict):
        if not C.non_vide(acc.get('outil')):
            errs.append("C4: `acces-outil.json` ne nomme pas l'outil")
        if not re.match(r'https?://', str(acc.get('url') or '')):
            errs.append("C4: `acces-outil.json` sans URL http(s) de l'outil")
        if not C.non_vide(acc.get('rejouer')):
            errs.append("C4: `acces-outil.json` sans commande `rejouer` — aucun palier ne pourra se vérifier dans l'outil")
        cs = acc.get('constate')
        if not isinstance(cs, dict) or not re.match(r'\d{4}-\d{2}-\d{2}', str(cs.get('date') or '')) \
                or not C.non_vide(cs.get('resultat')):
            errs.append("C4: `constate` absent ou incomplet (date ISO + résultat) — l'accès n'a pas été essayé pour de vrai")
    elif e != 'absent/vide':
        errs.append(f"C4: `acces-outil.json` {e}")

    # C5 — les consignes réelles (générées seulement sur décision citée de l'utilisateur)
    cons = rep.get('consignes') if isinstance(rep, dict) and isinstance(rep.get('consignes'), dict) else {}
    generees_ok = cons.get('generees_autorisees') is True and C.non_vide(cons.get('citation'))
    lignes, lerrs = C.lire_jsonl(d / 'consignes-reelles.jsonl')
    for x in lerrs[:5]:
        errs.append(f"C5: `consignes-reelles.jsonl` {x}")
    vus, ids = set(), {}
    if (d / 'consignes-reelles.jsonl').exists() and not lignes:
        errs.append("C5: `consignes-reelles.jsonl` ne porte aucune consigne — sans elles, aucun test")
    for c in lignes:
        cid = str(c.get('id') or '')
        if not cid:
            errs.append("C5: une consigne sans `id`")
            continue
        if cid in vus:
            errs.append(f"C5: id de consigne en double : {cid}")
        vus.add(cid)
        ids[cid] = c
        if not C.non_vide(c.get('texte')):
            errs.append(f"C5: consigne {cid} sans `texte`")
        att = c.get('attendu') if isinstance(c.get('attendu'), dict) else {}
        if att.get('action') not in C.ACTIONS:
            errs.append(f"C5: consigne {cid} : `attendu.action` `{att.get('action')}` hors de {list(C.ACTIONS)}")
        elif att.get('action') == 'executer' and not C.non_vide(att.get('commande')):
            errs.append(f"C5: consigne {cid} à exécuter sans `attendu.commande`")
        src = c.get('source')
        if not C.non_vide(src):
            errs.append(f"C5: consigne {cid} sans `source`")
        elif SOURCES_INTERDITES.search(src) and not generees_ok:
            errs.append(f"C5: consigne {cid} de source `{src}` — le test est fait de consignes réelles, jamais générées")

    # C6 — le catalogue
    cat, e = C.lire_json(d / 'catalogue.json')
    commandes = None
    if isinstance(cat, dict) and isinstance(cat.get('commandes'), list):
        commandes = {str(x.get('id')) for x in cat['commandes'] if isinstance(x, dict) and x.get('id')}
        if not commandes:
            errs.append("C6: `catalogue.json` ne porte aucune commande")
        manquantes = sorted({str(c['attendu']['commande']) for c in ids.values()
                             if isinstance(c.get('attendu'), dict) and c['attendu'].get('commande')
                             and str(c['attendu']['commande']) not in commandes})
        if commandes and manquantes:
            errs.append("C6: commandes attendues par des consignes réelles absentes du catalogue : "
                        + ', '.join(manquantes[:10]) + (' …' if len(manquantes) > 10 else ''))
    elif cat is not None or (e and e != 'absent/vide'):
        errs.append("C6: `catalogue.json` doit porter `{\"commandes\": [{\"id\": …}]}`")

    # C7 — le palier 1
    pal = C.paliers(ws)
    p1 = next((p for p in pal if p.get('n') == 1), None)
    if (d / 'paliers.json').exists() and p1 is None:
        errs.append("C7: `paliers.json` ne porte pas le palier 1 (`n: 1`)")
    if p1 is not None:
        if not C.non_vide(p1.get('titre')):
            errs.append("C7: palier 1 sans `titre`")
        if p1.get('statut', 'a-faire') not in C.STATUTS_PALIER:
            errs.append(f"C7: palier 1 au statut `{p1.get('statut')}` hors de {list(C.STATUTS_PALIER)}")
        pc = p1.get('commandes')
        if not isinstance(pc, list) or not pc:
            errs.append("C7: palier 1 sans `commandes`")
            pc = []
        pc = {str(x) for x in pc}
        if commandes is not None and pc - commandes:
            errs.append("C7: commandes du palier 1 absentes du catalogue : " + ', '.join(sorted(pc - commandes)[:10]))
        test = p1.get('test')
        if not isinstance(test, list) or not test:
            errs.append("C7: palier 1 sans `test` — un palier se juge sur ses vraies consignes")
            test = []
        inconnus = [str(t) for t in test if str(t) not in ids]
        if inconnus:
            errs.append("C7: consignes du test du palier 1 absentes des consignes réelles : " + ', '.join(inconnus[:10]))
        hors = [str(t) for t in test if str(t) in ids and (ids[str(t)].get('attendu') or {}).get('action') == 'executer'
                and str((ids[str(t)].get('attendu') or {}).get('commande')) not in pc]
        if hors:
            errs.append("C7: consignes du test du palier 1 qui exécutent une commande hors du palier : " + ', '.join(hors[:10]))
    return errs
