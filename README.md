# AI Fate Game

Local-first AI fate rewriting game. This repository currently contains the P0/P1 design handoff and a deliberately incomplete TypeScript engine scaffold. It is not yet a playable game.

## Start here

1. Read [AGENTS.md](AGENTS.md) and [CODEX_START_HERE.md](CODEX_START_HERE.md).
2. Read the product locks and requirements in [docs/](docs/).
3. Run `node scripts/preflight.mjs` to verify the handoff package.
4. Run `npm ci`, then implement P0 and P1 following the handoff instructions.

The original architecture, JSON schemas, and fictional demo pack are in [reference/](reference/). The initial `P1_GATE.test.ts` intentionally fails until the engine and real tests replace it. No API keys or model service are required for P0/P1.
