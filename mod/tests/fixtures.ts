// Fabriqué par tests/fabriquer-fixtures.py depuis le vrai programme. Ne pas éditer à la main.
import type { Vue } from '../types'

export const VUE_NEUF: Vue = {
 "run": "assistant-biblio-2026-10-27-090000",
 "projet": "assistant-biblio",
 "workspace": "/data/agent-runs/assistant-biblio-2026-10-27-090000",
 "etape_courante": 1,
 "etapes": [
  {
   "n": 1,
   "titre": "Concevoir",
   "resume": "Le besoin, l'accès à l'outil réel, les vraies consignes de l'utilisateur, la limite de la machine et ce qui rend un palier prêt ; puis l'agent propose seul le palier 1.",
   "sous_etapes": [
    {
     "id": "E1.1",
     "titre": "Le besoin",
     "qui": "moi",
     "etat": "en_cours",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": null,
     "citation": null,
     "sorties": [],
     "decisions": []
    },
    {
     "id": "E1.2",
     "titre": "L'accès à l'outil réel",
     "qui": "agent",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/besoin.md",
       "existe": false
      },
      {
       "chemin": "docs/agent/acces-outil.json",
       "existe": false
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.3",
     "titre": "Les consignes réelles",
     "qui": "moi",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/consignes-reelles.jsonl",
       "existe": false
      },
      {
       "chemin": "docs/agent/catalogue.json",
       "existe": false
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.4",
     "titre": "La limite de la machine",
     "qui": "agent",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/reponses.json",
       "existe": false
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.5",
     "titre": "Ce qui rend un palier prêt",
     "qui": "agent",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/reponses.json",
       "existe": false
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.6",
     "titre": "Le palier 1",
     "qui": "programme",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/paliers.json",
       "existe": false
      },
      {
       "chemin": "docs/agent/palier-1.md",
       "existe": false
      }
     ],
     "decisions": []
    }
   ],
   "etat": "ouverte"
  },
  {
   "n": 2,
   "titre": "Construire un palier",
   "resume": "Le palier se construit seul sur le serveur : ses données, l'entraînement, un vérificateur indépendant qui rejoue les vraies consignes dans le vrai outil, puis la préversion et sa fiche.",
   "sous_etapes": [
    {
     "id": "E2.1",
     "titre": "Données et entraînement",
     "qui": "programme",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/avancement.json",
       "existe": false
      }
     ],
     "decisions": []
    },
    {
     "id": "E2.2",
     "titre": "Vérification et préversion",
     "qui": "programme",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/versions.json",
       "existe": false
      }
     ],
     "decisions": []
    }
   ],
   "etat": "fermee"
  },
  {
   "n": 3,
   "titre": "Revue",
   "resume": "L'utilisateur essaie la préversion dans son outil. « Bon » la passe en production, puis palier suivant ou arrêt ; sinon ses retours relancent la construction sur ce palier.",
   "sous_etapes": [
    {
     "id": "E3.1",
     "titre": "L'essai de la préversion",
     "qui": "moi",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/revue.json",
       "existe": false
      }
     ],
     "decisions": []
    }
   ],
   "etat": "fermee"
  }
 ],
 "liens": {
  "outil": null,
  "preversion": null,
  "fiche": null
 },
 "construction": null,
 "tour": 0,
 "tours": [],
 "close": false,
 "lance_le": null,
 "palier": null,
 "version": null,
 "relance_refusee": null,
 "regles": [
  "Le moins de questions possible : seules quatre questions se posent à l'étape 1 (le besoin, l'accès à l'outil réel, la limite de la machine, ce qui rend un palier prêt). Tout le reste, tu le proposes et tu le montres.",
  "Une seule question par message ; toute question à choix est en A/B/C avec une option D « autre chose, précise-moi » écrite en clair parmi les autres.",
  "Ne pose jamais une question dont la réponse se retrouve : cherche d'abord (fichiers de la run, dossiers du projet, configs), puis dis en une ligne ce que tu as trouvé.",
  "Jamais de validation où l'utilisateur ne ferait que dire oui : sa réponse à une question vaut validation de la sous-étape, citée mot pour mot.",
  "Chaque réponse de l'utilisateur s'enregistre avec l'outil `decision`, ses mots exacts en citation, sous sa sous-étape.",
  "Réponses courtes : le résultat d'abord, en points, sans préambule ni conclusion qui répète.",
  "Quand l'utilisateur demande de revenir sur une sous-étape (souvent depuis le volet), appelle l'outil `rouvrir` avec sa raison, et reprends-la."
 ],
 "attend": {
  "quoi": "le besoin : ce que l’agent doit savoir faire, avec tes mots",
  "sous_etape": "E1.1"
 },
 "sous_etape_courante": "E1.1",
 "consigne": "Le prochain message de l'utilisateur EST le besoin (le module le garde seul, mot pour mot, dans docs/agent/besoin.md). Ne demande jamais « que veux-tu faire ? ».",
 "brief": {
  "noeud": "concevoir",
  "sys": "/opt/flux/state/agent/assistant-biblio-2026-10-27-090000/concevoir/sys.md",
  "brief": "/opt/flux/state/agent/assistant-biblio-2026-10-27-090000/concevoir/brief.md"
 },
 "neuf": true
} as Vue

export const VUE_A_VALIDER: Vue = {
 "run": "assistant-biblio-2026-10-27-090000",
 "projet": "assistant-biblio",
 "workspace": "/data/agent-runs/assistant-biblio-2026-10-27-090000",
 "etape_courante": 1,
 "etapes": [
  {
   "n": 1,
   "titre": "Concevoir",
   "resume": "Le besoin, l'accès à l'outil réel, les vraies consignes de l'utilisateur, la limite de la machine et ce qui rend un palier prêt ; puis l'agent propose seul le palier 1.",
   "sous_etapes": [
    {
     "id": "E1.1",
     "titre": "Le besoin",
     "qui": "moi",
     "etat": "validee",
     "depuis": null,
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "L’assistant doit gérer mes prêts à la voix",
     "sorties": [],
     "decisions": []
    },
    {
     "id": "E1.2",
     "titre": "L'accès à l'outil réel",
     "qui": "agent",
     "etat": "a_valider",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/besoin.md",
       "existe": true
      },
      {
       "chemin": "docs/agent/acces-outil.json",
       "existe": true
      }
     ],
     "decisions": [
      {
       "a": "2026-10-26T16:26:00Z",
       "sous_etape": "E1.2",
       "resume": "Accès par le compte de test",
       "citation": "prends le compte test",
       "option": "A"
      }
     ]
    },
    {
     "id": "E1.3",
     "titre": "Les consignes réelles",
     "qui": "moi",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/consignes-reelles.jsonl",
       "existe": false
      },
      {
       "chemin": "docs/agent/catalogue.json",
       "existe": false
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.4",
     "titre": "La limite de la machine",
     "qui": "agent",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/reponses.json",
       "existe": false
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.5",
     "titre": "Ce qui rend un palier prêt",
     "qui": "agent",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/reponses.json",
       "existe": false
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.6",
     "titre": "Le palier 1",
     "qui": "programme",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/paliers.json",
       "existe": false
      },
      {
       "chemin": "docs/agent/palier-1.md",
       "existe": false
      }
     ],
     "decisions": []
    }
   ],
   "etat": "ouverte"
  },
  {
   "n": 2,
   "titre": "Construire un palier",
   "resume": "Le palier se construit seul sur le serveur : ses données, l'entraînement, un vérificateur indépendant qui rejoue les vraies consignes dans le vrai outil, puis la préversion et sa fiche.",
   "sous_etapes": [
    {
     "id": "E2.1",
     "titre": "Données et entraînement",
     "qui": "programme",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/avancement.json",
       "existe": false
      }
     ],
     "decisions": []
    },
    {
     "id": "E2.2",
     "titre": "Vérification et préversion",
     "qui": "programme",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/versions.json",
       "existe": false
      }
     ],
     "decisions": []
    }
   ],
   "etat": "fermee"
  },
  {
   "n": 3,
   "titre": "Revue",
   "resume": "L'utilisateur essaie la préversion dans son outil. « Bon » la passe en production, puis palier suivant ou arrêt ; sinon ses retours relancent la construction sur ce palier.",
   "sous_etapes": [
    {
     "id": "E3.1",
     "titre": "L'essai de la préversion",
     "qui": "moi",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/revue.json",
       "existe": false
      }
     ],
     "decisions": []
    }
   ],
   "etat": "fermee"
  }
 ],
 "liens": {
  "outil": "https://mediatheque.example.org/",
  "preversion": null,
  "fiche": null
 },
 "construction": null,
 "tour": 0,
 "tours": [],
 "close": false,
 "lance_le": null,
 "palier": null,
 "version": null,
 "relance_refusee": null,
 "regles": [
  "Le moins de questions possible : seules quatre questions se posent à l'étape 1 (le besoin, l'accès à l'outil réel, la limite de la machine, ce qui rend un palier prêt). Tout le reste, tu le proposes et tu le montres.",
  "Une seule question par message ; toute question à choix est en A/B/C avec une option D « autre chose, précise-moi » écrite en clair parmi les autres.",
  "Ne pose jamais une question dont la réponse se retrouve : cherche d'abord (fichiers de la run, dossiers du projet, configs), puis dis en une ligne ce que tu as trouvé.",
  "Jamais de validation où l'utilisateur ne ferait que dire oui : sa réponse à une question vaut validation de la sous-étape, citée mot pour mot.",
  "Chaque réponse de l'utilisateur s'enregistre avec l'outil `decision`, ses mots exacts en citation, sous sa sous-étape.",
  "Réponses courtes : le résultat d'abord, en points, sans préambule ni conclusion qui répète.",
  "Quand l'utilisateur demande de revenir sur une sous-étape (souvent depuis le volet), appelle l'outil `rouvrir` avec sa raison, et reprends-la."
 ],
 "attend": {
  "quoi": "valider l'accès à l'outil réel",
  "sous_etape": "E1.2"
 },
 "sous_etape_courante": "E1.2",
 "consigne": "Complète docs/agent/besoin.md avec la vision (ce que l'agent final saura faire, en points). Cherche d'abord comment joindre l'outil réel et rejouer une consigne dedans (dossiers du projet, configs) ; rejoue UNE consigne pour de vrai et écris docs/agent/acces-outil.json. Une seule question si quelque chose manque, en A/B/C/D ; sinon dis ce que tu as constaté en une ligne et passe la sous-étape en validee avec la citation de l'utilisateur qui t'a donné l'accès, ou en a_valider s'il doit le confirmer.",
 "brief": {
  "noeud": "concevoir",
  "sys": "/opt/flux/state/agent/assistant-biblio-2026-10-27-090000/concevoir/sys.md",
  "brief": "/opt/flux/state/agent/assistant-biblio-2026-10-27-090000/concevoir/brief.md"
 }
} as Vue

export const VUE_QUESTION: Vue = {
 "run": "assistant-biblio-2026-10-27-090000",
 "projet": "assistant-biblio",
 "workspace": "/data/agent-runs/assistant-biblio-2026-10-27-090000",
 "etape_courante": 1,
 "etapes": [
  {
   "n": 1,
   "titre": "Concevoir",
   "resume": "Le besoin, l'accès à l'outil réel, les vraies consignes de l'utilisateur, la limite de la machine et ce qui rend un palier prêt ; puis l'agent propose seul le palier 1.",
   "sous_etapes": [
    {
     "id": "E1.1",
     "titre": "Le besoin",
     "qui": "moi",
     "etat": "validee",
     "depuis": null,
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "L’assistant doit gérer mes prêts à la voix",
     "sorties": [],
     "decisions": []
    },
    {
     "id": "E1.2",
     "titre": "L'accès à l'outil réel",
     "qui": "agent",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "oui",
     "sorties": [
      {
       "chemin": "docs/agent/besoin.md",
       "existe": true
      },
      {
       "chemin": "docs/agent/acces-outil.json",
       "existe": true
      }
     ],
     "decisions": [
      {
       "a": "2026-10-26T16:26:00Z",
       "sous_etape": "E1.2",
       "resume": "Accès par le compte de test",
       "citation": "prends le compte test",
       "option": "A"
      }
     ]
    },
    {
     "id": "E1.3",
     "titre": "Les consignes réelles",
     "qui": "moi",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "A",
     "sorties": [
      {
       "chemin": "docs/agent/consignes-reelles.jsonl",
       "existe": true
      },
      {
       "chemin": "docs/agent/catalogue.json",
       "existe": true
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.4",
     "titre": "La limite de la machine",
     "qui": "agent",
     "etat": "en_cours",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/reponses.json",
       "existe": false
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.5",
     "titre": "Ce qui rend un palier prêt",
     "qui": "agent",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/reponses.json",
       "existe": false
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.6",
     "titre": "Le palier 1",
     "qui": "programme",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/paliers.json",
       "existe": false
      },
      {
       "chemin": "docs/agent/palier-1.md",
       "existe": false
      }
     ],
     "decisions": []
    }
   ],
   "etat": "ouverte"
  },
  {
   "n": 2,
   "titre": "Construire un palier",
   "resume": "Le palier se construit seul sur le serveur : ses données, l'entraînement, un vérificateur indépendant qui rejoue les vraies consignes dans le vrai outil, puis la préversion et sa fiche.",
   "sous_etapes": [
    {
     "id": "E2.1",
     "titre": "Données et entraînement",
     "qui": "programme",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/avancement.json",
       "existe": false
      }
     ],
     "decisions": []
    },
    {
     "id": "E2.2",
     "titre": "Vérification et préversion",
     "qui": "programme",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/versions.json",
       "existe": false
      }
     ],
     "decisions": []
    }
   ],
   "etat": "fermee"
  },
  {
   "n": 3,
   "titre": "Revue",
   "resume": "L'utilisateur essaie la préversion dans son outil. « Bon » la passe en production, puis palier suivant ou arrêt ; sinon ses retours relancent la construction sur ce palier.",
   "sous_etapes": [
    {
     "id": "E3.1",
     "titre": "L'essai de la préversion",
     "qui": "moi",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/revue.json",
       "existe": false
      }
     ],
     "decisions": []
    }
   ],
   "etat": "fermee"
  }
 ],
 "liens": {
  "outil": "https://mediatheque.example.org/",
  "preversion": null,
  "fiche": null
 },
 "construction": null,
 "tour": 0,
 "tours": [],
 "close": false,
 "lance_le": null,
 "palier": null,
 "version": null,
 "relance_refusee": null,
 "regles": [
  "Le moins de questions possible : seules quatre questions se posent à l'étape 1 (le besoin, l'accès à l'outil réel, la limite de la machine, ce qui rend un palier prêt). Tout le reste, tu le proposes et tu le montres.",
  "Une seule question par message ; toute question à choix est en A/B/C avec une option D « autre chose, précise-moi » écrite en clair parmi les autres.",
  "Ne pose jamais une question dont la réponse se retrouve : cherche d'abord (fichiers de la run, dossiers du projet, configs), puis dis en une ligne ce que tu as trouvé.",
  "Jamais de validation où l'utilisateur ne ferait que dire oui : sa réponse à une question vaut validation de la sous-étape, citée mot pour mot.",
  "Chaque réponse de l'utilisateur s'enregistre avec l'outil `decision`, ses mots exacts en citation, sous sa sous-étape.",
  "Réponses courtes : le résultat d'abord, en points, sans préambule ni conclusion qui répète.",
  "Quand l'utilisateur demande de revenir sur une sous-étape (souvent depuis le volet), appelle l'outil `rouvrir` avec sa raison, et reprends-la."
 ],
 "attend": {
  "quoi": "la limite de la machine",
  "sous_etape": "E1.4"
 },
 "sous_etape_courante": "E1.4",
 "consigne": "Une question en A/B/C/D sur la taille et le temps de réponse maximaux, et la machine où l'agent tournera ; si une limite est déjà connue pour ce projet, elle est l'option A. Écris la clé `machine` de docs/agent/reponses.json (citation, taille_max_go, latence_max_s, machine). Sa réponse valide la sous-étape.",
 "brief": {
  "noeud": "concevoir",
  "sys": "/opt/flux/state/agent/assistant-biblio-2026-10-27-090000/concevoir/sys.md",
  "brief": "/opt/flux/state/agent/assistant-biblio-2026-10-27-090000/concevoir/brief.md"
 }
} as Vue

export const VUE_A_LANCER: Vue = {
 "run": "assistant-biblio-2026-10-27-090000",
 "projet": "assistant-biblio",
 "workspace": "/data/agent-runs/assistant-biblio-2026-10-27-090000",
 "etape_courante": 2,
 "etapes": [
  {
   "n": 1,
   "titre": "Concevoir",
   "resume": "Le besoin, l'accès à l'outil réel, les vraies consignes de l'utilisateur, la limite de la machine et ce qui rend un palier prêt ; puis l'agent propose seul le palier 1.",
   "sous_etapes": [
    {
     "id": "E1.1",
     "titre": "Le besoin",
     "qui": "moi",
     "etat": "validee",
     "depuis": null,
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "L’assistant doit gérer mes prêts à la voix",
     "sorties": [],
     "decisions": []
    },
    {
     "id": "E1.2",
     "titre": "L'accès à l'outil réel",
     "qui": "agent",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "oui",
     "sorties": [
      {
       "chemin": "docs/agent/besoin.md",
       "existe": true
      },
      {
       "chemin": "docs/agent/acces-outil.json",
       "existe": true
      }
     ],
     "decisions": [
      {
       "a": "2026-10-26T16:26:00Z",
       "sous_etape": "E1.2",
       "resume": "Accès par le compte de test",
       "citation": "prends le compte test",
       "option": "A"
      }
     ]
    },
    {
     "id": "E1.3",
     "titre": "Les consignes réelles",
     "qui": "moi",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "A",
     "sorties": [
      {
       "chemin": "docs/agent/consignes-reelles.jsonl",
       "existe": true
      },
      {
       "chemin": "docs/agent/catalogue.json",
       "existe": true
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.4",
     "titre": "La limite de la machine",
     "qui": "agent",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "B",
     "sorties": [
      {
       "chemin": "docs/agent/reponses.json",
       "existe": true
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.5",
     "titre": "Ce qui rend un palier prêt",
     "qui": "agent",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "A",
     "sorties": [
      {
       "chemin": "docs/agent/reponses.json",
       "existe": true
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.6",
     "titre": "Le palier 1",
     "qui": "programme",
     "etat": "validee",
     "depuis": null,
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "gate vert",
     "sorties": [
      {
       "chemin": "docs/agent/paliers.json",
       "existe": false
      },
      {
       "chemin": "docs/agent/palier-1.md",
       "existe": false
      }
     ],
     "decisions": []
    }
   ],
   "etat": "faite"
  },
  {
   "n": 2,
   "titre": "Construire un palier",
   "resume": "Le palier se construit seul sur le serveur : ses données, l'entraînement, un vérificateur indépendant qui rejoue les vraies consignes dans le vrai outil, puis la préversion et sa fiche.",
   "sous_etapes": [
    {
     "id": "E2.1",
     "titre": "Données et entraînement",
     "qui": "programme",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/avancement.json",
       "existe": false
      }
     ],
     "decisions": []
    },
    {
     "id": "E2.2",
     "titre": "Vérification et préversion",
     "qui": "programme",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/versions.json",
       "existe": false
      }
     ],
     "decisions": []
    }
   ],
   "etat": "fermee"
  },
  {
   "n": 3,
   "titre": "Revue",
   "resume": "L'utilisateur essaie la préversion dans son outil. « Bon » la passe en production, puis palier suivant ou arrêt ; sinon ses retours relancent la construction sur ce palier.",
   "sous_etapes": [
    {
     "id": "E3.1",
     "titre": "L'essai de la préversion",
     "qui": "moi",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/revue.json",
       "existe": false
      }
     ],
     "decisions": []
    }
   ],
   "etat": "fermee"
  }
 ],
 "liens": {
  "outil": "https://mediatheque.example.org/",
  "preversion": null,
  "fiche": null
 },
 "construction": null,
 "tour": 0,
 "tours": [],
 "close": false,
 "lance_le": null,
 "palier": null,
 "version": null,
 "relance_refusee": null,
 "regles": [
  "Le moins de questions possible : seules quatre questions se posent à l'étape 1 (le besoin, l'accès à l'outil réel, la limite de la machine, ce qui rend un palier prêt). Tout le reste, tu le proposes et tu le montres.",
  "Une seule question par message ; toute question à choix est en A/B/C avec une option D « autre chose, précise-moi » écrite en clair parmi les autres.",
  "Ne pose jamais une question dont la réponse se retrouve : cherche d'abord (fichiers de la run, dossiers du projet, configs), puis dis en une ligne ce que tu as trouvé.",
  "Jamais de validation où l'utilisateur ne ferait que dire oui : sa réponse à une question vaut validation de la sous-étape, citée mot pour mot.",
  "Chaque réponse de l'utilisateur s'enregistre avec l'outil `decision`, ses mots exacts en citation, sous sa sous-étape.",
  "Réponses courtes : le résultat d'abord, en points, sans préambule ni conclusion qui répète.",
  "Quand l'utilisateur demande de revenir sur une sous-étape (souvent depuis le volet), appelle l'outil `rouvrir` avec sa raison, et reprends-la."
 ],
 "attend": {
  "quoi": "lancer la construction",
  "action": "lancer"
 },
 "sous_etape_courante": null,
 "consigne": null,
 "brief": {
  "noeud": "concevoir",
  "sys": "/opt/flux/state/agent/assistant-biblio-2026-10-27-090000/concevoir/sys.md",
  "brief": "/opt/flux/state/agent/assistant-biblio-2026-10-27-090000/concevoir/brief.md"
 }
} as Vue

export const VUE_CONSTRUCTION: Vue = {
 "run": "assistant-biblio-2026-10-27-090000",
 "projet": "assistant-biblio",
 "workspace": "/data/agent-runs/assistant-biblio-2026-10-27-090000",
 "etape_courante": 2,
 "etapes": [
  {
   "n": 1,
   "titre": "Concevoir",
   "resume": "Le besoin, l'accès à l'outil réel, les vraies consignes de l'utilisateur, la limite de la machine et ce qui rend un palier prêt ; puis l'agent propose seul le palier 1.",
   "sous_etapes": [
    {
     "id": "E1.1",
     "titre": "Le besoin",
     "qui": "moi",
     "etat": "validee",
     "depuis": null,
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "L’assistant doit gérer mes prêts à la voix",
     "sorties": [],
     "decisions": []
    },
    {
     "id": "E1.2",
     "titre": "L'accès à l'outil réel",
     "qui": "agent",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "oui",
     "sorties": [
      {
       "chemin": "docs/agent/besoin.md",
       "existe": true
      },
      {
       "chemin": "docs/agent/acces-outil.json",
       "existe": true
      }
     ],
     "decisions": [
      {
       "a": "2026-10-26T16:26:00Z",
       "sous_etape": "E1.2",
       "resume": "Accès par le compte de test",
       "citation": "prends le compte test",
       "option": "A"
      }
     ]
    },
    {
     "id": "E1.3",
     "titre": "Les consignes réelles",
     "qui": "moi",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "A",
     "sorties": [
      {
       "chemin": "docs/agent/consignes-reelles.jsonl",
       "existe": true
      },
      {
       "chemin": "docs/agent/catalogue.json",
       "existe": true
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.4",
     "titre": "La limite de la machine",
     "qui": "agent",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "B",
     "sorties": [
      {
       "chemin": "docs/agent/reponses.json",
       "existe": true
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.5",
     "titre": "Ce qui rend un palier prêt",
     "qui": "agent",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "A",
     "sorties": [
      {
       "chemin": "docs/agent/reponses.json",
       "existe": true
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.6",
     "titre": "Le palier 1",
     "qui": "programme",
     "etat": "validee",
     "depuis": null,
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "gate vert",
     "sorties": [
      {
       "chemin": "docs/agent/paliers.json",
       "existe": false
      },
      {
       "chemin": "docs/agent/palier-1.md",
       "existe": false
      }
     ],
     "decisions": []
    }
   ],
   "etat": "faite"
  },
  {
   "n": 2,
   "titre": "Construire un palier",
   "resume": "Le palier se construit seul sur le serveur : ses données, l'entraînement, un vérificateur indépendant qui rejoue les vraies consignes dans le vrai outil, puis la préversion et sa fiche.",
   "sous_etapes": [
    {
     "id": "E2.1",
     "titre": "Données et entraînement",
     "qui": "programme",
     "etat": "validee",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/avancement.json",
       "existe": false
      }
     ],
     "decisions": []
    },
    {
     "id": "E2.2",
     "titre": "Vérification et préversion",
     "qui": "programme",
     "etat": "en_cours",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/versions.json",
       "existe": false
      }
     ],
     "decisions": []
    }
   ],
   "etat": "ouverte"
  },
  {
   "n": 3,
   "titre": "Revue",
   "resume": "L'utilisateur essaie la préversion dans son outil. « Bon » la passe en production, puis palier suivant ou arrêt ; sinon ses retours relancent la construction sur ce palier.",
   "sous_etapes": [
    {
     "id": "E3.1",
     "titre": "L'essai de la préversion",
     "qui": "moi",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/revue.json",
       "existe": false
      }
     ],
     "decisions": []
    }
   ],
   "etat": "fermee"
  }
 ],
 "liens": {
  "outil": "https://mediatheque.example.org/",
  "preversion": null,
  "fiche": null
 },
 "construction": {
  "en_cours": true,
  "phase": "palier",
  "tour": 0,
  "palier_courant": 1,
  "bloque": null,
  "paliers": [
   {
    "n": 1,
    "titre": "Ouvrir les vues",
    "statut": "en-cours"
   },
   {
    "n": 2,
    "titre": "Comparer",
    "statut": "a-faire"
   }
  ],
  "retours_a_traiter": [],
  "verification": {
   "verdict": "FAIL",
   "reussite": 0.7,
   "actions_a_tort": 1,
   "rejouees": 10,
   "version": "V1"
  }
 },
 "tour": 0,
 "tours": [],
 "close": false,
 "lance_le": "2026-10-26T16:26:00Z",
 "palier": 1,
 "version": null,
 "relance_refusee": null,
 "regles": [
  "Le moins de questions possible : seules quatre questions se posent à l'étape 1 (le besoin, l'accès à l'outil réel, la limite de la machine, ce qui rend un palier prêt). Tout le reste, tu le proposes et tu le montres.",
  "Une seule question par message ; toute question à choix est en A/B/C avec une option D « autre chose, précise-moi » écrite en clair parmi les autres.",
  "Ne pose jamais une question dont la réponse se retrouve : cherche d'abord (fichiers de la run, dossiers du projet, configs), puis dis en une ligne ce que tu as trouvé.",
  "Jamais de validation où l'utilisateur ne ferait que dire oui : sa réponse à une question vaut validation de la sous-étape, citée mot pour mot.",
  "Chaque réponse de l'utilisateur s'enregistre avec l'outil `decision`, ses mots exacts en citation, sous sa sous-étape.",
  "Réponses courtes : le résultat d'abord, en points, sans préambule ni conclusion qui répète.",
  "Quand l'utilisateur demande de revenir sur une sous-étape (souvent depuis le volet), appelle l'outil `rouvrir` avec sa raison, et reprends-la."
 ],
 "attend": null,
 "sous_etape_courante": "E2.2",
 "consigne": "Un vérificateur qui n'a pas construit rejoue le test du palier dans le vrai outil ; sur PASS, la préversion est livrée avec sa fiche « sait faire / ne sait pas encore ».",
 "brief": {
  "noeud": "concevoir",
  "sys": "/opt/flux/state/agent/assistant-biblio-2026-10-27-090000/concevoir/sys.md",
  "brief": "/opt/flux/state/agent/assistant-biblio-2026-10-27-090000/concevoir/brief.md"
 }
} as Vue

export const VUE_BLOQUEE: Vue = {
 "run": "assistant-biblio-2026-10-27-090000",
 "projet": "assistant-biblio",
 "workspace": "/data/agent-runs/assistant-biblio-2026-10-27-090000",
 "etape_courante": 2,
 "etapes": [
  {
   "n": 1,
   "titre": "Concevoir",
   "resume": "Le besoin, l'accès à l'outil réel, les vraies consignes de l'utilisateur, la limite de la machine et ce qui rend un palier prêt ; puis l'agent propose seul le palier 1.",
   "sous_etapes": [
    {
     "id": "E1.1",
     "titre": "Le besoin",
     "qui": "moi",
     "etat": "validee",
     "depuis": null,
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "L’assistant doit gérer mes prêts à la voix",
     "sorties": [],
     "decisions": []
    },
    {
     "id": "E1.2",
     "titre": "L'accès à l'outil réel",
     "qui": "agent",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "oui",
     "sorties": [
      {
       "chemin": "docs/agent/besoin.md",
       "existe": true
      },
      {
       "chemin": "docs/agent/acces-outil.json",
       "existe": true
      }
     ],
     "decisions": [
      {
       "a": "2026-10-26T16:26:00Z",
       "sous_etape": "E1.2",
       "resume": "Accès par le compte de test",
       "citation": "prends le compte test",
       "option": "A"
      }
     ]
    },
    {
     "id": "E1.3",
     "titre": "Les consignes réelles",
     "qui": "moi",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "A",
     "sorties": [
      {
       "chemin": "docs/agent/consignes-reelles.jsonl",
       "existe": true
      },
      {
       "chemin": "docs/agent/catalogue.json",
       "existe": true
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.4",
     "titre": "La limite de la machine",
     "qui": "agent",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "B",
     "sorties": [
      {
       "chemin": "docs/agent/reponses.json",
       "existe": true
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.5",
     "titre": "Ce qui rend un palier prêt",
     "qui": "agent",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "A",
     "sorties": [
      {
       "chemin": "docs/agent/reponses.json",
       "existe": true
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.6",
     "titre": "Le palier 1",
     "qui": "programme",
     "etat": "validee",
     "depuis": null,
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "gate vert",
     "sorties": [
      {
       "chemin": "docs/agent/paliers.json",
       "existe": false
      },
      {
       "chemin": "docs/agent/palier-1.md",
       "existe": false
      }
     ],
     "decisions": []
    }
   ],
   "etat": "faite"
  },
  {
   "n": 2,
   "titre": "Construire un palier",
   "resume": "Le palier se construit seul sur le serveur : ses données, l'entraînement, un vérificateur indépendant qui rejoue les vraies consignes dans le vrai outil, puis la préversion et sa fiche.",
   "sous_etapes": [
    {
     "id": "E2.1",
     "titre": "Données et entraînement",
     "qui": "programme",
     "etat": "validee",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/avancement.json",
       "existe": false
      }
     ],
     "decisions": []
    },
    {
     "id": "E2.2",
     "titre": "Vérification et préversion",
     "qui": "programme",
     "etat": "bloquee",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/versions.json",
       "existe": false
      }
     ],
     "decisions": []
    }
   ],
   "etat": "ouverte"
  },
  {
   "n": 3,
   "titre": "Revue",
   "resume": "L'utilisateur essaie la préversion dans son outil. « Bon » la passe en production, puis palier suivant ou arrêt ; sinon ses retours relancent la construction sur ce palier.",
   "sous_etapes": [
    {
     "id": "E3.1",
     "titre": "L'essai de la préversion",
     "qui": "moi",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/revue.json",
       "existe": false
      }
     ],
     "decisions": []
    }
   ],
   "etat": "fermee"
  }
 ],
 "liens": {
  "outil": "https://mediatheque.example.org/",
  "preversion": null,
  "fiche": null
 },
 "construction": {
  "en_cours": false,
  "phase": "palier",
  "tour": 0,
  "palier_courant": 1,
  "bloque": "3 passes sans progrès",
  "paliers": [
   {
    "n": 1,
    "titre": "Ouvrir les vues",
    "statut": "en-cours"
   },
   {
    "n": 2,
    "titre": "Comparer",
    "statut": "a-faire"
   }
  ],
  "retours_a_traiter": []
 },
 "tour": 0,
 "tours": [],
 "close": false,
 "lance_le": "2026-10-26T16:26:00Z",
 "palier": 1,
 "version": null,
 "relance_refusee": null,
 "regles": [
  "Le moins de questions possible : seules quatre questions se posent à l'étape 1 (le besoin, l'accès à l'outil réel, la limite de la machine, ce qui rend un palier prêt). Tout le reste, tu le proposes et tu le montres.",
  "Une seule question par message ; toute question à choix est en A/B/C avec une option D « autre chose, précise-moi » écrite en clair parmi les autres.",
  "Ne pose jamais une question dont la réponse se retrouve : cherche d'abord (fichiers de la run, dossiers du projet, configs), puis dis en une ligne ce que tu as trouvé.",
  "Jamais de validation où l'utilisateur ne ferait que dire oui : sa réponse à une question vaut validation de la sous-étape, citée mot pour mot.",
  "Chaque réponse de l'utilisateur s'enregistre avec l'outil `decision`, ses mots exacts en citation, sous sa sous-étape.",
  "Réponses courtes : le résultat d'abord, en points, sans préambule ni conclusion qui répète.",
  "Quand l'utilisateur demande de revenir sur une sous-étape (souvent depuis le volet), appelle l'outil `rouvrir` avec sa raison, et reprends-la."
 ],
 "attend": {
  "quoi": "construction bloquée : 3 passes sans progrès",
  "action": "lancer"
 },
 "sous_etape_courante": "E2.2",
 "consigne": "Un vérificateur qui n'a pas construit rejoue le test du palier dans le vrai outil ; sur PASS, la préversion est livrée avec sa fiche « sait faire / ne sait pas encore ».",
 "brief": {
  "noeud": "concevoir",
  "sys": "/opt/flux/state/agent/assistant-biblio-2026-10-27-090000/concevoir/sys.md",
  "brief": "/opt/flux/state/agent/assistant-biblio-2026-10-27-090000/concevoir/brief.md"
 }
} as Vue

export const VUE_REVUE: Vue = {
 "run": "assistant-biblio-2026-10-27-090000",
 "projet": "assistant-biblio",
 "workspace": "/data/agent-runs/assistant-biblio-2026-10-27-090000",
 "etape_courante": 3,
 "etapes": [
  {
   "n": 1,
   "titre": "Concevoir",
   "resume": "Le besoin, l'accès à l'outil réel, les vraies consignes de l'utilisateur, la limite de la machine et ce qui rend un palier prêt ; puis l'agent propose seul le palier 1.",
   "sous_etapes": [
    {
     "id": "E1.1",
     "titre": "Le besoin",
     "qui": "moi",
     "etat": "validee",
     "depuis": null,
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "L’assistant doit gérer mes prêts à la voix",
     "sorties": [],
     "decisions": []
    },
    {
     "id": "E1.2",
     "titre": "L'accès à l'outil réel",
     "qui": "agent",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "oui",
     "sorties": [
      {
       "chemin": "docs/agent/besoin.md",
       "existe": true
      },
      {
       "chemin": "docs/agent/acces-outil.json",
       "existe": true
      }
     ],
     "decisions": [
      {
       "a": "2026-10-26T16:26:00Z",
       "sous_etape": "E1.2",
       "resume": "Accès par le compte de test",
       "citation": "prends le compte test",
       "option": "A"
      }
     ]
    },
    {
     "id": "E1.3",
     "titre": "Les consignes réelles",
     "qui": "moi",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "A",
     "sorties": [
      {
       "chemin": "docs/agent/consignes-reelles.jsonl",
       "existe": true
      },
      {
       "chemin": "docs/agent/catalogue.json",
       "existe": true
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.4",
     "titre": "La limite de la machine",
     "qui": "agent",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "B",
     "sorties": [
      {
       "chemin": "docs/agent/reponses.json",
       "existe": true
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.5",
     "titre": "Ce qui rend un palier prêt",
     "qui": "agent",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "A",
     "sorties": [
      {
       "chemin": "docs/agent/reponses.json",
       "existe": true
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.6",
     "titre": "Le palier 1",
     "qui": "programme",
     "etat": "validee",
     "depuis": null,
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "gate vert",
     "sorties": [
      {
       "chemin": "docs/agent/paliers.json",
       "existe": true
      },
      {
       "chemin": "docs/agent/palier-1.md",
       "existe": false
      }
     ],
     "decisions": []
    }
   ],
   "etat": "faite"
  },
  {
   "n": 2,
   "titre": "Construire un palier",
   "resume": "Le palier se construit seul sur le serveur : ses données, l'entraînement, un vérificateur indépendant qui rejoue les vraies consignes dans le vrai outil, puis la préversion et sa fiche.",
   "sous_etapes": [
    {
     "id": "E2.1",
     "titre": "Données et entraînement",
     "qui": "programme",
     "etat": "validee",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/avancement.json",
       "existe": false
      }
     ],
     "decisions": []
    },
    {
     "id": "E2.2",
     "titre": "Vérification et préversion",
     "qui": "programme",
     "etat": "validee",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/versions.json",
       "existe": true
      }
     ],
     "decisions": []
    }
   ],
   "etat": "faite"
  },
  {
   "n": 3,
   "titre": "Revue",
   "resume": "L'utilisateur essaie la préversion dans son outil. « Bon » la passe en production, puis palier suivant ou arrêt ; sinon ses retours relancent la construction sur ce palier.",
   "sous_etapes": [
    {
     "id": "E3.1",
     "titre": "L'essai de la préversion",
     "qui": "moi",
     "etat": "en_cours",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/revue.json",
       "existe": false
      }
     ],
     "decisions": []
    }
   ],
   "etat": "ouverte"
  }
 ],
 "liens": {
  "outil": "https://mediatheque.example.org/",
  "preversion": "https://outil.example/preversion/V1",
  "fiche": "docs/agent/paliers/p1/fiche.md"
 },
 "construction": {
  "en_cours": false,
  "phase": "preversion",
  "tour": 0,
  "palier_courant": 1,
  "bloque": null,
  "paliers": [
   {
    "n": 1,
    "titre": "Ouvrir les vues",
    "statut": "preversion"
   },
   {
    "n": 2,
    "titre": "Comparer",
    "statut": "a-faire"
   }
  ],
  "preversion": {
   "version": "V1",
   "palier": 1,
   "tour": 0,
   "date": "2026-10-27T10:00:00Z",
   "emplacement": "https://outil.example/preversion/V1",
   "statut": "preversion"
  },
  "production": null,
  "retours_a_traiter": [],
  "verification": {
   "verdict": "PASS",
   "reussite": 0.9,
   "actions_a_tort": 0,
   "rejouees": 10,
   "version": "V1"
  }
 },
 "tour": 0,
 "tours": [],
 "close": false,
 "lance_le": "2026-10-26T16:26:00Z",
 "palier": 1,
 "version": "V1",
 "relance_refusee": null,
 "regles": [
  "Le moins de questions possible : seules quatre questions se posent à l'étape 1 (le besoin, l'accès à l'outil réel, la limite de la machine, ce qui rend un palier prêt). Tout le reste, tu le proposes et tu le montres.",
  "Une seule question par message ; toute question à choix est en A/B/C avec une option D « autre chose, précise-moi » écrite en clair parmi les autres.",
  "Ne pose jamais une question dont la réponse se retrouve : cherche d'abord (fichiers de la run, dossiers du projet, configs), puis dis en une ligne ce que tu as trouvé.",
  "Jamais de validation où l'utilisateur ne ferait que dire oui : sa réponse à une question vaut validation de la sous-étape, citée mot pour mot.",
  "Chaque réponse de l'utilisateur s'enregistre avec l'outil `decision`, ses mots exacts en citation, sous sa sous-étape.",
  "Réponses courtes : le résultat d'abord, en points, sans préambule ni conclusion qui répète.",
  "Quand l'utilisateur demande de revenir sur une sous-étape (souvent depuis le volet), appelle l'outil `rouvrir` avec sa raison, et reprends-la."
 ],
 "attend": {
  "quoi": "essayer la préversion du palier 1",
  "sous_etape": "E3.1"
 },
 "sous_etape_courante": "E3.1",
 "consigne": "Montre la fiche de la préversion et où l'essayer. L'utilisateur l'essaie dans son outil. S'il dit que c'est bon : mets en production (commande `production` de docs/agent/acces-outil.json, fiche affichée dans l'outil), écris docs/agent/production.json et le statut `production` dans paliers.json, puis demande la suite en A/B/C/D (A palier suivant : tu le proposes et le montres / B arrêt / D autre chose) et appelle l'outil `revue` verdict good avec `suite`. Sinon : reprends chaque retour (une question à la fois si un retour est ambigu), outil `retours` avec la liste (dit = ses mots exacts, consigne = ce qu'il a essayé, attendu = un critère vérifiable dans l'outil), puis outil `revue` verdict retours : la construction repart toute seule sur ce palier.",
 "brief": {
  "noeud": "concevoir",
  "sys": "/opt/flux/state/agent/assistant-biblio-2026-10-27-090000/concevoir/sys.md",
  "brief": "/opt/flux/state/agent/assistant-biblio-2026-10-27-090000/concevoir/brief.md"
 }
} as Vue

export const VUE_PALIER2: Vue = {
 "run": "assistant-biblio-2026-10-27-090000",
 "projet": "assistant-biblio",
 "workspace": "/data/agent-runs/assistant-biblio-2026-10-27-090000",
 "etape_courante": 2,
 "etapes": [
  {
   "n": 1,
   "titre": "Concevoir",
   "resume": "Le besoin, l'accès à l'outil réel, les vraies consignes de l'utilisateur, la limite de la machine et ce qui rend un palier prêt ; puis l'agent propose seul le palier 1.",
   "sous_etapes": [
    {
     "id": "E1.1",
     "titre": "Le besoin",
     "qui": "moi",
     "etat": "validee",
     "depuis": null,
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "L’assistant doit gérer mes prêts à la voix",
     "sorties": [],
     "decisions": []
    },
    {
     "id": "E1.2",
     "titre": "L'accès à l'outil réel",
     "qui": "agent",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "oui",
     "sorties": [
      {
       "chemin": "docs/agent/besoin.md",
       "existe": true
      },
      {
       "chemin": "docs/agent/acces-outil.json",
       "existe": true
      }
     ],
     "decisions": [
      {
       "a": "2026-10-26T16:26:00Z",
       "sous_etape": "E1.2",
       "resume": "Accès par le compte de test",
       "citation": "prends le compte test",
       "option": "A"
      }
     ]
    },
    {
     "id": "E1.3",
     "titre": "Les consignes réelles",
     "qui": "moi",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "A",
     "sorties": [
      {
       "chemin": "docs/agent/consignes-reelles.jsonl",
       "existe": true
      },
      {
       "chemin": "docs/agent/catalogue.json",
       "existe": true
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.4",
     "titre": "La limite de la machine",
     "qui": "agent",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "B",
     "sorties": [
      {
       "chemin": "docs/agent/reponses.json",
       "existe": true
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.5",
     "titre": "Ce qui rend un palier prêt",
     "qui": "agent",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "A",
     "sorties": [
      {
       "chemin": "docs/agent/reponses.json",
       "existe": true
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.6",
     "titre": "Le palier 1",
     "qui": "programme",
     "etat": "validee",
     "depuis": null,
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "gate vert",
     "sorties": [
      {
       "chemin": "docs/agent/paliers.json",
       "existe": true
      },
      {
       "chemin": "docs/agent/palier-1.md",
       "existe": false
      }
     ],
     "decisions": []
    }
   ],
   "etat": "faite"
  },
  {
   "n": 2,
   "titre": "Construire un palier",
   "resume": "Le palier se construit seul sur le serveur : ses données, l'entraînement, un vérificateur indépendant qui rejoue les vraies consignes dans le vrai outil, puis la préversion et sa fiche.",
   "sous_etapes": [
    {
     "id": "E2.1",
     "titre": "Données et entraînement",
     "qui": "programme",
     "etat": "en_cours",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/avancement.json",
       "existe": false
      }
     ],
     "decisions": []
    },
    {
     "id": "E2.2",
     "titre": "Vérification et préversion",
     "qui": "programme",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/versions.json",
       "existe": true
      }
     ],
     "decisions": []
    }
   ],
   "etat": "ouverte"
  },
  {
   "n": 3,
   "titre": "Revue",
   "resume": "L'utilisateur essaie la préversion dans son outil. « Bon » la passe en production, puis palier suivant ou arrêt ; sinon ses retours relancent la construction sur ce palier.",
   "sous_etapes": [
    {
     "id": "E3.1",
     "titre": "L'essai de la préversion",
     "qui": "moi",
     "etat": "a_faire",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/revue.json",
       "existe": true
      }
     ],
     "decisions": []
    }
   ],
   "etat": "fermee"
  }
 ],
 "liens": {
  "outil": "https://mediatheque.example.org/",
  "preversion": null,
  "fiche": null
 },
 "construction": {
  "en_cours": true,
  "phase": "palier",
  "tour": 1,
  "palier_courant": 2,
  "bloque": null,
  "paliers": [
   {
    "n": 1,
    "titre": "Ouvrir les vues",
    "statut": "production"
   },
   {
    "n": 2,
    "titre": "Comparer",
    "statut": "en-cours"
   }
  ],
  "retours_a_traiter": []
 },
 "tour": 1,
 "tours": [
  {
   "tour": 1,
   "palier": 1,
   "version": "V1",
   "verdict": "good",
   "date": "2026-10-26T16:26:01Z",
   "citation": "c'est bon, on continue",
   "suite": "palier-suivant"
  }
 ],
 "close": false,
 "lance_le": "2026-10-26T16:26:00Z",
 "palier": 2,
 "version": null,
 "relance_refusee": null,
 "regles": [
  "Le moins de questions possible : seules quatre questions se posent à l'étape 1 (le besoin, l'accès à l'outil réel, la limite de la machine, ce qui rend un palier prêt). Tout le reste, tu le proposes et tu le montres.",
  "Une seule question par message ; toute question à choix est en A/B/C avec une option D « autre chose, précise-moi » écrite en clair parmi les autres.",
  "Ne pose jamais une question dont la réponse se retrouve : cherche d'abord (fichiers de la run, dossiers du projet, configs), puis dis en une ligne ce que tu as trouvé.",
  "Jamais de validation où l'utilisateur ne ferait que dire oui : sa réponse à une question vaut validation de la sous-étape, citée mot pour mot.",
  "Chaque réponse de l'utilisateur s'enregistre avec l'outil `decision`, ses mots exacts en citation, sous sa sous-étape.",
  "Réponses courtes : le résultat d'abord, en points, sans préambule ni conclusion qui répète.",
  "Quand l'utilisateur demande de revenir sur une sous-étape (souvent depuis le volet), appelle l'outil `rouvrir` avec sa raison, et reprends-la."
 ],
 "attend": null,
 "sous_etape_courante": "E2.1",
 "consigne": "Lancée par le bouton du volet ou l'outil `lancer`. Rien à faire en conversation : le volet suit l'avancement.",
 "brief": {
  "noeud": "concevoir",
  "sys": "/opt/flux/state/agent/assistant-biblio-2026-10-27-090000/concevoir/sys.md",
  "brief": "/opt/flux/state/agent/assistant-biblio-2026-10-27-090000/concevoir/brief.md"
 }
} as Vue

export const VUE_CLOSE: Vue = {
 "run": "assistant-biblio-2026-10-27-090000",
 "projet": "assistant-biblio",
 "workspace": "/data/agent-runs/assistant-biblio-2026-10-27-090000",
 "etape_courante": 3,
 "etapes": [
  {
   "n": 1,
   "titre": "Concevoir",
   "resume": "Le besoin, l'accès à l'outil réel, les vraies consignes de l'utilisateur, la limite de la machine et ce qui rend un palier prêt ; puis l'agent propose seul le palier 1.",
   "sous_etapes": [
    {
     "id": "E1.1",
     "titre": "Le besoin",
     "qui": "moi",
     "etat": "validee",
     "depuis": null,
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "L’assistant doit gérer mes prêts à la voix",
     "sorties": [],
     "decisions": []
    },
    {
     "id": "E1.2",
     "titre": "L'accès à l'outil réel",
     "qui": "agent",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "oui",
     "sorties": [
      {
       "chemin": "docs/agent/besoin.md",
       "existe": true
      },
      {
       "chemin": "docs/agent/acces-outil.json",
       "existe": true
      }
     ],
     "decisions": [
      {
       "a": "2026-10-26T16:26:00Z",
       "sous_etape": "E1.2",
       "resume": "Accès par le compte de test",
       "citation": "prends le compte test",
       "option": "A"
      }
     ]
    },
    {
     "id": "E1.3",
     "titre": "Les consignes réelles",
     "qui": "moi",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "A",
     "sorties": [
      {
       "chemin": "docs/agent/consignes-reelles.jsonl",
       "existe": true
      },
      {
       "chemin": "docs/agent/catalogue.json",
       "existe": true
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.4",
     "titre": "La limite de la machine",
     "qui": "agent",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "B",
     "sorties": [
      {
       "chemin": "docs/agent/reponses.json",
       "existe": true
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.5",
     "titre": "Ce qui rend un palier prêt",
     "qui": "agent",
     "etat": "validee",
     "depuis": "2026-10-26T16:26:00Z",
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "A",
     "sorties": [
      {
       "chemin": "docs/agent/reponses.json",
       "existe": true
      }
     ],
     "decisions": []
    },
    {
     "id": "E1.6",
     "titre": "Le palier 1",
     "qui": "programme",
     "etat": "validee",
     "depuis": null,
     "valide_le": "2026-10-26T16:26:00Z",
     "citation": "gate vert",
     "sorties": [
      {
       "chemin": "docs/agent/paliers.json",
       "existe": true
      },
      {
       "chemin": "docs/agent/palier-1.md",
       "existe": false
      }
     ],
     "decisions": []
    }
   ],
   "etat": "faite"
  },
  {
   "n": 2,
   "titre": "Construire un palier",
   "resume": "Le palier se construit seul sur le serveur : ses données, l'entraînement, un vérificateur indépendant qui rejoue les vraies consignes dans le vrai outil, puis la préversion et sa fiche.",
   "sous_etapes": [
    {
     "id": "E2.1",
     "titre": "Données et entraînement",
     "qui": "programme",
     "etat": "validee",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/avancement.json",
       "existe": false
      }
     ],
     "decisions": []
    },
    {
     "id": "E2.2",
     "titre": "Vérification et préversion",
     "qui": "programme",
     "etat": "validee",
     "depuis": null,
     "valide_le": null,
     "citation": null,
     "sorties": [
      {
       "chemin": "docs/agent/versions.json",
       "existe": true
      }
     ],
     "decisions": []
    }
   ],
   "etat": "faite"
  },
  {
   "n": 3,
   "titre": "Revue",
   "resume": "L'utilisateur essaie la préversion dans son outil. « Bon » la passe en production, puis palier suivant ou arrêt ; sinon ses retours relancent la construction sur ce palier.",
   "sous_etapes": [
    {
     "id": "E3.1",
     "titre": "L'essai de la préversion",
     "qui": "moi",
     "etat": "validee",
     "depuis": null,
     "valide_le": null,
     "citation": "parfait, on s’arrête là",
     "sorties": [
      {
       "chemin": "docs/agent/revue.json",
       "existe": true
      }
     ],
     "decisions": []
    }
   ],
   "etat": "faite"
  }
 ],
 "liens": {
  "outil": "https://mediatheque.example.org/",
  "preversion": "https://outil.example/preversion/V2",
  "fiche": "docs/agent/paliers/p2/fiche.md"
 },
 "construction": {
  "en_cours": false,
  "phase": "preversion",
  "tour": 1,
  "palier_courant": 2,
  "bloque": null,
  "paliers": [
   {
    "n": 1,
    "titre": "Ouvrir les vues",
    "statut": "production"
   },
   {
    "n": 2,
    "titre": "Comparer",
    "statut": "preversion"
   }
  ],
  "preversion": {
   "version": "V2",
   "palier": 2,
   "tour": 1,
   "date": "2026-10-27T10:00:00Z",
   "emplacement": "https://outil.example/preversion/V2",
   "statut": "preversion"
  },
  "production": null,
  "retours_a_traiter": [],
  "verification": {
   "verdict": "PASS",
   "reussite": 0.9,
   "actions_a_tort": 0,
   "rejouees": 10,
   "version": "V2"
  }
 },
 "tour": 2,
 "tours": [
  {
   "tour": 1,
   "palier": 1,
   "version": "V1",
   "verdict": "good",
   "date": "2026-10-26T16:26:01Z",
   "citation": "c'est bon, on continue",
   "suite": "palier-suivant"
  },
  {
   "tour": 2,
   "palier": 2,
   "version": "V2",
   "verdict": "good",
   "date": "2026-10-26T16:26:01Z",
   "citation": "parfait, on s’arrête là",
   "suite": "arret"
  }
 ],
 "close": true,
 "lance_le": "2026-10-26T16:26:00Z",
 "palier": 2,
 "version": null,
 "relance_refusee": null,
 "regles": [
  "Le moins de questions possible : seules quatre questions se posent à l'étape 1 (le besoin, l'accès à l'outil réel, la limite de la machine, ce qui rend un palier prêt). Tout le reste, tu le proposes et tu le montres.",
  "Une seule question par message ; toute question à choix est en A/B/C avec une option D « autre chose, précise-moi » écrite en clair parmi les autres.",
  "Ne pose jamais une question dont la réponse se retrouve : cherche d'abord (fichiers de la run, dossiers du projet, configs), puis dis en une ligne ce que tu as trouvé.",
  "Jamais de validation où l'utilisateur ne ferait que dire oui : sa réponse à une question vaut validation de la sous-étape, citée mot pour mot.",
  "Chaque réponse de l'utilisateur s'enregistre avec l'outil `decision`, ses mots exacts en citation, sous sa sous-étape.",
  "Réponses courtes : le résultat d'abord, en points, sans préambule ni conclusion qui répète.",
  "Quand l'utilisateur demande de revenir sur une sous-étape (souvent depuis le volet), appelle l'outil `rouvrir` avec sa raison, et reprends-la."
 ],
 "attend": null,
 "sous_etape_courante": null,
 "consigne": null,
 "brief": {
  "noeud": "concevoir",
  "sys": "/opt/flux/state/agent/assistant-biblio-2026-10-27-090000/concevoir/sys.md",
  "brief": "/opt/flux/state/agent/assistant-biblio-2026-10-27-090000/concevoir/brief.md"
 }
} as Vue
