"""Tests du programme du module agent : un faux moteur flux (new-run, run-node, agent-lancer, agent-etat) dans un
dossier temporaire, le vrai programme appelé comme le mod l'appelle (JSON sur l'entrée standard)."""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import textwrap
import unittest

PROG = pathlib.Path(__file__).resolve().parents[1] / 'agent.py'

FAUX_NEW_RUN = '''
import sys, os, pathlib
root = pathlib.Path(os.environ['AGENT_RUNS']); root.mkdir(parents=True, exist_ok=True)
ws = root / (sys.argv[2] + '-2026-10-27-090000'); ws.mkdir()
(ws / 'WORKSPACE.txt').write_text('workflow: agent\\nprojet: %s\\nouvert: 2026-10-27T09:00:00\\nmode: production\\n' % sys.argv[2])
'''

# Le faux run-node : --brief-only écrit le brief ; sinon le gate du nœud est vert si GATE_VERT_<nœud> existe dans la run.
FAUX_RUN_NODE = '''
import sys, os, json, pathlib
wf, node = sys.argv[1], sys.argv[2]
ws = pathlib.Path(sys.argv[sys.argv.index('--workspace') + 1])
d = pathlib.Path(os.environ['FLUX_HOME']) / 'state' / wf / ws.name; (d / node).mkdir(parents=True, exist_ok=True)
if '--brief-only' in sys.argv:
    (d / node / 'brief.md').write_text('brief'); (d / node / 'sys.md').write_text('sys'); print(d / node / 'brief.md'); sys.exit(0)
vert = (ws / ('GATE_VERT_' + node)).exists()
(ws / ('GATE_PASSE_' + node)).write_text('1')
(d / (node + '.json')).write_text(json.dumps({'statut': 'vert' if vert else 'rouge', 'erreurs': [] if vert else ['C4: acces-outil.json ne nomme pas l outil']}))
sys.exit(0 if vert else 1)
'''

FAUX_LANCER = '''
import sys, json, pathlib
ws = pathlib.Path(sys.argv[1])
if (ws / 'LANCER_REFUSE').exists():
    print(json.dumps({'ok': False, 'refus': (ws / 'LANCER_REFUSE').read_text()})); sys.exit(1)
if '--dry-run' not in sys.argv:
    (ws / 'LANCE').write_text(str(int((ws / 'LANCE').read_text()) + 1) if (ws / 'LANCE').exists() else '1')
d = ws / 'docs/agent/retours'
a_traiter = [f for f in (d.glob('tour-*.json') if d.is_dir() else []) if json.loads(f.read_text()).get('statut') == 'a-traiter']
print(json.dumps({'ok': True, 'tmux': 'agent-lanceur-x', 'mode': 'retours' if a_traiter else 'palier', 'palier': 1,
                  'dry_run': '--dry-run' in sys.argv}))
'''

FAUX_ETAT = '''
import sys, json, pathlib
ws = pathlib.Path(sys.argv[1])
f = ws / 'ETAT_CONSTRUCTION.json'
print(f.read_text() if f.exists() else json.dumps({'en_cours': True, 'phase': 'palier', 'tour': 0, 'palier_courant': 1,
      'paliers': [], 'preversion': None, 'production': None, 'verification': None, 'bloque': None, 'retours_a_traiter': []}))
'''

SORTIES = {
    'E1.2': ['docs/agent/acces-outil.json'],
    'E1.3': ['docs/agent/consignes-reelles.jsonl', 'docs/agent/catalogue.json'],
    'E1.4': ['docs/agent/reponses.json'],
    'E1.5': [],
}


class Banc(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = pathlib.Path(self.tmp.name)
        self.runs, self.flux = t / 'runs', t / 'flux'
        for rel, src in [('runtime/new-run.py', FAUX_NEW_RUN), ('runtime/run-node.py', FAUX_RUN_NODE),
                         ('tools/agent-lancer.py', FAUX_LANCER), ('tools/agent-etat.py', FAUX_ETAT)]:
            p = self.flux / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(textwrap.dedent(src))
        (self.flux / 'workflows').mkdir()
        (self.flux / 'workflows/agent.json').write_text(json.dumps({'workspace_root': str(self.runs), 'nodes': [
            {'id': 'concevoir', 'n': 1}, {'id': 'construire', 'n': 2}, {'id': 'revue', 'n': 3}]}))

    def tearDown(self):
        self.tmp.cleanup()

    def appel(self, commande, runs=None, **args):
        env = dict(os.environ, AGENT_RUNS=str(runs or self.runs), FLUX_HOME=str(self.flux),
                   AGENT_OUTILS=str(self.flux / 'tools'), AGENT_GRAPHES=str(self.flux / 'workflows'))
        r = subprocess.run([sys.executable, '-B', str(PROG), commande], input=json.dumps(args),
                           capture_output=True, text=True, env=env, timeout=60)
        return json.loads(r.stdout.strip().splitlines()[-1])

    def ok(self, commande, **args):
        r = self.appel(commande, **args)
        self.assertTrue(r['ok'], r)
        return r['resultat']

    def refus(self, commande, **args):
        r = self.appel(commande, **args)
        self.assertFalse(r['ok'], r)
        return r['refus']

    def ecrire(self, ws, rel, contenu='x'):
        p = pathlib.Path(ws) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(contenu if isinstance(contenu, str) else json.dumps(contenu, ensure_ascii=False))

    def lire(self, ws, rel):
        return json.loads((pathlib.Path(ws) / rel).read_text())

    def etats(self, run, n):
        return {s['id']: s['etat'] for s in self.ok('etat', run=run)['etapes'][n - 1]['sous_etapes']}

    def etape1_jusqua(self, run, ws, jusqua='E1.5'):
        self.ok('besoin', run=run, citation='Un agent qui range mes mails dans les bons dossiers')
        for sid, fichiers in SORTIES.items():
            for f in fichiers:
                self.ecrire(ws, f, {'url': 'https://outil.example/'} if f.endswith('acces-outil.json') else 'x')
            self.ok('avancer', run=run, sous_etape=sid, etat='validee', citation='A')
            if sid == jusqua:
                return

    def prete(self, projet='essai'):
        """Une run dont l'étape 1 est close (gate vert)."""
        v = self.ok('ouvrir', projet=projet)
        run, ws = v['run'], v['workspace']
        self.etape1_jusqua(run, ws)
        self.ecrire(ws, 'GATE_VERT_concevoir')
        self.ok('cloturer', run=run)
        return run, ws

    def livrer(self, ws, palier, version, tour, paliers=None):
        """La construction a livré `version` du `palier` en préversion pendant le tour `tour` (rien ne tourne)."""
        paliers = paliers or [{'n': palier, 'titre': 'Ranger les mails', 'statut': 'preversion', 'commandes': ['ranger'], 'test': ['c1']}]
        self.ecrire(ws, 'docs/agent/paliers.json', {'paliers': paliers})
        vs = self.lire(ws, 'docs/agent/versions.json')['versions'] if (pathlib.Path(ws) / 'docs/agent/versions.json').exists() else []
        vs.append({'version': version, 'palier': palier, 'tour': tour, 'date': '2026-10-27T10:00:00Z',
                   'emplacement': f'https://outil.example/preversion/{version}', 'statut': 'preversion'})
        self.ecrire(ws, 'docs/agent/versions.json', {'versions': vs})
        self.ecrire(ws, f'docs/agent/paliers/p{palier}/fiche.md', '## Sait faire\n\n• ranger\n\n## Ne sait pas encore\n\n• trier')
        self.ecrire(ws, 'ETAT_CONSTRUCTION.json', {
            'en_cours': False, 'phase': 'preversion', 'tour': tour, 'palier_courant': palier, 'bloque': None,
            'paliers': [{'n': p['n'], 'titre': p['titre'], 'statut': p['statut']} for p in paliers],
            'preversion': vs[-1], 'production': None, 'retours_a_traiter': [],
            'verification': {'verdict': 'PASS', 'reussite': 0.9, 'actions_a_tort': 0, 'rejouees': 10, 'version': version}})

    def mettre_en_production(self, ws, palier, version, suivant=False):
        paliers = [{'n': palier, 'titre': 'Ranger les mails', 'statut': 'production', 'commandes': ['ranger'], 'test': ['c1']}]
        if suivant:
            paliers.append({'n': palier + 1, 'titre': 'Trier', 'statut': 'a-faire', 'commandes': ['trier'], 'test': ['c2']})
        self.ecrire(ws, 'docs/agent/paliers.json', {'paliers': paliers})
        vs = self.lire(ws, 'docs/agent/versions.json')
        for v in vs['versions']:
            if v['version'] == version:
                v['statut'] = 'production'
        self.ecrire(ws, 'docs/agent/versions.json', vs)
        self.ecrire(ws, 'docs/agent/production.json', {'productions': [
            {'palier': palier, 'version': version, 'date': '2026-10-27T11:00:00Z', 'fiche': f'docs/agent/paliers/p{palier}/fiche.md'}]})


class TestEtape1(Banc):
    def test_ouvrir_cree_la_run_puis_la_reprend(self):
        v = self.ok('ouvrir', projet='Assistant Biblio', session='s1')
        self.assertTrue(v['neuf'])
        self.assertTrue(v['run'].startswith('assistant-biblio-'))
        self.assertEqual(v['attend']['sous_etape'], 'E1.1')
        self.assertTrue(pathlib.Path(v['brief']['sys']).exists(), 'le brief du nœud concevoir est préparé')
        self.assertTrue((pathlib.Path(v['workspace']) / 'state/module-agent.json').exists())
        v2 = self.ok('ouvrir', projet='assistant-biblio', session='s2')
        self.assertFalse(v2['neuf'])
        self.assertEqual(v2['run'], v['run'])

    def test_ouvrir_refuse_une_racine_que_le_graphe_ne_connait_pas(self):
        ailleurs = pathlib.Path(self.tmp.name) / 'ailleurs'
        self.assertIn('création refusée', self.refus('ouvrir', runs=ailleurs, projet='essai'))
        self.assertFalse(self.runs.exists(), 'new-run n’a pas été appelé')

    def test_besoin_mot_pour_mot_puis_e12(self):
        v = self.ok('ouvrir', projet='essai')
        run, ws = v['run'], pathlib.Path(v['workspace'])
        self.ok('besoin', run=run, citation='Je veux un agent qui range\nmes mails')
        e = {s['id']: s for s in self.ok('etat', run=run)['etapes'][0]['sous_etapes']}
        self.assertEqual((e['E1.1']['etat'], e['E1.1']['citation']), ('validee', 'Je veux un agent qui range\nmes mails'))
        self.assertEqual(e['E1.2']['etat'], 'en_cours')
        texte = (ws / 'docs/agent/besoin.md').read_text()
        self.assertTrue(texte.startswith('# Le besoin\n\nReçu le '))
        self.assertIn('> Je veux un agent qui range\n> mes mails', texte)
        self.assertTrue(self.ok('besoin', run=run, citation='autre')['deja'])
        self.assertEqual(self.ok('etat', run=run)['attend']['quoi'], 'donner l’accès à l’outil')

    def test_besoin_garde_un_besoin_prepare(self):
        v = self.ok('ouvrir', projet='essai')
        run, ws = v['run'], pathlib.Path(v['workspace'])
        self.ecrire(ws, 'docs/agent/besoin.md', '# Assistant de la médiathèque\n\n## Vision\n\n• gérer ses prêts à la voix\n')
        self.ok('besoin', run=run, citation='L’assistant doit gérer mes prêts')
        texte = (ws / 'docs/agent/besoin.md').read_text()
        self.assertTrue(texte.startswith('# Assistant de la médiathèque\n\n## Le besoin, mot pour mot\n\nReçu le '))
        self.assertIn('> L’assistant doit gérer mes prêts\n', texte)
        self.assertIn('## Vision\n\n• gérer ses prêts à la voix', texte)
        self.assertLess(texte.index('> L’assistant doit gérer mes prêts'), texte.index('## Vision'))

    def test_avancer_ordre_citation_sorties(self):
        v = self.ok('ouvrir', projet='essai')
        run, ws = v['run'], v['workspace']
        self.assertIn('pas encore validée', self.refus('avancer', run=run, sous_etape='E1.2', etat='en_cours'))
        self.ok('besoin', run=run, citation='besoin')
        self.assertIn('acces-outil.json', self.refus('avancer', run=run, sous_etape='E1.2', etat='a_valider'))
        self.ecrire(ws, 'docs/agent/acces-outil.json', {'url': 'https://outil.example/'})
        self.ok('avancer', run=run, sous_etape='E1.2', etat='a_valider')
        self.assertEqual(self.ok('etat', run=run)['attend'], {'quoi': "valider l'accès à l'outil réel", 'sous_etape': 'E1.2'})
        self.assertIn('citation', self.refus('avancer', run=run, sous_etape='E1.2', etat='validee'))
        self.assertIn('E1.2', self.refus('avancer', run=run, sous_etape='E1.3', etat='en_cours'))
        self.ok('avancer', run=run, sous_etape='E1.2', etat='validee', citation='voilà le lien')
        self.assertEqual(self.etats(run, 1)['E1.3'], 'en_cours')
        self.assertEqual(self.ok('etat', run=run)['attend']['quoi'], 'tes consignes réelles')
        self.assertIn('consignes-reelles.jsonl', self.refus('avancer', run=run, sous_etape='E1.3', etat='validee', citation='A'))
        self.assertIn('cloturer', self.refus('avancer', run=run, sous_etape='E1.6', etat='validee', citation='x'))
        self.assertIn('premier message', self.refus('avancer', run=run, sous_etape='E1.1', etat='validee', citation='x'))
        self.assertIn('constate', self.refus('avancer', run=run, sous_etape='E2.1', etat='validee', citation='x'))

    def test_questions_puis_e16_rien_n_attend(self):
        v = self.ok('ouvrir', projet='essai')
        run, ws = v['run'], v['workspace']
        self.etape1_jusqua(run, ws, 'E1.3')
        self.assertEqual(self.ok('etat', run=run)['attend']['quoi'], 'la limite de la machine')
        self.ecrire(ws, 'docs/agent/reponses.json', {})
        self.ok('avancer', run=run, sous_etape='E1.4', etat='validee', citation='B')
        self.assertEqual(self.ok('etat', run=run)['attend']['quoi'], 'ce qui rend un palier prêt')
        self.ok('avancer', run=run, sous_etape='E1.5', etat='validee', citation='A')
        v = self.ok('etat', run=run)
        self.assertEqual(self.etats(run, 1)['E1.6'], 'en_cours')
        self.assertIsNone(v['attend'], 'E1.6 : l’agent travaille')
        self.assertEqual(v['sous_etape_courante'], 'E1.6')

    def test_decision_et_rouvrir(self):
        v = self.ok('ouvrir', projet='essai')
        run = v['run']
        self.ok('decision', run=run, sous_etape='E1.4', resume='2 Go, 1 s', citation='sur un portable, 2 Go max', option='A')
        self.etape1_jusqua(run, v['workspace'], 'E1.4')
        self.ok('rouvrir', run=run, sous_etape='E1.3', raison='il a d’autres consignes')
        e = {s['id']: s for s in self.ok('etat', run=run)['etapes'][0]['sous_etapes']}
        self.assertEqual(e['E1.3']['etat'], 'en_cours')
        self.assertEqual(e['E1.4']['etat'], 'validee')
        self.assertEqual(e['E1.5']['etat'], 'a_faire')
        self.assertEqual(e['E1.4']['decisions'][0]['citation'], 'sur un portable, 2 Go max')

    def test_cloturer_rouge_puis_vert(self):
        v = self.ok('ouvrir', projet='essai')
        run, ws = v['run'], v['workspace']
        self.assertIn('E1.5', self.refus('cloturer', run=run))
        self.etape1_jusqua(run, ws)
        self.assertIn('ne nomme pas l outil', self.refus('cloturer', run=run))
        self.assertEqual(self.etats(run, 1)['E1.6'], 'en_cours')
        self.ecrire(ws, 'GATE_VERT_concevoir')
        self.assertEqual(self.ok('cloturer', run=run)['gate'], 'vert')
        v = self.ok('etat', run=run)
        e16 = v['etapes'][0]['sous_etapes'][-1]
        self.assertEqual((e16['etat'], e16['citation']), ('validee', 'gate vert'))
        self.assertEqual(v['etapes'][0]['etat'], 'faite')
        self.assertEqual(v['attend'], {'quoi': 'lancer la construction', 'action': 'lancer'})
        self.assertEqual(v['etape_courante'], 2)


class TestEtapes2et3(Banc):
    def test_lancer_exige_l_etape_1_puis_enregistre(self):
        v = self.ok('ouvrir', projet='autre')
        self.assertIn('étape 1', self.refus('lancer', run=v['run']))
        run, ws = self.prete()
        dry = self.ok('lancer', run=run, dry_run=True)
        self.assertTrue(dry['dry_run'])
        self.assertIsNone(self.ok('etat', run=run)['lance_le'], 'un essai à blanc ne lance rien')
        self.assertEqual(self.ok('lancer', run=run)['mode'], 'palier')
        e = self.lire(ws, 'state/module-agent.json')
        self.assertTrue(e['lance_le'])
        self.assertEqual([(x['mode'], x['palier']) for x in e['lancements']], [('palier', 1)])
        self.assertEqual(self.etats(run, 2), {'E2.1': 'en_cours', 'E2.2': 'a_faire'})
        self.assertIsNone(self.ok('etat', run=run)['attend'])
        self.ecrire(ws, 'LANCER_REFUSE', 'la construction tourne déjà')
        self.assertIn('tourne déjà', self.refus('lancer', run=run))

    def test_suivi_donnees_verification_bloque(self):
        run, ws = self.prete()
        self.ok('lancer', run=run)
        self.ecrire(ws, 'docs/agent/paliers/p1/donnees/entrainement.jsonl', '{}')
        self.ecrire(ws, 'docs/agent/paliers/p1/journal.md', 'j')
        self.assertEqual(self.etats(run, 2), {'E2.1': 'validee', 'E2.2': 'en_cours'})
        self.ecrire(ws, 'ETAT_CONSTRUCTION.json', {'en_cours': False, 'phase': 'palier', 'tour': 0, 'palier_courant': 1,
                                                   'paliers': [], 'bloque': '3 passes sans progrès'})
        v = self.ok('etat', run=run)
        self.assertEqual(self.etats(run, 2), {'E2.1': 'validee', 'E2.2': 'bloquee'})
        self.assertEqual(v['attend']['action'], 'lancer')
        self.assertIn('3 passes sans progrès', v['attend']['quoi'])

    def test_revue_good_palier_suivant_puis_arret(self):
        run, ws = self.prete()
        self.ok('lancer', run=run)
        self.assertIn('pas de revue', self.refus('revue', run=run, verdict='good', suite='arret', citation='top'))
        self.livrer(ws, 1, 'V1', 0)
        v = self.ok('etat', run=run)
        self.assertEqual(v['etape_courante'], 3)
        self.assertEqual(v['attend'], {'quoi': 'essayer la préversion du palier 1', 'sous_etape': 'E3.1'})
        self.assertEqual(v['liens'], {'outil': 'https://outil.example/', 'preversion': 'https://outil.example/preversion/V1',
                                      'fiche': 'docs/agent/paliers/p1/fiche.md'})
        self.assertEqual((v['palier'], v['version']), (1, 'V1'))
        self.assertIn('suite', self.refus('revue', run=run, verdict='good', citation='top'))
        self.assertIn('production.json', self.refus('revue', run=run, verdict='good', suite='palier-suivant', citation='top'))
        self.mettre_en_production(ws, 1, 'V1')
        self.assertEqual(self.etats(run, 3)['E3.1'], 'en_cours', 'la version passée en production reste celle qu’on juge')
        self.assertIn('palier 2', self.refus('revue', run=run, verdict='good', suite='palier-suivant', citation='top'))
        self.mettre_en_production(ws, 1, 'V1', suivant=True)
        r = self.ok('revue', run=run, verdict='good', suite='palier-suivant', citation="c'est bon, on continue")
        self.assertEqual((r['tour'], r['palier'], r['version'], r['relance']['mode']), (1, 1, 'V1', 'palier'))
        self.assertEqual((pathlib.Path(ws) / 'LANCE').read_text(), '2')
        t = self.lire(ws, 'docs/agent/revue.json')['tours'][0]
        self.assertEqual({k: t[k] for k in ('tour', 'palier', 'version', 'verdict', 'suite', 'citation')},
                         {'tour': 1, 'palier': 1, 'version': 'V1', 'verdict': 'good', 'suite': 'palier-suivant',
                          'citation': "c'est bon, on continue"})
        # palier 2 en construction : tout se remet en cours
        self.ecrire(ws, 'ETAT_CONSTRUCTION.json', {'en_cours': True, 'phase': 'preversion', 'tour': 1, 'palier_courant': 2,
                                                   'paliers': [], 'bloque': None, 'retours_a_traiter': []})
        v = self.ok('etat', run=run)
        self.assertEqual((v['etape_courante'], v['palier']), (2, 2))
        self.assertEqual(self.etats(run, 2), {'E2.1': 'en_cours', 'E2.2': 'a_faire'})
        self.assertEqual(self.etats(run, 3), {'E3.1': 'a_faire'})
        self.livrer(ws, 2, 'V2', 1, paliers=[{'n': 1, 'titre': 'Ranger les mails', 'statut': 'production'},
                                             {'n': 2, 'titre': 'Trier', 'statut': 'preversion'}])
        self.assertEqual(self.ok('etat', run=run)['attend']['quoi'], 'essayer la préversion du palier 2')
        self.ecrire(ws, 'docs/agent/production.json', {'productions': [{'palier': 2, 'version': 'V2', 'fiche': 'docs/agent/paliers/p2/fiche.md'}]})
        r = self.ok('revue', run=run, verdict='good', suite='arret', citation='parfait, on s’arrête')
        self.assertTrue(r['close'])
        self.assertTrue((pathlib.Path(ws) / 'GATE_PASSE_revue').exists(), 'le gate du nœud revue est passé')
        self.assertEqual(r['gate'], 'rouge')
        v = self.ok('etat', run=run)
        self.assertTrue(v['close'])
        self.assertIsNone(v['attend'])
        self.assertEqual(self.etats(run, 3), {'E3.1': 'validee'})
        self.assertEqual((pathlib.Path(ws) / 'LANCE').read_text(), '2', 'arrêt : pas de relance')
        self.assertIn('close', self.refus('lancer', run=run))

    def test_revue_retours_relance_le_palier(self):
        run, ws = self.prete()
        self.ok('lancer', run=run)
        self.livrer(ws, 1, 'V1', 0)
        self.assertIn('retours du tour 1', self.refus('revue', run=run, verdict='retours', citation='pas bon'))
        self.assertIn('attendu', self.refus('retours', run=run, citation='x', retours=[{'dit': 'il range mal'}]))
        r = self.ok('retours', run=run, citation='il range les factures dans perso', retours=[
            {'dit': 'il range les factures dans perso', 'consigne': 'range la facture EDF', 'attendu': 'la facture EDF va dans Factures'},
            {'dit': 'trop lent', 'attendu': 'répond en moins d’une seconde'}])
        self.assertEqual((r['tour'], r['palier']), (1, 1))
        t = self.lire(ws, 'docs/agent/retours/tour-1.json')
        self.assertEqual((t['tour'], t['palier'], t['statut']), (1, 1, 'a-traiter'))
        self.assertEqual(t['retours'][0], {'id': 'R1', 'dit': 'il range les factures dans perso',
                                           'consigne': 'range la facture EDF', 'attendu': 'la facture EDF va dans Factures'})
        self.assertIsNone(t['retours'][1]['consigne'])
        self.assertIn('range la facture EDF', (pathlib.Path(ws) / 'docs/agent/retours/tour-1.md').read_text())
        self.assertIn('retours', self.refus('revue', run=run, verdict='good', suite='arret', citation='bon'))
        rv = self.ok('revue', run=run, verdict='retours', citation='il veut que ça range mieux')
        self.assertEqual(rv['relance']['mode'], 'retours')
        self.assertEqual((pathlib.Path(ws) / 'LANCE').read_text(), '2')
        t = self.lire(ws, 'docs/agent/revue.json')['tours'][0]
        self.assertEqual((t['verdict'], t['palier'], t['version'], t['suite']), ('retours', 1, 'V1', None))
        self.ecrire(ws, 'ETAT_CONSTRUCTION.json', {'en_cours': True, 'phase': 'retours', 'tour': 1, 'palier_courant': 1,
                                                   'paliers': [], 'bloque': None, 'retours_a_traiter': [1]})
        self.ecrire(ws, 'docs/agent/paliers/p1/donnees/entrainement.jsonl', '{}')
        self.ecrire(ws, 'docs/agent/paliers/p1/journal.md', 'j')
        v = self.ok('etat', run=run)
        self.assertEqual((v['tour'], v['etape_courante']), (1, 2))
        self.assertEqual(self.etats(run, 2), {'E2.1': 'en_cours', 'E2.2': 'a_faire'}, 'un tour de retours remet en cours')
        self.assertEqual(self.etats(run, 3), {'E3.1': 'a_faire'})
        self.livrer(ws, 1, 'V2', 1)
        v = self.ok('etat', run=run)
        self.assertEqual((v['etape_courante'], v['version']), (3, 'V2'))

    def test_relance_refusee_se_garde(self):
        run, ws = self.prete()
        self.ok('lancer', run=run)
        self.livrer(ws, 1, 'V1', 0)
        self.ok('retours', run=run, citation='x', retours=[{'dit': 'mal', 'attendu': 'bien'}])
        self.ecrire(ws, 'LANCER_REFUSE', 'jeton du moteur principal illisible')
        rv = self.ok('revue', run=run, verdict='retours', citation='mal')
        self.ecrire(ws, 'ETAT_CONSTRUCTION.json', {'en_cours': False, 'phase': 'retours', 'tour': 1, 'palier_courant': 1,
                                                   'paliers': [], 'bloque': None, 'retours_a_traiter': [1]})
        self.assertIn('jeton', rv['relance_refusee'])
        v = self.ok('etat', run=run)
        self.assertEqual(v['attend']['action'], 'lancer')
        (pathlib.Path(ws) / 'LANCER_REFUSE').unlink()
        self.ok('lancer', run=run)
        self.assertNotIn('relance_refusee', self.lire(ws, 'state/module-agent.json'))

    def test_lire_reste_dans_la_run(self):
        run, ws = self.prete()
        self.assertEqual(self.ok('lire', run=run, chemin='docs/agent/catalogue.json')['contenu'], 'x')
        self.assertIn('hors de la run', self.refus('lire', run=run, chemin='../../etc/passwd'))
        self.assertIn('hors de la run', self.refus('lire', run=run, chemin='/etc/passwd'))
        self.assertIn('run invalide', self.refus('etat', run='../x'))

    def test_liste(self):
        run, _ = self.prete()
        self.assertEqual([r['run'] for r in self.ok('liste')['runs']], [run])


if __name__ == '__main__':
    unittest.main()
