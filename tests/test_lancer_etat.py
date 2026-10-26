"""tools/agent-lancer.py et tools/agent-etat.py — au contrat de docs/contrat.md.

Aucun agent n'est lancé : le superviseur joue contre un FAUX moteur (AGENT_LANCER_RUN_NODE), les états vivent dans un
dossier temporaire (FLUX_STATE_DIR), les workspaces aussi. Les réglages du moteur (moteurs.json) sont un faux, dans
une racine flux temporaire (FLUX_RACINE) ; le code du moteur vient de FLUX_HOME (sinon vendor/flux).

    python3 -m unittest tests.test_lancer_etat
"""
import importlib.util, json, os, pathlib, shutil, subprocess, sys, tempfile, time, unittest

DEPOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DEPOT / 'tests'))
import test_validateurs as V  # noqa: E402  (fabrique la run témoin)

LANCER = DEPOT / 'tools' / 'agent-lancer.py'
ETAT = DEPOT / 'tools' / 'agent-etat.py'
D = 'docs/agent'

FAUX_MOTEUR = r'''
import json, os, pathlib, sys
ws = pathlib.Path(sys.argv[sys.argv.index('--workspace') + 1])
plan = json.loads((ws / 'plan-faux-moteur.json').read_text())
compteur = ws / 'compteur'
i = int(compteur.read_text()) if compteur.exists() else 0
compteur.write_text(str(i + 1))
pas = plan[min(i, len(plan) - 1)]
d = pathlib.Path(os.environ['FLUX_STATE_DIR']) / 'agent' / ws.name
d.mkdir(parents=True, exist_ok=True)
st = json.loads((d / 'construire.json').read_text()) if (d / 'construire.json').exists() else {'passages': []}
p = {'n': len(st['passages']) + 1, 'started': '2026-10-24T10:00:00Z', 'ended': '2026-10-24T10:05:00Z',
     'verdict': {0: 'vert', 1: 'rouge', 2: 'panne'}[pas['rc']], 'compte': 'essai', 'session': 'aucune'}
if pas.get('panne'):
    p['panne'] = {'cause': pas['panne']}
st['passages'].append(p); st['rc'] = pas['rc']
st['statut'] = pas.get('statut', 'panne' if pas['rc'] == 2 else 'en-cours')
(d / 'construire.json').write_text(json.dumps(st))
if pas.get('progres'):
    j = ws / 'docs/agent/paliers/p1'
    j.mkdir(parents=True, exist_ok=True)
    with open(j / 'journal.md', 'a') as f:
        f.write('\n## Constructeur — passe %d\n' % (i + 1))
if pas.get('bloque'):
    av = ws / 'docs/agent/avancement.json'
    a = json.loads(av.read_text()) if av.exists() else {}
    a['bloque'] = pas['bloque']
    av.write_text(json.dumps(a))
sys.exit(pas['rc'])
'''


def fabriquer(ws):
    """Une run à la sortie de l'étape 1 : tous les livrables de `concevoir`, le palier 1 à construire."""
    V.fabriquer(ws)
    for rel in ('paliers', 'retours', 'revue.json', 'production.json', 'versions.json', 'avancement.json'):
        p = ws / D / rel
        shutil.rmtree(p) if p.is_dir() else p.unlink(missing_ok=True)
    V.ecrire(ws, f'{D}/paliers.json', {'paliers': [
        {'n': 1, 'titre': 'Ouvrir et régler', 'commandes': ['ouvrir_prets', 'prolonger_pret'],
         'test': ['S01-p01', 'S01-p02', 'S02-p01', 'S02-p02'], 'statut': 'a-faire'}]})


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix='agent-lanceur-'))
        self.ws = self.tmp / f'test-lanceur-{os.getpid()}-{time.time_ns() % 10**8}'
        self.ws.mkdir()
        fabriquer(self.ws)
        V.ecrire(self.ws, 'WORKSPACE.txt', 'workflow: agent\nprojet: test-lanceur\nouvert: 2026-10-24T10:00:00\nmode: production\n')
        self.state = self.tmp / 'state'
        self.state.mkdir()
        self.faux = self.tmp / 'faux-run-node.py'
        self.faux.write_text(FAUX_MOTEUR, encoding='utf-8')
        self.racine = self.tmp / 'racine-flux'
        V.ecrire(self.racine, 'moteurs.json', {'defaut': 'essai', 'moteurs': [{'id': 'essai', 'config_dir': str(self.tmp)}]})
        self.reglages = dict(FLUX_STATE_DIR=str(self.state), AGENT_LANCER_RUN_NODE=str(self.faux),
                             FLUX_RACINE=str(self.racine), FLUX_WORKFLOWS_DIR=str(DEPOT / 'workflows'))
        self.env = dict(os.environ, **self.reglages)
        self.env.pop('AGENT_MOTEUR', None)
        self.env.pop('FLUX_IGNORER_VERSION', None)
        self.sessions = []

    def tearDown(self):
        for s in self.sessions:   # une session de test, par son nom exact
            subprocess.call(['tmux', 'kill-session', '-t', s], stderr=subprocess.DEVNULL)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def json_de(self, outil, *args):
        r = subprocess.run([sys.executable, str(outil), str(self.ws), *args], capture_output=True, text=True,
                           env=self.env, timeout=60)
        lignes = r.stdout.strip().splitlines()
        self.assertTrue(lignes, f'aucune sortie ; stderr : {r.stderr[-500:]}')
        self.assertEqual(len(lignes), 1, f'une seule ligne JSON attendue : {r.stdout!r}')
        return json.loads(lignes[0])

    def plan(self, pas):
        V.ecrire(self.ws, 'plan-faux-moteur.json', pas)


class Etat(Base):
    def test_run_neuve(self):
        e = self.json_de(ETAT)
        for k in ('en_cours', 'phase', 'tour', 'palier_courant', 'paliers', 'preversion', 'production', 'bloque', 'derniere_passe'):
            self.assertIn(k, e)
        self.assertFalse(e['en_cours'])
        self.assertEqual((e['tour'], e['palier_courant']), (0, 1))
        self.assertEqual([p['statut'] for p in e['paliers']], ['a-faire'])
        self.assertIsNone(e['preversion'])
        self.assertIsNone(e['bloque'])

    def test_preversion_lue(self):
        V.livrer(self.ws, 1, ['S01-p01', 'S01-p02'], 'V1', 0)
        V.ecrire(self.ws, f'{D}/versions.json', {'versions': [{'version': 'V1', 'palier': 1, 'tour': 0, 'date': '2026-10-25T07:00:00Z',
                                                              'emplacement': 'test', 'statut': 'preversion'}]})
        V.ecrire(self.ws, f'{D}/avancement.json', {'phase': 'preversion', 'tour': 0, 'palier_courant': 1,
                                                  'paliers': [{'n': 1, 'statut': 'preversion'}], 'bloque': None})
        e = self.json_de(ETAT)
        self.assertEqual(e['phase'], 'preversion')
        self.assertEqual((e['preversion'] or {}).get('version'), 'V1')
        self.assertEqual((e['verification'] or {}).get('verdict'), 'PASS')

    def test_bloque_lu_dans_le_lanceur(self):
        V.ecrire(self.ws, 'state/lanceur.json', {'statut': 'bloque', 'raison': 'panne du moteur : quota-atteint',
                                                 'tmux': 'inexistante-xyz', 'passes': []})
        self.assertEqual(self.json_de(ETAT)['bloque'], 'panne du moteur : quota-atteint')

    def test_lanceur_disparu(self):
        V.ecrire(self.ws, 'state/lanceur.json', {'statut': 'en-cours', 'tmux': 'inexistante-xyz', 'passes': []})
        e = self.json_de(ETAT)
        self.assertFalse(e['en_cours'])
        self.assertIn('sans conclure', e['bloque'])

    def test_lecture_pure(self):
        avant = {p: p.stat().st_mtime_ns for p in self.tmp.rglob('*')}
        self.json_de(ETAT)
        apres = {p: p.stat().st_mtime_ns for p in self.tmp.rglob('*')}
        self.assertEqual(avant, apres)

    def test_workspace_absent(self):
        r = subprocess.run([sys.executable, str(ETAT), str(self.tmp / 'nulle-part')], capture_output=True, text=True)
        self.assertIn('indisponible', json.loads(r.stdout))


class DryRun(Base):
    def test_palier(self):
        avant = {p: p.stat().st_mtime_ns for p in self.tmp.rglob('*')}
        r = self.json_de(LANCER, '--dry-run')
        self.assertTrue(r['ok'], r)
        self.assertEqual((r['mode'], r['palier'], r['plafond'], r['moteur']), ('palier', 1, 6, 'essai'))
        self.assertTrue(r['dry_run'])
        self.assertTrue(r['tmux'].startswith('agent-lanceur-'))
        self.assertEqual(avant, {p: p.stat().st_mtime_ns for p in self.tmp.rglob('*')}, 'le dry-run a écrit')

    def test_retours(self):
        V.ecrire(self.ws, f'{D}/retours/tour-1.json', {'tour': 1, 'palier': 1, 'statut': 'a-traiter', 'retours': []})
        r = self.json_de(LANCER, '--dry-run')
        self.assertEqual((r['mode'], r['plafond'], r['tours_a_traiter']), ('retours', 6, [1]))

    def test_refus_etape_1_incomplete(self):
        (self.ws / D / 'catalogue.json').unlink()
        r = self.json_de(LANCER, '--dry-run')
        self.assertFalse(r['ok'])
        self.assertIn('catalogue.json', r['refus'])

    def test_refus_autopilote(self):
        V.ecrire(self.ws, 'state/autopilote', '')
        self.assertIn('autopilote', self.json_de(LANCER, '--dry-run')['refus'])

    def test_refus_run_close(self):
        V.ecrire(self.ws, f'{D}/revue.json', {'tours': [{'tour': 1, 'verdict': 'good', 'suite': 'arret'}]})
        self.assertIn('close', self.json_de(LANCER, '--dry-run')['refus'])

    def test_bon_puis_palier_suivant_n_est_pas_une_run_close(self):
        V.ecrire(self.ws, f'{D}/revue.json', {'tours': [{'tour': 1, 'verdict': 'good', 'suite': 'palier-suivant'}]})
        self.assertTrue(self.json_de(LANCER, '--dry-run')['ok'])

    def test_refus_rien_a_construire(self):
        V.ecrire(self.ws, f'{D}/paliers.json', {'paliers': [{'n': 1, 'titre': 'x', 'commandes': [], 'test': [], 'statut': 'production'}]})
        self.assertIn('rien à construire', self.json_de(LANCER, '--dry-run')['refus'])

    def test_refus_deja_en_cours(self):
        s = f'test-agent-occupe-{os.getpid()}'
        subprocess.check_call(['tmux', 'new-session', '-d', '-s', s, 'sleep 60'])
        self.sessions.append(s)
        V.ecrire(self.ws, 'state/lanceur.json', {'statut': 'en-cours', 'tmux': s, 'mode': 'palier'})
        self.assertIn('tourne déjà', self.json_de(LANCER, '--dry-run')['refus'])
        self.assertTrue(self.json_de(ETAT)['en_cours'])

    def test_refus_moteur_inconnu(self):
        self.assertIn('moteur inconnu', self.json_de(LANCER, '--dry-run', '--moteur', 'nimporte')['refus'])


class Superviseur(Base):
    def superviser(self, plafond=8):
        old = dict(os.environ)
        os.environ.update(self.reglages)
        try:
            spec = importlib.util.spec_from_file_location('agent_lancer', LANCER)
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            V.ecrire(self.ws, 'state/lanceur.json', {'statut': 'en-cours', 'passes': []})
            rc = m.superviser(self.ws, plafond)
        finally:
            os.environ.clear(); os.environ.update(old)
        return rc, json.loads((self.ws / 'state/lanceur.json').read_text())

    def test_relance_jusqu_au_vert(self):
        self.plan([{'rc': 1, 'progres': True}, {'rc': 1, 'progres': True}, {'rc': 0, 'progres': True}])
        rc, st = self.superviser()
        self.assertEqual((rc, st['statut'], len(st['passes'])), (0, 'fini', 3))

    def test_sans_progres(self):
        self.plan([{'rc': 1}])
        rc, st = self.superviser()
        self.assertEqual((st['statut'], len(st['passes'])), ('bloque', 3))
        self.assertIn('sans progrès', st['raison'])

    def test_quota(self):
        self.plan([{'rc': 2, 'panne': 'quota-atteint'}])
        rc, st = self.superviser()
        self.assertEqual((st['statut'], len(st['passes'])), ('bloque', 1))
        self.assertIn('quota-atteint', st['raison'])

    def test_session_morte_deux_fois(self):
        self.plan([{'rc': 2, 'panne': 'session-morte'}])
        rc, st = self.superviser()
        self.assertEqual((st['statut'], len(st['passes'])), ('bloque', 2))

    def test_entree_bloquee(self):
        self.plan([{'rc': 2, 'statut': 'bloque-entree'}])
        rc, st = self.superviser()
        self.assertIn('amont', st['raison'])

    def test_bloque_ecrit_par_le_noeud(self):
        self.plan([{'rc': 1, 'progres': True, 'bloque': 'palier 1 : 3 cycles refusés'}])
        V.ecrire(self.ws, f'{D}/avancement.json', {'phase': 'palier', 'tour': 0, 'palier_courant': 1, 'paliers': []})
        rc, st = self.superviser()
        self.assertEqual(st['raison'], 'palier 1 : 3 cycles refusés')

    def test_plafond(self):
        self.plan([{'rc': 1, 'progres': True}])
        rc, st = self.superviser(plafond=4)
        self.assertEqual((st['statut'], len(st['passes'])), ('bloque', 4))
        self.assertIn('plafond', st['raison'])


class Lancement(Base):
    def test_detache_pose_le_moteur_et_finit(self):
        self.plan([{'rc': 1, 'progres': True}, {'rc': 0, 'progres': True}])
        r = self.json_de(LANCER)
        self.assertTrue(r['ok'], r)
        self.sessions.append(r['tmux'])
        self.assertEqual((self.ws / 'state/moteur').read_text().strip(), 'essai')
        for _ in range(60):
            st = json.loads((self.ws / 'state/lanceur.json').read_text())
            if st['statut'] != 'en-cours':
                break
            time.sleep(0.5)
        self.assertEqual((st['statut'], len(st['passes'])), ('fini', 2))
        self.assertFalse(self.json_de(ETAT)['en_cours'])


if __name__ == '__main__':
    unittest.main()
