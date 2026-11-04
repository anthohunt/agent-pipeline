# Third-party dependencies

This repository redistributes no third-party library. The components below are installed separately by the user, when
needed.

| Component | Role | License | Required |
|---|---|---|---|
| flux (pipeline engine, separate repository by the same author) | plays the graph, starts the agents, runs the checks | Apache 2.0 | yes |
| la-boucle-engine (training engine, separate repository by the same author) | trains the agent of a step, judges on a held-out share | Apache 2.0 | for the build stage |
| Python 3.10+ (standard library) | tools, checks, module program | PSF | yes |
| jsonschema | graph validation by the flux engine | MIT | yes (through flux) |
| tmux | detached sessions of the stage 2 launcher | ISC | to run agents |
| Claude Code (Anthropic) | the agents; the `mod/` module is a Claude Code mod | Anthropic's terms (not open source) | to run agents |

All these licenses are compatible with the Apache 2.0 license of the code in this repository: nothing is copied or
statically linked.
