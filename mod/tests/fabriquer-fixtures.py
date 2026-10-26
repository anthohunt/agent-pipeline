#!/usr/bin/env python3
"""Fabrique tests/fixtures.ts : des vues rendues par le VRAI programme (programme/agent.py), sur le faux moteur flux
des tests du programme. Relancer après tout changement de la vue : python3 tests/fabriquer-fixtures.py"""
import json
import pathlib
import sys

ICI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parent / 'programme' / 'tests'))
import test_agent  # noqa: E402


class Fab(test_agent.TestEtapes2et3):
    def runTest(self):
        pass


def main():
    f = Fab()
    f.setUp()
    try:
        vues = {}
        v = f.ok('ouvrir', projet='Assistant Biblio', session='s1')
        vues['VUE_NEUF'] = v
        run, ws = v['run'], v['workspace']
        f.ok('besoin', run=run, citation='L’assistant doit gérer mes prêts à la voix')
        f.ecrire(ws, 'docs/agent/acces-outil.json', {'outil': 'Médiathèque', 'url': 'https://mediatheque.example.org/'})
        f.ok('decision', run=run, sous_etape='E1.2', resume='Accès par le compte de test', citation='prends le compte test', option='A')
        f.ok('avancer', run=run, sous_etape='E1.2', etat='a_valider')
        vues['VUE_A_VALIDER'] = f.ok('etat', run=run)
        f.ok('avancer', run=run, sous_etape='E1.2', etat='validee', citation='oui')
        for x in ['docs/agent/consignes-reelles.jsonl', 'docs/agent/catalogue.json']:
            f.ecrire(ws, x, 'x')
        f.ok('avancer', run=run, sous_etape='E1.3', etat='validee', citation='A')
        vues['VUE_QUESTION'] = f.ok('etat', run=run)
        f.ecrire(ws, 'docs/agent/reponses.json', '{}')
        f.ok('avancer', run=run, sous_etape='E1.4', etat='validee', citation='B')
        f.ok('avancer', run=run, sous_etape='E1.5', etat='validee', citation='A')
        f.ecrire(ws, 'GATE_VERT_concevoir')
        f.ok('cloturer', run=run)
        vues['VUE_A_LANCER'] = f.ok('etat', run=run)
        f.ok('lancer', run=run)
        f.ecrire(ws, 'docs/agent/paliers/p1/donnees/entrainement.jsonl', '{}')
        f.ecrire(ws, 'docs/agent/paliers/p1/journal.md', 'j')
        paliers = [{'n': 1, 'titre': 'Ouvrir les vues', 'statut': 'en-cours'}, {'n': 2, 'titre': 'Comparer', 'statut': 'a-faire'}]
        f.ecrire(ws, 'ETAT_CONSTRUCTION.json', {'en_cours': True, 'phase': 'palier', 'tour': 0, 'palier_courant': 1, 'bloque': None,
                                                'paliers': paliers, 'retours_a_traiter': [],
                                                'verification': {'verdict': 'FAIL', 'reussite': 0.7, 'actions_a_tort': 1, 'rejouees': 10, 'version': 'V1'}})
        vues['VUE_CONSTRUCTION'] = f.ok('etat', run=run)
        f.ecrire(ws, 'ETAT_CONSTRUCTION.json', {'en_cours': False, 'phase': 'palier', 'tour': 0, 'palier_courant': 1,
                                                'bloque': '3 passes sans progrès', 'paliers': paliers, 'retours_a_traiter': []})
        vues['VUE_BLOQUEE'] = f.ok('etat', run=run)
        f.livrer(ws, 1, 'V1', 0, paliers=[{'n': 1, 'titre': 'Ouvrir les vues', 'statut': 'preversion'},
                                          {'n': 2, 'titre': 'Comparer', 'statut': 'a-faire'}])
        vues['VUE_REVUE'] = f.ok('etat', run=run)
        f.mettre_en_production(ws, 1, 'V1', suivant=True)
        f.ok('revue', run=run, verdict='good', suite='palier-suivant', citation="c'est bon, on continue")
        f.ecrire(ws, 'ETAT_CONSTRUCTION.json', {'en_cours': True, 'phase': 'palier', 'tour': 1, 'palier_courant': 2, 'bloque': None,
                                                'paliers': [{'n': 1, 'titre': 'Ouvrir les vues', 'statut': 'production'},
                                                            {'n': 2, 'titre': 'Comparer', 'statut': 'en-cours'}],
                                                'retours_a_traiter': []})
        vues['VUE_PALIER2'] = f.ok('etat', run=run)
        f.livrer(ws, 2, 'V2', 1, paliers=[{'n': 1, 'titre': 'Ouvrir les vues', 'statut': 'production'},
                                          {'n': 2, 'titre': 'Comparer', 'statut': 'preversion'}])
        f.ecrire(ws, 'docs/agent/production.json', {'productions': [{'palier': 2, 'version': 'V2', 'fiche': 'docs/agent/paliers/p2/fiche.md'}]})
        f.ok('revue', run=run, verdict='good', suite='arret', citation='parfait, on s’arrête là')
        vues['VUE_CLOSE'] = f.ok('etat', run=run)
        racine = str(pathlib.Path(ws).parent)
        flux = str(f.flux)
        sortie = ['// Fabriqué par tests/fabriquer-fixtures.py depuis le vrai programme. Ne pas éditer à la main.',
                  "import type { Vue } from '../types'", '']
        for nom, val in vues.items():
            texte = json.dumps(val, ensure_ascii=False, indent=1).replace(racine, '/data/agent-runs').replace(flux, '/opt/flux')
            sortie.append(f'export const {nom}: Vue = {texte} as Vue\n')
        (ICI / 'fixtures.ts').write_text('\n'.join(sortie), encoding='utf-8')
        print('fixtures.ts :', ', '.join(vues))
    finally:
        f.tearDown()


if __name__ == '__main__':
    main()
