# Exemple : l'entraînement d'un palier avec La boucle

Données et programmes **inventés** : un assistant pour la « Médiathèque de Valbourg » (fictive), palier 1 = deux commandes
(`ouvrir_prets`, `prolonger_pret`). Le sujet est un interpréteur à règles (`sujet.py`) ; le harnais, `harnais-0/regles.json`,
est ce que le chercheur améliore ; le chercheur (`chercheur.py`) est ici un script écrit à la main — un vrai run met un
agent à sa place. Les données (`fabriquer_donnees.py`) ressemblent aux données d'un palier : phrases évidentes, formes
familières, demandes à ne pas exécuter (« supprime tous mes prêts », piège : elle contient « mes prêts »), phrases qui
ne demandent rien.

```bash
cp -r exemple/palier-1 /tmp/palier-1 && cd /tmp/palier-1
export PYTHONPATH=<chemin de la-boucle-engine>
python3 -m boucle sceller donnees/entrainement.jsonl && python3 -m boucle sceller donnees/examen.jsonl
python3 -m boucle verifier chantier.json
python3 -m boucle run chantier.json            # objectif atteint : 85 sur la part tenue à part, départ à 50
```

Les données sont déjà fabriquées ; `python3 fabriquer_donnees.py` les refait à l'identique (graine fixe, puis il faut
resceller). Licences : code Apache 2.0, ce texte CC BY 4.0.
