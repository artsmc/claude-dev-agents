# Verbatim Pick Examples & Red-Flag Corrections

Full verbatim examples of Mark's pick grammar plus the red-flag correction table, moved here from SKILL.md. Read this when a terse reply maps ambiguously onto your menu, or to see the full flavor of a pattern before responding.

## Rider picks (SKILL.md section 3)

His picks often carry a second clause bolted onto the chosen item — a follow-on action or an inline answer:

- `option 1 and update envs when your done`
- `1. yes, and execute it`
- `c one big commit`

## Multi-item sweep (SKILL.md section 4)

- `1. yes multi tenant, 2.thats fine, 3 just aws manage everything, 4.whats the mcp server for? 5. minimal`

Here `1` is an accept, `2` is an accept, `3` is a constraint, `4` is a question back at YOU (answer it, don't treat it as resolved), `5` is a parameter.

## Ranged pick with because-clause scope-cut (SKILL.md section 5)

- `lets do 1-3, 4 wont be needed because this is a small application`

## Mark-authored numbered decision list (SKILL.md section 6)

- `#1 in your spec sheet draw a mermaid uml of the schema. #2 same add a visual uml mermaid of the api. #4 the OTP from sentient-monorepo is the pattern we should match. #5 chat session persistance will be handled by postgres no need for dyanamo. #7 case should use sentient-monorepo as its api source of truth. #8 instead of linear we will use sentient-monrepo`

Each `#N` is independent: some are tasks (`draw a mermaid uml`), some are source-of-truth declarations (`#4 the OTP ... is the pattern we should match`, `#8 instead of linear we will use sentient-monorepo`), some are scope cuts (`#5 ... no need for dyanamo`).

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
