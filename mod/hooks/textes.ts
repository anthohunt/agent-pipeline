// Les textes du mod : les consignes de l'agent (prompt système de la session rattachée) et les messages à
// l'utilisateur. Fonctions pures, testées par les tests du mod.

import type { Vue } from '../types'

export const ETAT: Record<string, string> = {
  a_faire: 'à faire', en_cours: 'en cours', a_valider: 'à valider', validee: 'validée', bloquee: 'bloquée',
}

export const QUI: Record<string, string> = { moi: 'toi', agent: 'Claude, ta réponse valide', programme: 'automatique' }

/** Le statut d'un palier (paliers.json) : ✓ production, ◆ préversion, ▶ en cours, ○ à faire. */
export const PALIER: Record<string, string> = { production: '✓', preversion: '◆', 'en-cours': '▶', 'a-faire': '○' }

/** « 2026-10-27T09:14:00Z » → « 09:14 » (heure de Paris). */
export function heure(iso: string | null | undefined): string {
  if (!iso) return ''
  try {
    return new Date(iso).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Paris' })
  } catch {
    return iso.slice(11, 16)
  }
}

/** 0.9 → « 90 % ». */
export function pourcent(x: number | null | undefined): string {
  return typeof x === 'number' ? `${Math.round(x * 100)} %` : '?'
}

export function bienvenue(v: Vue): string {
  return [
    `Agent « ${v.projet ?? v.run} » — run ${v.run} ouverte.`,
    '',
    '3 étapes : 1. Concevoir (ici, quatre questions au plus) · 2. Construire un palier (seul, sur le serveur) · 3. Revue (tu essaies la préversion dans ton outil).',
    '',
    'Dis ce que l’agent doit savoir faire, avec tes mots.',
  ].join('\n')
}

export function contexteReprise(v: Vue): string {
  const derniere = v.etapes.flatMap(e => e.sous_etapes).flatMap(s => s.decisions).slice(-1)[0]
  return [
    `Reprise de la run ${v.run} (projet ${v.projet ?? '?'}), étape ${v.etape_courante}${v.palier ? `, palier ${v.palier}` : ''}.`,
    v.sous_etape_courante ? `Sous-étape en cours : ${v.sous_etape_courante}.` : '',
    derniere ? `Dernière décision (${derniere.sous_etape}) : ${derniere.resume} — « ${derniere.citation} ».` : '',
    `Ce qui attend l'utilisateur : ${v.attend?.quoi ?? 'rien'}.`,
    `Relis ${v.brief.sys} puis ${v.brief.brief}, et les fichiers de la run, avant de répondre ; résume en 3 à 5 lignes où on en est, puis reprends.`,
  ].filter(Boolean).join('\n')
}

/** Le protocole de l'agent : ajouté au prompt système de la seule session rattachée. */
export function protocole(v: Vue): string {
  const courante = v.etapes.flatMap(e => e.sous_etapes).find(s => s.id === v.sous_etape_courante)
  const lignes = [
    '# Mode agent (module agent)',
    '',
    `Cette session conduit la run **${v.run}** de la pipeline agent (projet « ${v.projet ?? '?'} »).`,
    `Workspace de la run (travaille DEDANS, tous les chemins y sont relatifs) : ${v.workspace}`,
    '',
    '## Les 3 étapes',
    '1. **Concevoir** — en conversation, le moins de questions possible : le besoin, l’accès à l’outil réel, les consignes réelles de l’utilisateur, la limite de la machine, ce qui rend un palier prêt ; puis tu proposes et montres seul le palier 1.',
    '2. **Construire un palier** — automatique sur le serveur (bouton du volet ou outil `lancer`) : les données du palier, l’entraînement, un vérificateur indépendant qui rejoue les vraies consignes dans le vrai outil, puis la préversion et sa fiche « sait faire / ne sait pas encore ».',
    '3. **Revue** — l’utilisateur essaie la préversion dans son outil. « Bon » : tu la mets en production (fiche affichée dans l’outil, production.json, paliers.json), puis outil `revue` verdict good avec la suite (palier-suivant ou arret). Des retours : outil `retours` puis `revue` verdict retours, et la construction repart sur ce palier.',
    '',
    `## Où on en est : étape ${v.etape_courante}${v.palier ? `, palier ${v.palier}` : ''}${courante ? `, sous-étape ${courante.id} — ${courante.titre} (${ETAT[courante.etat] ?? courante.etat})` : ''}`,
    v.consigne ? `Consigne : ${v.consigne}` : '',
    v.attend ? `Ce qui attend l’utilisateur : ${v.attend.quoi}.` : 'Rien n’attend l’utilisateur.',
    v.tour ? `Tours de revue passés : ${v.tour}.` : '',
    v.version ? `Préversion à essayer : ${v.version}${v.liens.preversion ? ` (${v.liens.preversion})` : ''}.` : '',
    '',
    '## Les consignes détaillées du graphe (étape 1)',
    `Au début de l’étape 1 et à chaque reprise, lis ${v.brief.sys} puis ${v.brief.brief} : ce sont les protocoles du nœud « ${v.brief.noeud} » du graphe flux (comment joindre l’outil, recueillir les consignes réelles, choisir le palier 1). Ils priment pour le COMMENT ; ce module prime pour l’ORDRE des sous-étapes et les validations.`,
    '',
    '## Règles',
    ...v.regles.map(r => `• ${r}`),
    '• Écris à l’utilisateur avec de vraies puces « • », options A/B/C/D, jamais d’emoji, jamais de punchline.',
    '',
    '## Tes outils (module agent)',
    '• `decision` : une réponse de l’utilisateur, ses mots exacts, sous sa sous-étape.',
    '• `avancer` : E1.2 à E1.5 — en_cours → a_valider (s’il doit confirmer) → validee (sur sa réponse, citée). Les sorties de la sous-étape doivent exister ; valider ouvre la suivante.',
    '• `rouvrir` : revenir sur une sous-étape de l’étape 1, avec la raison (avant la construction seulement).',
    '• `cloturer` : fin de l’étape 1 (E1.6), passe le contrôle du moteur ; s’il est rouge, corrige et rappelle-le.',
    '• `lancer` : démarre (ou relance, si bloquée) la construction du palier sur le serveur.',
    '• `retours` puis `revue` : la revue de la préversion (étape 3).',
    '• `etat` : relire l’état ; `lire` : lire un fichier de la run.',
  ]
  return lignes.filter((l, i, a) => l !== '' || a[i - 1] !== '').join('\n')
}
