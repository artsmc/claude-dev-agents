# /enumerated-menu-pick-and-sweep

> Use whenever you're about to present Mark with consequential choices, questions, or tradeoffs — structure them as a numbered or lettered menu so a bare reply counts as a full selection, and use this to read his terse picks ("go with B", "1. yes 2. thats fine 3. just aws", "do 1-3, 4 wont be needed because...").

## What it does

A two-sided protocol for decision-making with Mark. Output side: any consequential choice set gets shaped as a numbered/lettered menu, one decision per line, so his whole reply can be a single character. Input side: a grammar for reading his terse picks — a bare `B` is a full committed selection (execute, don't re-confirm); riders bolted onto a pick ("option 1 and update envs when your done") are part of the same instruction; multi-item sweeps get resolved index-by-index against your menu; ranged picks with a because-clause ("1-3, 4 wont be needed because...") are final scope cuts; and when Mark authors his own `#`-numbered list, each line is an independent directive to apply verbatim (skipped numbers stay skipped).

## When it triggers

- You are about to ask Mark several questions or present tradeoffs — restructure as a menu first
- One-token replies against a list you just gave: "go with B", "lets go with 2", "c one big commit"
- A pick with a rider: "1. yes, and execute it"
- A sweep answering every numbered point at once: "1. yes 2. thats fine 3. just aws 4. whats the mcp server? 5. minimal"
- A ranged pick with a scope-cut reason: "do 1-3, 4 wont be needed because this is a small application"
- Mark writing his own numbered decision list across a spec ("#1 draw a mermaid uml... #4 the OTP from sentient-monorepo is the pattern")

## Usage

Behavioral skill — auto-triggers from its description both when the agent is about to present choices and when a terse pick arrives. `/enumerated-menu-pick-and-sweep` forces it. A cue hook exists at `hooks/reasoning-skills/` but is not wired.

## Context cost

Description always in context (~860 chars); SKILL.md body loads on trigger (~7k chars); `references/examples.md` (~2.6k chars) loads on demand when a terse reply maps ambiguously onto the menu.

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | Menu-shaping rules + the pick/rider/sweep/range grammar |
| `references/examples.md` | Verbatim pick examples + misread/correction table |
| `evals/trigger-eval.json` | Trigger-accuracy eval cases |

## Related skills

- **steer-and-correct-the-agent** — handles Mark's single terse directives once a pick is in motion ("yes", "no replace X with Y"); this skill handles picks that only resolve against a labeled list.
- **scope-question-and-delegate** — decides WHICH questions are worth asking; this skill formats them and reads the answers.
- **research-gated-build-plan** — where a sweep's scope cuts get recorded into the larger plan.
