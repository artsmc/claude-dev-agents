#!/usr/bin/env python3
"""Judge-based trigger eval for the headroom-context-compression skill.

Why this exists: skill-creator's run_loop tests triggering by running `claude -p`
in a bare sandbox with no MCP, no files, and no subagents, then watching for a
Skill/Read tool call. For an MCP-/agentic-context-dependent skill that approach
reports recall=0 — not because the description is bad, but because the scenarios
the queries describe don't exist in the sandbox, so Claude has nothing to act on.

This eval sidesteps that. It asks an LLM judge a *routing* question: given a
realistic set of available skills (headroom + tempting decoys) and a user
request, which single skill should be consulted? No MCP, files, or subagents
needed — triggering is a function of description-vs-query, and that's exactly
what we measure. The decoys give the should-NOT-trigger near-misses a correct
alternative home (gzip->archive, png/mp4->media, concise code->refactor,
TOAST->db), so this tests headroom's precision as hard as its recall.

Usage:
    python3 judge_trigger_eval.py [--model claude-opus-4-8] [--runs 3]
                                  [--eval-set trigger-eval.json]
"""
import argparse
import json
import os
import subprocess
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent

def real_headroom_description() -> str:
    """Read headroom's ACTUAL frontmatter description from SKILL.md, so the eval
    tests the real description (not a paraphrase) and reflects any edits."""
    skill_md = HERE.parent / "SKILL.md"
    text = skill_md.read_text()
    fm = text.split("---", 2)[1]
    # join the YAML block scalar lines after 'description:'
    lines, capturing, buf = fm.splitlines(), False, []
    for ln in lines:
        if ln.startswith("description:"):
            capturing = True
            continue
        if capturing:
            if ln and not ln.startswith(" ") and ":" in ln.split(" ")[0]:
                break  # next frontmatter key
            buf.append(ln.strip())
    desc = " ".join(b for b in buf if b)
    return desc or "(description not found)"


# Realistic competing skill set. headroom's entry is its REAL description
# (loaded from SKILL.md); the rest are plausible decoys that should win the
# near-misses so this tests precision as hard as recall.
SKILLS = [
    ("headroom-context-compression", real_headroom_description()),
    ("file-archive",
     "Create gzip/zip/tar archives of files and directories for backup, "
     "release artifacts, or transfer over scp/network."),
    ("media-optimizer",
     "Compress, transcode, and resize images and video (png/jpg/mp4) to reduce "
     "file size for uploads, attachments, and bandwidth limits."),
    ("code-simplifier",
     "Refactor source code to be shorter, clearer, and less repetitive; reduce "
     "duplication and dead code in functions and modules."),
    ("db-performance-tuner",
     "Optimize database schema, indexes, query plans, and storage including "
     "Postgres TOAST / column compression for large tables."),
    ("doc-summarizer",
     "Summarize long documents (PDFs, contracts, articles, diffs) into short "
     "human-readable briefs and TL;DRs for a person to read."),
]


def build_prompt(query: str) -> str:
    listing = "\n".join(f'- {n}: {d}' for n, d in SKILLS)
    return (
        "You are the skill router inside a coding assistant. Below is the list "
        "of available skills with their descriptions. A user has sent a request. "
        "Decide which SINGLE skill (if any) should be consulted to best handle "
        "it. If none of the skills fit, answer NONE.\n\n"
        f"AVAILABLE SKILLS:\n{listing}\n\n"
        f"USER REQUEST:\n\"{query}\"\n\n"
        "Reply with ONLY the exact skill name from the list, or NONE. "
        "No explanation, no punctuation."
    )


def ask_judge(query: str, model: str, timeout: int = 120) -> str:
    cmd = ["claude", "-p", build_prompt(query), "--output-format", "json"]
    if model:
        cmd += ["--model", model]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    try:
        out = subprocess.run(cmd, capture_output=True, text=True,
                             timeout=timeout, env=env)
        data = json.loads(out.stdout)
        text = (data.get("result") or "").strip()
    except Exception as e:  # noqa: BLE001
        return f"__ERROR__:{e}"
    # normalize: take the first skill-name-looking token
    low = text.lower()
    for name, _ in SKILLS:
        if name in low:
            return name
    return "NONE" if "none" in low else (text[:40] or "NONE")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-opus-4-8")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--eval-set", default=str(HERE / "trigger-eval.json"))
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()

    evals = json.loads(Path(args.eval_set).read_text())
    target = "headroom-context-compression"

    # fan out all (query, run) jobs
    jobs = [(i, r) for i in range(len(evals)) for r in range(args.runs)]
    picks: dict[int, list[str]] = defaultdict(list)
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        fut = {ex.submit(ask_judge, evals[i]["query"], args.model): (i, r)
               for (i, r) in jobs}
        for f in as_completed(fut):
            i, _ = fut[f]
            picks[i].append(f.result())

    tp = fp = tn = fn = 0
    rows = []
    for i, item in enumerate(evals):
        ps = picks[i]
        rate = sum(1 for p in ps if p == target) / len(ps)
        triggered = rate >= args.threshold
        should = item["should_trigger"]
        ok = triggered == should
        if should and triggered: tp += 1
        elif should and not triggered: fn += 1
        elif not should and triggered: fp += 1
        else: tn += 1
        rows.append((ok, should, rate, item["query"][:62], ps))

    prec = tp / (tp + fp) if (tp + fp) else 1.0
    rec = tp / (tp + fn) if (tp + fn) else 1.0
    acc = (tp + tn) / len(evals)

    print(f"\n{'='*72}\nJUDGE TRIGGER EVAL  (model={args.model}, runs={args.runs})\n{'='*72}")
    for ok, should, rate, q, ps in rows:
        mark = "PASS" if ok else "FAIL"
        exp = "TRIGGER" if should else "no-trig"
        # show what it picked when it wasn't headroom (diagnoses misroutes)
        other = "" if rate >= args.threshold else "  -> " + ",".join(sorted(set(ps)))
        print(f"  [{mark}] hr_rate={rate:.2f} exp={exp}: {q}{other}")
    print(f"{'-'*72}")
    print(f"  precision={prec:.0%}  recall={rec:.0%}  accuracy={acc:.0%}  "
          f"(tp={tp} fp={fp} tn={tn} fn={fn})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
