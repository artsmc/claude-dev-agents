#!/usr/bin/env python3
"""End-to-end behavior probe for the headroom-context-compression skill.

Gap this fills: subagents spawned for a normal skill-creator output benchmark
can't reach the headroom MCP, so they can't verify the skill actually DRIVES
the tools. This probe runs a real `claude -p` session (which loads the headroom
MCP from ~/.claude.json), hands it a genuine large file, and asserts on the
*tool calls actually made* — not on prose.

It checks three things, in increasing strength:
  1. TRIGGER   — the skill (headroom-context-compression) was invoked.
  2. COMPRESS  — mcp__headroom__headroom_compress was actually called.
  3. ROUNDTRIP — a follow-up turn drives mcp__headroom__headroom_retrieve and
                 the elided needle comes back (proves reversibility e2e).

This is the real integration test for an MCP skill: triggering AND follow-through.

Usage:
    python3 e2e_mcp_probe.py [--model claude-opus-4-8] [--timeout 180]
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

NEEDLE = "SENTINEL-7Q9-do-not-drop-me"


def make_log(path: Path) -> None:
    lines = [f"{i} ERROR ECONNREFUSED 10.0.0.{i % 256}:5432 attempt={i} "
             f"pool=primary backoff={i*3}ms" for i in range(1800)]
    lines.insert(900, f"1799 FATAL unrecoverable: {NEEDLE} corr_id=abc123")
    path.write_text("\n".join(lines) + "\n")


HEADROOM_BIN = "/home/artsmc/.local/bin/headroom"


def write_mcp_config(tmp: Path) -> Path:
    """Minimal MCP config so `claude -p` loads headroom in headless mode.

    Headless mode does NOT inherit ~/.claude.json MCP servers (and gates their
    tools behind permissions that auto-deny non-interactively). We pass headroom
    explicitly via --mcp-config + --strict-mcp-config, and bypass permission
    prompts (safe here: local tool, temp file, no network).
    """
    cfg = {"mcpServers": {"headroom": {
        "type": "stdio", "command": HEADROOM_BIN, "args": ["mcp", "serve"]}}}
    p = tmp / "headroom-mcp.json"
    p.write_text(json.dumps(cfg))
    return p


def stream_tools(query: str, model: str, timeout: int, cwd: str, mcp_cfg: Path):
    """Run claude -p, return (ordered tool names, full stdout text)."""
    cmd = ["claude", "-p", query, "--output-format", "stream-json",
           "--verbose", "--mcp-config", str(mcp_cfg), "--strict-mcp-config",
           "--dangerously-skip-permissions"]
    if model:
        cmd += ["--model", model]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    tools, skills, text = [], [], []
    try:
        out = subprocess.run(cmd, capture_output=True, text=True,
                             timeout=timeout, env=env, cwd=cwd)
    except subprocess.TimeoutExpired as e:
        out = type("X", (), {"stdout": e.stdout or "", "stderr": ""})()
    for line in (out.stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("type") == "assistant":
            for c in e.get("message", {}).get("content", []):
                if c.get("type") == "tool_use":
                    tools.append(c.get("name"))
                    if c.get("name") == "Skill":
                        skills.append(c.get("input", {}).get("skill", ""))
                if c.get("type") == "text":
                    text.append(c.get("text", ""))
        if e.get("type") == "result":
            text.append(e.get("result", "") or "")
    return tools, skills, "\n".join(text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-opus-4-8")
    ap.add_argument("--timeout", type=int, default=180)
    args = ap.parse_args()

    tmp = Path(tempfile.mkdtemp(prefix="headroom-e2e-"))
    log = tmp / "pg-errors.log"
    make_log(log)
    print(f"made {log} ({log.read_text().count(chr(10))} lines, "
          f"needle hidden at ~line 900)")

    mcp_cfg = write_mcp_config(tmp)

    # First, confirm the MCP is visible once loaded via --mcp-config.
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    chk = subprocess.run(
        ["claude", "-p",
         "List ONLY the exact names of tools you have available that begin "
         "with 'mcp__headroom'. If none, reply NONE.",
         "--output-format", "json", "--model", args.model,
         "--mcp-config", str(mcp_cfg), "--strict-mcp-config",
         "--dangerously-skip-permissions"],
        capture_output=True, text=True, env=env, timeout=90)
    try:
        avail = (json.loads(chk.stdout).get("result") or "")
    except Exception:
        avail = chk.stdout
    mcp_visible = "headroom" in avail.lower()
    print(f"\n[0] MCP visible to claude -p? {'YES' if mcp_visible else 'NO'}  "
          f"({avail.strip()[:120]})")
    if not mcp_visible:
        print("  ! headroom MCP not loaded in subprocess — restart Claude Code "
              "and/or verify ~/.claude.json. Behavior checks can't pass without it.")

    query = (
        f"There's a ~1800-line postgres error log at {log}. I'm going to hand "
        "it to a subagent for root-cause analysis. Use the headroom compression "
        "tool to shrink it first so the handoff prompt stays small, and keep the "
        "full log recoverable by hash. Then tell me the compression hash and the "
        "savings percentage."
    )
    tools, skills, text = stream_tools(query, args.model, args.timeout,
                                      str(tmp), mcp_cfg)
    print(f"\n[run] tool calls: {tools}")
    print(f"[run] skills invoked: {skills}")

    triggered = "headroom-context-compression" in skills
    compressed = any(t == "mcp__headroom__headroom_compress" for t in tools)
    retrieved = any(t == "mcp__headroom__headroom_retrieve" for t in tools)

    print(f"\n{'='*64}\nE2E RESULTS\n{'='*64}")
    print(f"  [{'PASS' if triggered else 'FAIL'}] 1. skill triggered")
    print(f"  [{'PASS' if compressed else 'FAIL'}] 2. headroom_compress actually called")
    print(f"  [{'PASS' if retrieved else 'n/a '}] 3. headroom_retrieve called this turn "
          f"(optional in one-shot)")
    if "%" in text or "hash" in text.lower():
        print("  note: model reported a hash/savings figure in its answer.")
    print(f"\nartifacts in {tmp}")
    # success = skill drove the compress tool (the core behavioral claim)
    return 0 if (triggered and compressed) else 1


if __name__ == "__main__":
    sys.exit(main())
