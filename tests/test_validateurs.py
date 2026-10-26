#!/usr/bin/env python3
"""Tests par mutation des contrôles de la pipeline agent en 3 étapes.

    python3 -m unittest tests.test_validateurs   (depuis la racine du dépôt)
    python3 tests/test_validateurs.py

Un workspace minimal mais complet est fabriqué dans un dossier temporaire : le palier 1
conçu, construit, revu « bon », mis en production, et le palier 2 proposé puis livré en
préversion. Il doit passer les trois contrôles. Chaque test lui applique UNE mutation et
exige que le contrôle la refuse avec le bon contrat. Un contrôle qui laisse passer une
mutation est un contrôle qui ne contrôle rien.
"""
import importlib.util, json, os, pathlib, shutil, sys, tempfile, time, unittest

ICI = pathlib.Path(__file__).resolve().parent
VAL = ICI.parent / 'validators'   # les contrôles de ce dépôt


def charger(nom):
    spec = importlib.util.spec_from_file_location(nom, VAL / f'{nom}.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CONCEVOIR = charger('agent_concevoir')
CONSTRUIRE = charger('agent_construire')
REVUE = charger('agent_revue')

D = 'docs/agent'
BESOIN = "Je veux dire à l'assistant ce que je veux faire dans la médiathèque et qu'il le fasse."
CONSIGNES = [
    {'id': 'S01-p01', 'texte': 'ouvre mes prêts', 'attendu': {'action': 'executer', 'commande': 'ouvrir_prets'}, 'source': 'pilote-1'},
    {'id': 'S01-p02', 'texte': 'prolonge mon prêt de 7 jours', 'attendu': {'action': 'executer', 'commande': 'prolonger_pret', 'args': {'jours': 7}}, 'source': 'pilote-1'},
    {'id': 'S02-p01', 'texte': 'supprime tout', 'attendu': {'action': 'proposer', 'commande': None}, 'source': 'pilote-1'},
    {'id': 'S02-p02', 'texte': 'il fait beau', 'attendu': {'action': 'rien'}, 'source': 'seance-2026-10-25'},
    {'id': 'S03-p01', 'texte': 'affiche les nouveautés', 'attendu': {'action': 'executer', 'commande': 'ouvrir_nouveautes'}, 'source': 'pilote-1'},
]


def ecrire(ws, chemin, contenu, age=None):
    p = ws / chemin
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(contenu, (dict, list)):
        contenu = json.dumps(contenu, ensure_ascii=False, indent=1)
    p.write_text(contenu, encoding='utf-8')
    if age is not None:
        os.utime(p, (time.time() - age, time.time() - age))
    return p


def jsonl(lst):
    return '\n'.join(json.dumps(x, ensure_ascii=False) for x in lst) + '\n'


def resultats(ids, rates=()):
    return [{'id': i, 'attendu': {}, 'obtenu': {}, 'ok': i not in rates, 'a_tort': False} for i in ids]


def livrer(ws, n, test, version, tour):
    """Le palier n construit, vérifié PASS et livré en préversion au tour donné."""
    pd = f'{D}/paliers/p{n}'
    ecrire(ws, f'{pd}/test.jsonl', jsonl([c for c in CONSIGNES if c['id'] in test]))
    ecrire(ws, f'{pd}/donnees/entrainement.jsonl', jsonl([{'texte': f'exemple évident {n}.{k}', 'attendu': {}} for k in range(3)]), age=600)
    ecrire(ws, f'{pd}/journal.md', f'# Palier {n}\n## Vérificateur — cycle 1\nVerdict : PASS\n')
    ecrire(ws, f'{pd}/verification.json', {
        'constructeur': 'constructeur-p%d' % n, 'verificateur': 'verificateur-p%d' % n,
        'rejoue_dans': 'http://127.0.0.1:9530', 'date': '2026-10-25T10:00:00Z', 'version': version,
        'resultats': resultats(test), 'reussite': 1.0, 'actions_a_tort': 0, 'verdict': 'PASS'})
    ecrire(ws, f'{pd}/fiche.md', f'# Version {version}\n## Sait faire\n- ouvrir\n## Ne sait pas encore\n- le reste\n')


def fabriquer(ws):
    ecrire(ws, 'WORKSPACE.txt', 'workflow: agent\nprojet: test\n', age=3600)
    ecrire(ws, f'{D}/besoin.md', f'# Le besoin\n\n> {BESOIN}\n\n## Vision\n- L\'assistant exécute les consignes.\n')
    ecrire(ws, f'{D}/reponses.json', {
        'besoin': {'citation': BESOIN}, 'acces': {'citation': 'la médiathèque de test sur le serveur'},
        'machine': {'citation': '2,4 Go et une seconde', 'taille_max_go': 2.4, 'latence_max_s': 1.0, 'machine': 'portable'},
        'critere': {'citation': 'B', 'reussite_min': 0.9, 'actions_a_tort_max': 0}})
    ecrire(ws, f'{D}/acces-outil.json', {
        'outil': 'Médiathèque', 'url': 'http://127.0.0.1:9530', 'rejouer': 'node rejouer.cjs <consigne>',
        'preversion': 'deployer-test.sh', 'production': 'deployer-prod.sh', 'fiche': 'panneau Assistant',
        'constate': {'date': '2026-10-25T09:00:00Z', 'resultat': 'ouvrir_prets a ouvert la page Mes prêts'}})
    ecrire(ws, f'{D}/consignes-reelles.jsonl', jsonl(CONSIGNES))
    ecrire(ws, f'{D}/catalogue.json', {'commandes': [{'id': c} for c in
                                                     ('ouvrir_prets', 'prolonger_pret', 'ouvrir_nouveautes')]})
    ecrire(ws, f'{D}/palier-1.md', '# Palier 1\nOuvrir et régler.\n')
    ecrire(ws, f'{D}/paliers.json', {'paliers': [
        {'n': 1, 'titre': 'Ouvrir et régler', 'commandes': ['ouvrir_prets', 'prolonger_pret'],
         'test': ['S01-p01', 'S01-p02', 'S02-p01', 'S02-p02'], 'statut': 'production'},
        {'n': 2, 'titre': 'Les nouveautés', 'commandes': ['ouvrir_prets', 'prolonger_pret', 'ouvrir_nouveautes'],
         'test': ['S01-p01', 'S03-p01'], 'statut': 'preversion'}]})
    livrer(ws, 1, ['S01-p01', 'S01-p02', 'S02-p01', 'S02-p02'], 'V2', 1)
    livrer(ws, 2, ['S01-p01', 'S03-p01'], 'V3', 2)
    ecrire(ws, f'{D}/retours/tour-1.json', {'tour': 1, 'palier': 1, 'date': '2026-10-25T08:00:00Z', 'statut': 'traite',
                                           'retours': [{'id': 'R1', 'dit': 'il ne règle pas', 'consigne': 'prolonge de 7 jours', 'attendu': 'la date de retour recule de 7 jours'}]})
    ecrire(ws, f'{D}/retours/tour-1.md', '# Tour 1\n- R1\n')
    ecrire(ws, f'{D}/versions.json', {'versions': [
        {'version': 'V1', 'palier': 1, 'tour': 0, 'date': '2026-10-25T07:00:00Z', 'emplacement': 'test', 'statut': 'preversion'},
        {'version': 'V2', 'palier': 1, 'tour': 1, 'date': '2026-10-25T09:30:00Z', 'emplacement': 'test', 'statut': 'production'},
        {'version': 'V3', 'palier': 2, 'tour': 2, 'date': '2026-10-25T11:00:00Z', 'emplacement': 'test', 'statut': 'preversion'}]})
    ecrire(ws, f'{D}/revue.json', {'tours': [
        {'tour': 1, 'palier': 1, 'version': 'V1', 'verdict': 'retours', 'date': '2026-10-25T08:00:00Z', 'citation': 'il ne règle pas', 'suite': None},
        {'tour': 2, 'palier': 1, 'version': 'V2', 'verdict': 'good', 'date': '2026-10-25T10:30:00Z', 'citation': 'c’est bon', 'suite': 'palier-suivant'}]})
    ecrire(ws, f'{D}/production.json', {'productions': [
        {'palier': 1, 'version': 'V2', 'date': '2026-10-25T10:31:00Z', 'fiche': f'{D}/paliers/p1/fiche.md'}]})
    ecrire(ws, f'{D}/avancement.json', {'phase': 'preversion', 'tour': 2, 'palier_courant': 2,
                                       'paliers': [{'n': 1, 'statut': 'production'}, {'n': 2, 'statut': 'preversion'}],
                                       'maj': '2026-10-25T11:00:00Z', 'bloque': None})


def lire(ws, chemin):
    return json.loads((ws / chemin).read_text(encoding='utf-8'))


class Base(unittest.TestCase):
    def setUp(self):
        self.ws = pathlib.Path(tempfile.mkdtemp(prefix='agent-test-'))
        fabriquer(self.ws)

    def tearDown(self):
        shutil.rmtree(self.ws, ignore_errors=True)

    def refuse(self, mod, code):
        errs = mod.validate(str(self.ws))
        self.assertTrue(any(e.startswith(code + ':') for e in errs), f'{code} attendu, reçu : {errs}')

    def modifier(self, chemin, f):
        j = lire(self.ws, chemin)
        f(j)
        ecrire(self.ws, chemin, j)


class Temoin(Base):
    def test_le_workspace_temoin_passe_les_trois_controles(self):
        for mod in (CONCEVOIR, CONSTRUIRE, REVUE):
            self.assertEqual(mod.validate(str(self.ws)), [], mod.__name__)


class Concevoir(Base):
    def test_livrable_manquant(self):
        (self.ws / D / 'palier-1.md').unlink()
        self.refuse(CONCEVOIR, 'C1')

    def test_reponse_sans_citation(self):
        self.modifier(f'{D}/reponses.json', lambda j: j['acces'].update(citation=''))
        self.refuse(CONCEVOIR, 'C2')

    def test_critere_hors_bornes(self):
        self.modifier(f'{D}/reponses.json', lambda j: j['critere'].update(reussite_min=1.5))
        self.refuse(CONCEVOIR, 'C2')

    def test_machine_sans_limite(self):
        self.modifier(f'{D}/reponses.json', lambda j: j['machine'].update(taille_max_go=None, latence_max_s=None))
        self.refuse(CONCEVOIR, 'C2')

    def test_besoin_reformule(self):
        ecrire(self.ws, f'{D}/besoin.md', '# Le besoin\nL\'assistant pilote la médiathèque.\n')
        self.refuse(CONCEVOIR, 'C3')

    def test_acces_jamais_essaye(self):
        self.modifier(f'{D}/acces-outil.json', lambda j: j.pop('constate'))
        self.refuse(CONCEVOIR, 'C4')

    def test_acces_sans_rejeu(self):
        self.modifier(f'{D}/acces-outil.json', lambda j: j.update(rejouer=''))
        self.refuse(CONCEVOIR, 'C4')

    def test_consigne_generee(self):
        c = dict(CONSIGNES[0], id='G1', source='générée par un agent')
        ecrire(self.ws, f'{D}/consignes-reelles.jsonl', jsonl(CONSIGNES + [c]))
        self.refuse(CONCEVOIR, 'C5')

    def test_consigne_generee_autorisee(self):
        c = dict(CONSIGNES[0], id='G1', source='générée par un agent')
        ecrire(self.ws, f'{D}/consignes-reelles.jsonl', jsonl(CONSIGNES + [c]))
        self.modifier(f'{D}/reponses.json', lambda j: j.update(consignes={'generees_autorisees': True, 'citation': 'tu les generes'}))
        self.assertEqual(CONCEVOIR.validate(str(self.ws)), [])

    def test_consigne_generee_autorisee_sans_citation(self):
        c = dict(CONSIGNES[0], id='G1', source='générée par un agent')
        ecrire(self.ws, f'{D}/consignes-reelles.jsonl', jsonl(CONSIGNES + [c]))
        self.modifier(f'{D}/reponses.json', lambda j: j.update(consignes={'generees_autorisees': True}))
        self.refuse(CONCEVOIR, 'C5')

    def test_consigne_en_double(self):
        ecrire(self.ws, f'{D}/consignes-reelles.jsonl', jsonl(CONSIGNES + [CONSIGNES[0]]))
        self.refuse(CONCEVOIR, 'C5')

    def test_action_inconnue(self):
        c = dict(CONSIGNES[0], id='X1', attendu={'action': 'repeter'})
        ecrire(self.ws, f'{D}/consignes-reelles.jsonl', jsonl(CONSIGNES + [c]))
        self.refuse(CONCEVOIR, 'C5')

    def test_commande_attendue_hors_catalogue(self):
        self.modifier(f'{D}/catalogue.json', lambda j: j.update(commandes=[{'id': 'ouvrir_prets'}, {'id': 'ouvrir_nouveautes'}]))
        self.refuse(CONCEVOIR, 'C6')

    def test_palier_1_absent(self):
        self.modifier(f'{D}/paliers.json', lambda j: j.update(paliers=j['paliers'][1:]))
        self.refuse(CONCEVOIR, 'C7')

    def test_palier_1_sans_test(self):
        self.modifier(f'{D}/paliers.json', lambda j: j['paliers'][0].update(test=[]))
        self.refuse(CONCEVOIR, 'C7')

    def test_palier_1_teste_une_commande_hors_palier(self):
        self.modifier(f'{D}/paliers.json', lambda j: j['paliers'][0]['test'].append('S03-p01'))
        self.refuse(CONCEVOIR, 'C7')

    def test_palier_1_test_inconnu(self):
        self.modifier(f'{D}/paliers.json', lambda j: j['paliers'][0]['test'].append('INCONNU'))
        self.refuse(CONCEVOIR, 'C7')


class Construire(Base):
    def test_avancement_hors_contrat(self):
        self.modifier(f'{D}/avancement.json', lambda j: j.update(phase='jalons'))
        self.refuse(CONSTRUIRE, 'C1')

    def test_palier_pas_encore_livre(self):
        self.modifier(f'{D}/paliers.json', lambda j: j['paliers'][1].update(statut='en-cours'))
        self.refuse(CONSTRUIRE, 'C2')

    def test_tous_en_production(self):
        self.modifier(f'{D}/paliers.json', lambda j: j['paliers'][1].update(statut='production'))
        self.refuse(CONSTRUIRE, 'C2')

    def test_test_change_en_cours(self):
        ecrire(self.ws, f'{D}/paliers/p2/test.jsonl', jsonl([CONSIGNES[0]]))
        self.refuse(CONSTRUIRE, 'C3')

    def test_phrase_de_test_generee(self):
        fausse = dict(CONSIGNES[4], texte='montre-moi les nouveautés stp')
        ecrire(self.ws, f'{D}/paliers/p2/test.jsonl', jsonl([CONSIGNES[0], fausse]))
        self.refuse(CONSTRUIRE, 'C3')

    def test_sans_donnees(self):
        (self.ws / D / 'paliers/p2/donnees/entrainement.jsonl').unlink()
        self.refuse(CONSTRUIRE, 'C4')

    def test_fuite_du_test_dans_l_entrainement(self):
        ecrire(self.ws, f'{D}/paliers/p2/donnees/entrainement.jsonl', jsonl([{'texte': 'affiche les nouveautés'}]), age=600)
        self.refuse(CONSTRUIRE, 'C4')

    def test_verificateur_est_le_constructeur(self):
        self.modifier(f'{D}/paliers/p2/verification.json', lambda j: j.update(verificateur=j['constructeur']))
        self.refuse(CONSTRUIRE, 'C5')

    def test_consigne_non_rejouee(self):
        self.modifier(f'{D}/paliers/p2/verification.json', lambda j: j.update(resultats=j['resultats'][:1], reussite=1.0))
        self.refuse(CONSTRUIRE, 'C5')

    def test_reussite_declaree_fausse(self):
        self.modifier(f'{D}/paliers/p2/verification.json', lambda j: j.update(resultats=resultats(['S01-p01', 'S03-p01'], rates=['S03-p01'])))
        self.refuse(CONSTRUIRE, 'C5')

    def test_pass_sous_le_critere(self):
        self.modifier(f'{D}/paliers/p2/verification.json', lambda j: j.update(
            resultats=resultats(['S01-p01', 'S03-p01'], rates=['S03-p01']), reussite=0.5))
        self.refuse(CONSTRUIRE, 'C5')

    def test_action_a_tort_au_dela_du_critere(self):
        def f(j):
            j['resultats'][0]['a_tort'] = True
            j['actions_a_tort'] = 1
        self.modifier(f'{D}/paliers/p2/verification.json', f)
        self.refuse(CONSTRUIRE, 'C5')

    def test_verification_perimee(self):
        os.utime(self.ws / D / 'paliers/p2/verification.json', (time.time() - 900, time.time() - 900))
        self.refuse(CONSTRUIRE, 'C6')

    def test_retours_non_verifies(self):
        ecrire(self.ws, f'{D}/retours/tour-3.json', {'tour': 3, 'palier': 2, 'date': '2026-10-25T12:00:00Z', 'statut': 'traite',
                                                    'retours': [{'id': 'R1', 'dit': 'x', 'attendu': 'y'}]})
        self.refuse(CONSTRUIRE, 'C6')

    def test_fiche_incomplete(self):
        ecrire(self.ws, f'{D}/paliers/p2/fiche.md', '# V3\n## Sait faire\n- ouvrir\n')
        self.refuse(CONSTRUIRE, 'C7')

    def test_version_du_tour_absente(self):
        self.modifier(f'{D}/versions.json', lambda j: j.update(versions=j['versions'][:2]))
        self.refuse(CONSTRUIRE, 'C8')

    def test_version_livree_en_production(self):
        self.modifier(f'{D}/versions.json', lambda j: j['versions'][2].update(statut='production'))
        self.refuse(CONSTRUIRE, 'C8')

    def test_tour_en_attente(self):
        self.modifier(f'{D}/retours/tour-1.json', lambda j: j.update(statut='a-traiter'))
        self.refuse(CONSTRUIRE, 'C9')

    def test_journal_sans_pass(self):
        ecrire(self.ws, f'{D}/paliers/p2/journal.md', '# Palier 2\nVérificateur : FAIL\n')
        self.refuse(CONSTRUIRE, 'C10')


class Revue(Base):
    def test_revue_absente(self):
        (self.ws / D / 'revue.json').unlink()
        self.refuse(REVUE, 'C1')

    def test_citation_vide(self):
        self.modifier(f'{D}/revue.json', lambda j: j['tours'][1].update(citation=' '))
        self.refuse(REVUE, 'C1')

    def test_tours_mal_numerotes(self):
        self.modifier(f'{D}/revue.json', lambda j: j['tours'][1].update(tour=5))
        self.refuse(REVUE, 'C1')

    def test_version_inconnue(self):
        self.modifier(f'{D}/revue.json', lambda j: j['tours'][0].update(version='V9'))
        self.refuse(REVUE, 'C2')

    def test_version_d_un_autre_tour(self):
        self.modifier(f'{D}/revue.json', lambda j: j['tours'][1].update(version='V1'))
        self.refuse(REVUE, 'C2')

    def test_retours_sans_fichier(self):
        (self.ws / D / 'retours/tour-1.json').unlink()
        self.refuse(REVUE, 'C3')

    def test_retour_sans_attendu(self):
        self.modifier(f'{D}/retours/tour-1.json', lambda j: j['retours'][0].update(attendu=''))
        self.refuse(REVUE, 'C3')

    def test_good_sans_production(self):
        ecrire(self.ws, f'{D}/production.json', {'productions': []})
        self.refuse(REVUE, 'C4')

    def test_good_sans_suite(self):
        self.modifier(f'{D}/revue.json', lambda j: j['tours'][1].update(suite=None))
        self.refuse(REVUE, 'C4')

    def test_good_palier_pas_en_production(self):
        self.modifier(f'{D}/paliers.json', lambda j: j['paliers'][0].update(statut='preversion'))
        self.refuse(REVUE, 'C4')

    def test_palier_suivant_absent(self):
        self.modifier(f'{D}/paliers.json', lambda j: j.update(paliers=j['paliers'][:1]))
        self.refuse(REVUE, 'C5')

    def test_arret_suivi_d_un_tour(self):
        def f(j):
            j['tours'][1]['suite'] = 'arret'
            j['tours'].append({'tour': 3, 'palier': 2, 'version': 'V3', 'verdict': 'retours',
                               'date': '2026-10-25T12:00:00Z', 'citation': 'encore'})
        self.modifier(f'{D}/revue.json', f)
        self.refuse(REVUE, 'C5')


if __name__ == '__main__':
    unittest.main()
