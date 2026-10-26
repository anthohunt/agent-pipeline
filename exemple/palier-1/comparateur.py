"""Comparateur de l'exemple : trois issues par cas.

reussi    l'assistant a fait ce qu'il fallait (bonne commande, bons paramètres), ou s'est tu / a proposé quand il le fallait
tolere    une erreur sans conséquence : il a proposé au lieu d'agir, ou n'a rien fait (l'utilisateur répète)
interdit  une action à tort : il a agi alors qu'il ne fallait pas, ou a fait une autre action que celle attendue
"""


def comparer(proposition, corrige, critere, options):
    if not isinstance(proposition, dict) or proposition.get("action") not in ("executer", "proposer", "rien"):
        return "interdit"          # une sortie illisible n'est jamais une réussite
    attendu, obtenu = corrige.get("action"), proposition.get("action")
    if attendu == "executer":
        if obtenu == "executer":
            ok = proposition.get("commande") == corrige.get("commande") and (proposition.get("args") or {}) == (corrige.get("args") or {})
            return "reussi" if ok else "interdit"
        return "tolere"
    if obtenu == "executer":
        return "interdit"          # agir alors qu'il ne fallait pas
    return "reussi" if obtenu == attendu else "tolere"
