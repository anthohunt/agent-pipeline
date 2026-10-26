import { describe, expect, mock, test } from 'claude-code/testing'
import type { On } from 'claude-code'

import {
  VUE_A_LANCER, VUE_A_VALIDER, VUE_BLOQUEE, VUE_CLOSE, VUE_CONSTRUCTION, VUE_NEUF, VUE_PALIER2, VUE_QUESTION, VUE_REVUE,
} from './fixtures'

const BASE = { sections: [{ id: 'intro', text: 'base', scope: 'shared' as const }] }
const COMPOSE = { model: 'claude-opus-5-5', promptModel: 'claude-opus-5-5', surfaces: [], tools: [], outputStyle: null, traits: [] }
const OUTIL = 'mcp__agent__'
const PANE = { plugin: 'agent', component: 'Pane', requestId: 'agent', props: { title: 'Agent', isFocused: true, bodyColumns: 90, placement: 'dock', scroll: { offset: 0, bodyRows: 60 }, view: {} } } as const
const BANDE = { plugin: 'agent', component: 'AbovePrompt', requestId: 'band', props: { bodyColumns: 200 } } as const

type Appel = { commande: string; args: Record<string, unknown> }

/** Le monde sous le mod : le programme répond par commande (vues fabriquées par le vrai programme). */
function monde(on: On, reponses: Record<string, unknown>) {
  const appels: Appel[] = []
  const outils: string[] = []
  const soumis: string[] = []
  const toasts: string[] = []
  const ouverts: string[] = []
  mock.store(on)
  mock.clock(on, { now: Date.parse('2026-10-27T09:00:00Z') })
  mock.env(on, {})
  on('fs.stat', async () => ({ value: { kind: 'file', size: 1, mtimeMs: 0 } }) as never)
  on('process.run', async (_$, e) => {
    const commande = String(e.argv[e.argv.length - 1])
    const args = JSON.parse(String(e.init?.stdin ?? '{}')) as Record<string, unknown>
    appels.push({ commande, args })
    const r = typeof reponses[commande] === 'function' ? (reponses[commande] as () => unknown)() : reponses[commande] ?? {}
    return { value: { exitCode: 0, stdout: JSON.stringify(r && (r as { refus?: string }).refus ? { ok: false, refus: (r as { refus: string }).refus } : { ok: true, resultat: r }) + '\n', stderr: '' } } as never
  })
  on('tool.register', async (_$, e) => (outils.push((e as { name: string }).name), { value: { tool: `${OUTIL}${(e as { name: string }).name}` } }) as never)
  on('ui.open', async (_$, e) => (ouverts.push(String((e as { id?: string }).id)), { value: { isPlaced: true } }) as never)
  on('ui.close', async () => ({ value: undefined }) as never)
  on('ui.toast', async (_$, e) => (toasts.push(String((e as { text?: string }).text ?? e)), { value: undefined }) as never)
  on('command.register', async () => ({ value: undefined }) as never)
  on('session.id', async () => ({ value: 'session-test' }) as never)
  on('session.start', async (_$, e) => ({ cwd: (e as { cwd: string }).cwd }) as never)
  on('prompt.compose', () => BASE)
  on('prompt.submit', async (_$, e) => (soumis.push(e.text), { text: e.text }) as never)
  return { appels, outils, soumis, toasts, ouverts }
}

const ouvrir = (args: string) => ({ command: 'agent', args, origin: { kind: 'composer' }, presentation: { isFullscreen: true, columns: 160 } }) as never
const sections = async ($: { prompt: { compose: (i: never) => Promise<{ sections: readonly { id: string; text: string }[] }> } }) => (await $.prompt.compose(COMPOSE as never)).sections

describe('seule la session rattachée est une session agent', () => {
  test('session non rattachée : même prompt système, aucun outil, outil refusé', async ($, on) => {
    const { appels, outils } = monde(on, {})
    await $.session.start({ surface: 'terminal', isInteractive: true, cwd: '/work' } as never)
    expect((await sections($ as never)).map(s => s.id)).toEqual(['intro'])
    expect(outils).toEqual([])
    expect(appels).toEqual([])
    const r = await $.tool.call({ tool: `${OUTIL}avancer`, sous_etape: 'E1.2', etat: 'a_valider' } as never)
    expect(JSON.stringify(r)).toContain("n'est pas rattachée")
  })

  test('/agent <projet> rattache : bienvenue, outils, consignes ; /agent off détache', async ($, on) => {
    const { appels, outils } = monde(on, { ouvrir: VUE_NEUF, etat: VUE_NEUF })
    await $.session.start({ surface: 'terminal', isInteractive: true, cwd: '/work' } as never)
    const r = await $.command.run(ouvrir('Assistant Biblio'))
    expect(r.text).toContain(`Agent « assistant-biblio » — run ${VUE_NEUF.run} ouverte.`)
    expect(r.text).toContain('Dis ce que l’agent doit savoir faire, avec tes mots.')
    expect(r.text).toContain('2. Construire un palier')
    expect(appels[0]).toEqual({ commande: 'ouvrir', args: { projet: 'assistant-biblio', session: 'session-test' } })
    expect(outils).toEqual(['etat', 'decision', 'avancer', 'rouvrir', 'cloturer', 'lancer', 'retours', 'revue', 'lire'])
    const s = await sections($ as never)
    expect(s.map(x => x.id)).toEqual(['intro', 'agent:protocole'])
    expect(s[1]?.text).toContain('# Mode agent (module agent)')
    expect(s[1]?.text).toContain(VUE_NEUF.workspace)
    expect(s[1]?.text).toContain('sous-étape E1.1 — Le besoin')
    expect(s[1]?.text).toContain('« autre chose, précise-moi »')
    expect(s[1]?.text).toContain(`lis ${VUE_NEUF.brief.sys} puis ${VUE_NEUF.brief.brief}`)
    expect(VUE_NEUF.brief.sys).toContain('/state/agent/')
    expect(VUE_NEUF.brief.sys).toContain('/concevoir/sys.md')
    const off = await $.command.run(ouvrir('off'))
    expect(off.text).toContain('session normale')
    expect((await sections($ as never)).map(x => x.id)).toEqual(['intro'])
  })

  test('/agent seul : la run rattachée et ce qui attend', async ($, on) => {
    monde(on, { ouvrir: VUE_QUESTION, etat: VUE_QUESTION })
    await $.command.run(ouvrir('assistant-biblio'))
    const r = await $.command.run(ouvrir(''))
    expect(r.text).toContain('la limite de la machine')
  })

  test('une session déjà rattachée se rattache seule au redémarrage', async ($, on) => {
    const { appels } = monde(on, { ouvrir: VUE_A_VALIDER, etat: VUE_A_VALIDER })
    await $.command.run(ouvrir('assistant-biblio'))
    await $.session.start({ surface: 'desktop', isInteractive: true, cwd: '/work' } as never)
    expect(appels.filter(a => a.commande === 'ouvrir').length).toBe(2)
    expect((await sections($ as never)).map(x => x.id)).toContain('agent:protocole')
  })
})

describe('étape 1 — concevoir', () => {
  test('le premier message après l’ouverture est le besoin, mot pour mot', async ($, on) => {
    const { appels } = monde(on, { ouvrir: VUE_NEUF, etat: VUE_A_VALIDER, besoin: {} })
    await $.command.run(ouvrir('assistant-biblio'))
    await $.prompt.submit({ text: 'L’assistant doit gérer mes prêts à la voix', origin: { kind: 'composer' } } as never)
    expect(appels.find(a => a.commande === 'besoin')?.args).toEqual({ run: VUE_NEUF.run, citation: 'L’assistant doit gérer mes prêts à la voix' })
    await $.prompt.submit({ text: 'A', origin: { kind: 'composer' } } as never)
    expect(appels.filter(a => a.commande === 'besoin').length).toBe(1)
  })

  test("un outil de l'agent passe au programme avec la run de la session", async ($, on) => {
    const { appels } = monde(on, { ouvrir: VUE_A_VALIDER, etat: VUE_A_VALIDER, decision: { decision: { citation: 'prends le compte test' } } })
    await $.command.run(ouvrir('assistant-biblio'))
    const r = await $.tool.call({ tool: `${OUTIL}decision`, sous_etape: 'E1.2', resume: 'Compte de test', citation: 'prends le compte test', option: 'A' } as never)
    expect(JSON.stringify(r)).toContain('prends le compte test')
    expect(appels.find(a => a.commande === 'decision')?.args).toEqual({ run: VUE_A_VALIDER.run, sous_etape: 'E1.2', resume: 'Compte de test', citation: 'prends le compte test', option: 'A' })
  })

  test('un refus du programme revient à l’agent, lisible', async ($, on) => {
    monde(on, { ouvrir: VUE_A_VALIDER, etat: VUE_A_VALIDER, cloturer: { refus: 'contrôle de l’étape 1 rouge — C4: acces-outil.json ne nomme pas l outil' } })
    await $.command.run(ouvrir('assistant-biblio'))
    const r = await $.tool.call({ tool: `${OUTIL}cloturer` } as never)
    expect(JSON.stringify(r)).toContain('C4: acces-outil.json ne nomme pas l outil')
  })

  test('volet : ce qui attend en tête, étape 1 dépliée, décision, lien de l’outil et fichier ouvrable', async ($, on) => {
    const { appels } = monde(on, { ouvrir: VUE_A_VALIDER, etat: VUE_A_VALIDER, lire: { contenu: '{"outil":"Médiathèque"}', chemin: 'docs/agent/acces-outil.json' } })
    await $.command.run(ouvrir('assistant-biblio'))
    for (const surface of ['terminal', 'desktop'] as const) {
      const ui = await $.ui.mount({ ...PANE, surface })
      expect(await ui.find({ type: 'Text', text: 'À toi :' })).toBeDefined()
      expect(await ui.find({ type: 'Text', text: /valider l'accès à l'outil réel/ })).toBeDefined()
      for (const [i, titre] of ['Concevoir', 'Construire un palier', 'Revue'].entries()) expect((await ui.find({ key: `basculer-${i + 1}` }))?.text).toContain(titre)
      expect(await ui.find({ type: 'Text', text: /^▾ 1\. Concevoir$/ })).toBeDefined()
      expect(await ui.find({ type: 'Text', text: /Accès par le compte de test/ })).toBeDefined()
      expect(await ui.find({ type: 'Text', text: /La limite de la machine/ })).toBeDefined()
      expect(await ui.find({ key: 'lien-outil' })).toBeDefined()
      expect(await ui.find({ key: 'copier-outil' })).toBeDefined()
      await ui.press({ key: 'f-docs/agent/acces-outil.json' })
      expect(appels.find(a => a.commande === 'lire')?.args).toEqual({ run: VUE_A_VALIDER.run, chemin: 'docs/agent/acces-outil.json' })
    }
  })

  test('une question en cours : son libellé court dans la bande', async ($, on) => {
    monde(on, { ouvrir: VUE_QUESTION, etat: VUE_QUESTION })
    await $.command.run(ouvrir('assistant-biblio'))
    const bande = await $.ui.mount({ ...BANDE, surface: 'terminal' } as never)
    expect(await bande.find({ type: 'Text', text: /étape 1 Concevoir · t'attend : la limite de la machine/ })).toBeDefined()
  })
})

describe('étape 2 — construire un palier', () => {
  test('le bouton Lancer appelle le programme directement, sans passer par l’agent', async ($, on) => {
    let lance = false
    const { appels, soumis, toasts } = monde(on, {
      ouvrir: VUE_A_LANCER,
      etat: () => (lance ? VUE_CONSTRUCTION : VUE_A_LANCER),
      lancer: () => ((lance = true), { ok: true, mode: 'palier', palier: 1, tmux: 't' }),
    })
    await $.command.run(ouvrir('assistant-biblio'))
    const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
    expect((await ui.find({ key: 'lancer' }))?.text).toContain('Lancer la construction')
    await ui.press({ key: 'lancer' })
    expect(appels.find(a => a.commande === 'lancer')?.args).toEqual({ run: VUE_A_LANCER.run })
    expect(soumis).toEqual([])
    expect(toasts.join(' ')).toContain('construction du palier 1 lancé')
  })

  test('suivi : paliers et dernière vérification au volet, palier dans la bande', async ($, on) => {
    monde(on, { ouvrir: VUE_CONSTRUCTION, etat: VUE_CONSTRUCTION })
    await $.command.run(ouvrir('assistant-biblio'))
    const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
    expect(await ui.find({ type: 'Text', text: /le palier se construit seul/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /^▶ palier 1 Ouvrir les vues$/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /^○ palier 2 Comparer$/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /Dernière vérification \(V1\) : FAIL · réussite 70 % · actions à tort 1/ })).toBeDefined()
    const bande = await $.ui.mount({ ...BANDE, surface: 'terminal' } as never)
    expect(await bande.find({ type: 'Text', text: /étape 2 Construire un palier · palier 1, en construction/ })).toBeDefined()
  })

  test('bloquée : la raison en rouge et le bouton Relancer', async ($, on) => {
    monde(on, { ouvrir: VUE_BLOQUEE, etat: VUE_BLOQUEE })
    await $.command.run(ouvrir('assistant-biblio'))
    const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
    expect((await ui.find({ key: 'lancer' }))?.text).toContain('Relancer')
    expect(await ui.find({ type: 'Text', text: /Bloquée : 3 passes sans progrès/ })).toBeDefined()
  })

  test('palier suivant : la construction repart, palier 2 en cours, palier 1 en production', async ($, on) => {
    monde(on, { ouvrir: VUE_PALIER2, etat: VUE_PALIER2 })
    await $.command.run(ouvrir('assistant-biblio'))
    const ui = await $.ui.mount({ ...PANE, surface: 'terminal' })
    expect(await ui.find({ type: 'Text', text: /^✓ palier 1 Ouvrir les vues$/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /^▶ palier 2 Comparer$/ })).toBeDefined()
    const bande = await $.ui.mount({ ...BANDE, surface: 'terminal' } as never)
    expect(await bande.find({ type: 'Text', text: /palier 2, en construction/ })).toBeDefined()
  })

  test('toast quand la préversion devient prête', async ($, on) => {
    let pret = false
    const { toasts } = monde(on, { ouvrir: VUE_CONSTRUCTION, etat: () => (pret ? VUE_REVUE : VUE_CONSTRUCTION) })
    await $.command.run(ouvrir('assistant-biblio'))
    pret = true
    await $.tool.call({ tool: `${OUTIL}etat` } as never)
    expect(toasts.join(' ')).toContain('préversion V1 du palier 1 est prête à essayer')
  })
})

describe('étape 3 — revue', () => {
  test('liens outil, préversion et fiche ; deux boutons qui parlent pour l’utilisateur', async ($, on) => {
    const { soumis, appels, ouverts } = monde(on, { ouvrir: VUE_REVUE, etat: VUE_REVUE, lire: { contenu: '## Sait faire', chemin: 'docs/agent/paliers/p1/fiche.md' } })
    await $.command.run(ouvrir('assistant-biblio'))
    const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
    expect(await ui.find({ type: 'Text', text: /essayer la préversion du palier 1/ })).toBeDefined()
    expect(await ui.find({ key: 'lien-outil' })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /^Préversion V1$/ })).toBeDefined()
    await ui.press({ key: 'fiche' })
    expect(appels.find(a => a.commande === 'lire')?.args).toEqual({ run: VUE_REVUE.run, chemin: 'docs/agent/paliers/p1/fiche.md' })
    expect(ouverts).toContain('agent-fichier')
    await ui.press({ key: 'retours' })
    expect(soumis).toEqual(["J'ai des retours sur la préversion, je te les donne."])
    await ui.press({ key: 'good' })
    expect(soumis[1]).toBe("J'ai essayé la préversion : c'est bon.")
    const bande = await $.ui.mount({ ...BANDE, surface: 'terminal' } as never)
    expect(await bande.find({ type: 'Text', text: /étape 3 Revue · palier 1, préversion V1 · t'attend : essayer la préversion du palier 1/ })).toBeDefined()
  })

  test('retours puis revue : arguments transmis tels quels', async ($, on) => {
    const { appels } = monde(on, { ouvrir: VUE_REVUE, etat: VUE_REVUE, retours: { tour: 1 }, revue: { tour: 1, verdict: 'retours' } })
    await $.command.run(ouvrir('assistant-biblio'))
    const liste = [{ dit: 'il ouvre la mauvaise vue', consigne: 'montre les stocks', attendu: 'la vue Stocks s’ouvre' }]
    await $.tool.call({ tool: `${OUTIL}retours`, retours: liste, citation: 'il ouvre la mauvaise vue' } as never)
    await $.tool.call({ tool: `${OUTIL}revue`, verdict: 'good', suite: 'palier-suivant', citation: "c'est bon" } as never)
    expect(appels.find(a => a.commande === 'retours')?.args).toEqual({ run: VUE_REVUE.run, retours: liste, citation: 'il ouvre la mauvaise vue' })
    expect(appels.find(a => a.commande === 'revue')?.args).toEqual({ run: VUE_REVUE.run, verdict: 'good', suite: 'palier-suivant', citation: "c'est bon" })
  })

  test('run close : plus rien n’attend, les tours se lisent', async ($, on) => {
    monde(on, { ouvrir: VUE_CLOSE, etat: VUE_CLOSE })
    await $.command.run(ouvrir('assistant-biblio'))
    const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
    expect(await ui.find({ type: 'Text', text: /Run close : le dernier palier est en production/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /tour 1 · palier 1 V1 · palier suivant/ })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: /tour 2 · palier 2 V2 · arrêt/ })).toBeDefined()
    const bande = await $.ui.mount({ ...BANDE, surface: 'terminal' } as never)
    expect(await bande.find({ type: 'Text', text: /run close/ })).toBeDefined()
  })
})
