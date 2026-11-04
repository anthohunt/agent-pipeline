**English** · [Français](README.fr.md)

# agent-pipeline

A three-stage agent pipeline that builds a specialised agent **step by step** (*paliers*), the way software is built: a
first version that knows little but does it well, then increasingly complete versions, each one tried by the user in
their real tool before it goes to production.

| # | Stage | Mode | End-of-stage check |
|---|---|---|---|
| 1 | **Design** | in conversation, four questions at most | `agent-concevoir` |
| 2 | **Build a step** | autonomous, on a server, restarted until green | `agent-construire` |
| 3 | **Review** | in conversation (human gate) | `agent-revue` |

1. **Design**: the need (word for word), access to the real tool (established by actually replaying an instruction), the
   user's **real instructions** (never generated, unless a quoted decision says otherwise), the machine's limit, what
   makes a step ready; then the agent **proposes and shows step 1 on its own**: about ten commands and their test.
2. **Build a step**: a builder writes the step's data and trains the agent; an **independent verifier** (a fresh agent
   that built nothing) replays each test instruction in the real tool, counts what the tool *actually* did, and returns
   PASS or FAIL against the user's criterion; delivery as a **preview**, with its "can do / cannot do yet" sheet. Nothing
   goes to production at this stage.
3. **Review**: the user tries the preview. "Good" puts it in production, then comes the next step (proposed and shown)
   or a stop; feedback, kept word for word, restarts the build on that step.

Each stage has an **automatic check** (`validators/`) that judges its deliverables: while it is red, the next stage
does not start. The build check recomputes the success rate and the wrongful actions from the replayed results: a
verdict that does not match makes the node fail.

> The skills, docs, code comments and user-facing strings are in French.

## What is in the repository

| Folder | Content |
|---|---|
| `workflows/` | the graph `agent.json` (the 3 nodes) |
| `skills/` | the agents' instructions, one folder each (`<name>/SKILL.md`): `agent-concevoir`, `agent-construire` (the lead), `agent-construire.1` (the builder), `agent-construire.2` (the verifier), `agent-revue`, `agent-start` (fallback path) |
| `validators/` | the end-of-stage checks (`agent_concevoir.py`, `agent_construire.py`, `agent_revue.py`, `agent_commun.py`) |
| `tools/` | the stage 2 launcher (`agent-lancer.py`, which restarts it until green) and its status (`agent-etat.py`, one JSON line) |
| `mod/` | a Claude Code mod: tracking pane, band above the prompt, user decisions kept word for word (`/agent <project>`) |
| `docs/contrat.md` | the file contract between graph, tools and module |
| `exemple/` | `demo.sh` (end-to-end demonstration, no account needed) and `palier-1/` (training one step with La boucle, no AI model) |
| `tests/` | tests of the checks (by mutation), the launcher and the status tool |

## Dependencies: two repositories by the same author

### The flux engine

The pipeline does not run alone: it is played by [**flux**](https://github.com/anthohunt/flux), an agent pipeline engine
(separate repository, Apache 2.0). It reads the graphs, injects the instructions, starts the agents in Claude Code
sessions and runs the checks. This repository does not copy it: clone it into `vendor/flux` (or elsewhere, and set its
path in `FLUX_HOME`).

### La boucle (training)

Stage 2 trains the agent of a step with the [**La boucle engine**](https://github.com/anthohunt/la-boucle-engine)
(repository `la-boucle-engine`, Apache 2.0, Python standard library only, public command `python3 -m boucle …`): measure,
read the mistakes, try an idea, keep what improves the score; a **held-out share** of the step's data acts as the
engine's exam, which the researcher never sees. Without this repository, the build stage cannot train an agent; stages 1
and 3, the checks, the launcher and the demonstration work without it, except the last stage of `exemple/demo.sh`.
Clone it into `vendor/la-boucle-engine` (or set `BOUCLE_HOME`), or run
`pip install git+https://github.com/anthohunt/la-boucle-engine`. The step's test (the real instructions) **never** enters
the engine: only the verifier replays it.

## Install

Requirements: Linux or macOS, `git`, Python 3.10+, `pip`. To run real agents: `tmux` and Claude Code signed in to an
account.

```bash
git clone https://github.com/anthohunt/agent-pipeline agent-pipeline
cd agent-pipeline
git clone https://github.com/anthohunt/flux vendor/flux                          # the engine (see its own README)
git clone https://github.com/anthohunt/la-boucle-engine vendor/la-boucle-engine  # training
python3 -m pip install -r vendor/flux/requirements.txt                           # jsonschema
cp .env.example .env                                                             # then adapt the paths
set -a; . ./.env; set +a
```

Check the install:

```bash
python3 "$FLUX_HOME/runtime/verifier-graphes.py" workflows/*.json   # → GRAPHES CONFORMES
python3 -m unittest discover -s tests                              # checks, launcher, status
python3 -m unittest discover -s mod/programme/tests                 # module program
bash exemple/demo.sh                                                # end-to-end demonstration
```

`exemple/demo.sh` creates a run called "assistant-biblio" (an invented project), writes the brief of the design node with
its instructions, shows the stage 1 check red on an empty run and then all three checks green on a finished sample run,
reads the build status, asks the launcher what it would do, then trains one step with La boucle. **All of this runs
without an account.** What follows (the design conversation and the build agents) requires Claude Code signed in.

## Usage

1. **New run**: in Claude Code, with the mod, `/agent <project>`; without the mod, the `/agent-start` skill
   (created by `python3 $FLUX_HOME/runtime/new-run.py agent '<project>'`).
2. **Design** in the same session: the four questions, then the proposed step 1.
3. **Build**: `python3 tools/agent-lancer.py <workspace>` starts stage 2 detached (one step, or one round of feedback)
   and restarts it until the check is green; `python3 tools/agent-etat.py <workspace>` tells you where it stands.
4. **Review**: the `agent-revue` skill (or the mod's pane); "good" puts it in production, feedback restarts the build.

## Settings

Everything that depends on the machine goes through environment variables, listed with sample values in `.env.example`:
location of the engines (`FLUX_HOME`, `BOUCLE_HOME`), what flux reads to play this pipeline (`FLUX_WORKFLOWS_DIR`,
`FLUX_SKILLS_DIR`, `FLUX_VALIDATORS_PATH`), the agents' account (`AGENT_MOTEUR`, an engine from flux's `moteurs.json`),
prefix for heavy commands (`AGENT_LIMITEUR`).

## What this pipeline does not do

It provides neither the tool the agent must drive nor a model: the user gives access to **their** real tool and states
the limit of **their** machine; an example that calls a paid AI model stops at the stage that requires an account.

## Licenses

- **Code** (Python, TypeScript, shell, JSON graph): [Apache 2.0](LICENSE), see [NOTICE](NOTICE).
- **Text, documents and diagrams** (instructions in `skills/*/SKILL.md`, `docs/`, README, graph text):
  [CC BY 4.0](LICENSE-docs). You may reuse and adapt them, crediting the author, Anthony Hunt.
- Third-party dependencies and their licenses: [THIRD-PARTY.md](THIRD-PARTY.md).

Author: Anthony Hunt.
