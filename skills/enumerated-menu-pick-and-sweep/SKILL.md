---
name: enumerated-menu-pick-and-sweep
description: Use whenever you're about to present Mark with consequential choices, questions, or tradeoffs — structure them as a numbered or lettered menu so a bare reply counts as a full selection, and use this to read his terse picks. Triggers on one-token replies that only resolve against a labeled list you just gave ('go with B', 'lets go with 2', 'run option B', 'c one big commit'), picks carrying a rider ('option 1 and update envs when your done', '1. yes, and execute it'), multi-item sweeps answering every numbered point at once ('1. yes 2. thats fine 3. just aws 4. whats the mcp server? 5. minimal'), ranged picks with a because-clause scope-cut ('do 1-3, 4 wont be needed because...'), and Mark authoring his own numbered decision list to apply across a spec. Format choices as a menu — a bare letter is uninterpretable unless you offered the list first.
---

# Offer Choices As An Enumerated Menu, Resolve Picks Item-By-Item

Mark decides by picking from a list. He does not want a wall of prose he has to parse and reply to in sentences — he wants you to do the structuring work so his answer can be a single character. When you surface consequential choices, questions, or findings, lay them out as a numbered or lettered menu; then he sweeps that menu item-by-item, accepting or cutting each one with a one-clause reason and pinning the single thing that actually matters. A bare `B` or `#2` is a FULL selection, but it is uninterpretable unless a labeled list came first — so the menu shape is your responsibility, and reading his terse picks correctly is the rest of this skill.

## 1. Shape your own output as an enumerated menu — make a bare letter a valid answer
Whenever you are about to present consequential choices, open questions, tradeoffs, or findings, do NOT bury them in prose. Restructure them as a numbered (`1. 2. 3.`) or lettered (`A. B. C.`) list, one decision per line, each line self-contained. The test: could Mark resolve this whole message by typing `B`, `option 1`, or `1. yes 2. no`? If not, you have under-structured it. This is what lets him reply `run option B` or `c one big commit` — the letter only carries meaning because you labeled the options first. Keep each item to a single decision; don't fuse two choices onto one number.

## 2. A bare letter/number IS the selection — execute it, don't re-ask
When his reply only makes sense against a list you just offered — `go with B`, `lets go with #2`, `Option B`, `run option B`, `option 1` — that is a complete, committed choice. Map it back to the exact menu item and act on it. Do not re-explain the option, re-ask for confirmation, or re-present the menu. The whole point of the menu was to make his reply this cheap; honor it by moving immediately.

## 3. Parse the rider attached to the pick
His picks often carry a second clause bolted onto the chosen item — a follow-on action or an inline answer:
- `option 1 and update envs when your done`
- `1. yes, and execute it`
- `c one big commit`
Treat the rider as part of the same instruction: do the selected option AND the appended directive in one move. The rider is scoped to that item — `update envs when your done` is the tail of choosing option 1, not a separate request to negotiate.

## 4. Resolve a multi-item sweep — answer every numbered point in one pass
When he answers several of your numbered items at once, walk his reply index-by-index against your menu and resolve each independently:
- `1. yes multi tenant, 2.thats fine, 3 just aws manage everything, 4.whats the mcp server for? 5. minimal`
Here `1` is an accept, `2` is an accept, `3` is a constraint, `4` is a question back at YOU (answer it, don't treat it as resolved), `5` is a parameter. Match his numbers to yours exactly; a terse `thats fine` against item 2 means item 2 is settled. If one of his numbered replies is a question (`4.whats the mcp server for?`), surface the answer before proceeding on that item — it is the one piece still open.

## 5. Honor a ranged selection and its because-clause scope-cut
He selects spans and prunes the remainder with an explicit reason:
- `lets do 1-3, 4 wont be needed because this is a small application`
`1-3` accepts items 1, 2, and 3 as a block. The `4 wont be needed because...` is a deliberate scope cut — drop item 4 and treat the because-clause as the recorded justification, not a point to argue back. When he gives a reason for cutting, the reason is final; don't re-pitch the dropped item. Reflect the cut in whatever plan/spec/tickets follow so it can't creep back in.

## 6. When HE authors the numbered list, it is the spec — apply each item across the artifact
Mark frequently writes his own `#`-numbered list of decisions to apply across a spec sheet or codebase. Each numbered line is a directive; sweep them top to bottom and apply every one:
- `#1 in your spec sheet draw a mermaid uml of the schema. #2 same add a visual uml mermaid of the api. #4 the OTP from sentient-monorepo is the pattern we should match. #5 chat session persistance will be handled by postgres no need for dyanamo. #7 case should use sentient-monorepo as its api source of truth. #8 instead of linear we will use sentient-monrepo`
Note that his numbering can skip (`#1 #2 #4 #5 #7 #8`) — do not invent or fill the gaps, just resolve the items he actually wrote. Each `#N` is independent: some are tasks (`draw a mermaid uml`), some are source-of-truth declarations (`#4 the OTP ... is the pattern we should match`, `#8 instead of linear we will use sentient-monorepo`), some are scope cuts (`#5 ... no need for dyanamo`). Apply them all; do not collapse them into a vague summary.

## 7. Pin the one thing that matters; defer or derisk the rest
Inside a sweep, identify the single item Mark flags as the thing that actually matters and lead with it, letting the others wait or be handled cheaply. He says so explicitly:
- `the api is not important what is important is that its present on the homepage`
A pick can elevate one item and demote the rest in the same breath. When he does this, do the pinned item to the bar he set and don't over-invest in the demoted ones — a `minimal` or `thats fine` on an item is permission to do the cheap version.

## 8. If a menu was never offered, a bare letter is unparseable — say so or re-offer
A lone `B` or `#2` with no prior labeled list in the thread is ambiguous, not a free choice for you to assign. Don't guess which `B` he means. Either re-surface the menu you should have presented, or ask the one blunt question that recovers the mapping. The fix is almost always upstream: you should have given him a menu to begin with (section 1).

## Red flags
| You did | Mark's correction |
|---|---|
| Presented choices as prose he has to answer in sentences | He still replies `go with B` — and you have to guess what B was |
| Re-asked for confirmation after a bare `option 1` | The pick was already complete; just execute it |
| Dropped the rider on a pick (`...and update envs when your done`) | The appended directive is part of the selection — do both |
| Treated a question inside a sweep (`4.whats the mcp server for?`) as resolved | It is the open item; answer it before moving on |
| Re-pitched an item he cut with a because-clause | `4 wont be needed because this is a small application` is final |
| Filled gaps in his skip-numbered list (`#1 #2 #4`) | Resolve only the items he wrote; don't invent #3 |
| Over-built a demoted item | `the api is not important... it just needs to be present on the homepage` |
| Collapsed his authored decision list into a vague summary | Each `#N` is its own directive — apply every one |

See **steer-and-correct-the-agent** for his single terse directives (`yes`, `no replace X with Y`, method constraints) once a pick is in motion, and **research-gated-build-plan** for sequencing and scope-cutting a larger plan that a sweep resolves.
