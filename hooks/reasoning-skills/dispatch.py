#!/usr/bin/env python3
"""
UserPromptSubmit hook: surface Mark's metacognitive reasoning skills.

These skills (research-gated-build-plan, diagnose-from-raw-symptom,
prove-it-live-before-done, fleet-dispatch-and-watch, steer-and-correct-the-agent,
plus any mined later) encode HOW Mark works. Skills undertrigger — the model
often forgets to consult them. This hook reads each prompt, matches it against
the skills' trigger signatures, and injects a short cue reminding the model to
consider the matching skill(s).

Contract: non-blocking, fails OPEN (any error -> exit 0, no output). It can only
ever ADD a hint; it can never block or alter Mark's prompt.

Reads hook payload as JSON on stdin (field: "prompt"). On a match, emits:
  {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                          "additionalContext": "<cue>"}}
"""
import sys, os, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
SIG_PATH = os.path.join(HERE, "signatures.json")

# Tunables
MAX_SKILLS = 3          # don't nag with more than this many cues at once
MIN_PHRASE_LEN = 3      # ignore ultra-short phrase matches as noise


def load_signatures():
    with open(SIG_PATH) as fh:
        return json.load(fh).get("skills", [])


def match_skill(prompt_lc, skill):
    """Return the first concrete trigger that fired, or None."""
    for phrase in skill.get("phrases", []):
        p = phrase.lower().strip()
        if len(p) >= MIN_PHRASE_LEN and p in prompt_lc:
            return phrase
    for rx in skill.get("regexes", []):
        try:
            if re.search(rx, prompt_lc, re.IGNORECASE):
                return f"/{rx}/"
        except re.error:
            continue
    return None


def main():
    try:
        raw = sys.stdin.read()
    except Exception:
        return 0
    if not raw.strip():
        return 0
    try:
        payload = json.loads(raw)
    except Exception:
        return 0

    prompt = payload.get("prompt", "")
    if not isinstance(prompt, str) or not prompt.strip():
        return 0
    prompt_lc = prompt.lower()

    try:
        skills = load_signatures()
    except Exception:
        return 0

    hits = []
    for sk in skills:
        trig = match_skill(prompt_lc, sk)
        if trig:
            hits.append((sk, trig))
        if len(hits) >= MAX_SKILLS:
            break

    if not hits:
        return 0

    lines = ["[reasoning-skill cue] Your message pattern-matches Mark's reasoning skills. "
             "Before responding, consider invoking:"]
    for sk, trig in hits:
        lines.append(f"  • `{sk['slug']}` — {sk.get('nudge','').strip()} (matched: \"{trig}\")")
    lines.append("Invoke the skill via the Skill tool if it applies; ignore this cue if it clearly does not.")
    context = "\n".join(lines)

    out = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }
    sys.stdout.write(json.dumps(out))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # fail open no matter what
        sys.exit(0)
