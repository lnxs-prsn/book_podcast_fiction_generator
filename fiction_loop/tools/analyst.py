#!/usr/bin/env python3
"""fiction_loop analyst — deterministic situation analysis from the pipeline's receipts.

Zero tokens, zero network, zero dependencies (stdlib only). Reads the evidence the
pipeline already produces (pipeline.log JSON events, bridge .out files, STATUS.md,
state files, git) and matches it against the known failure-signature table built
from this project's real incident history. Prints ranked findings; says "unknown
signature" instead of guessing — escalate those with the evidence bundle.

Usage:  python3 fiction_loop/tools/analyst.py
Exit:   0 = no critical findings, 1 = critical findings present.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

R = Path(__file__).resolve().parent.parent  # fiction_loop/
FINDINGS: list[tuple[str, str, str]] = []   # (severity, verdict, fix)
OK: list[str] = []


def find(sev: str, verdict: str, fix: str) -> None:
    FINDINGS.append((sev, verdict, fix))


def ok(msg: str) -> None:
    OK.append(msg)


# --- 1. config -------------------------------------------------------------
def check_config() -> dict:
    try:
        import tomllib
        cfg = tomllib.loads((R / "tools/pipeline_config.toml").read_text())
    except Exception as e:
        find("CRITICAL", f"pipeline_config.toml unreadable: {e}", "fix TOML syntax")
        return {}
    ok(f"config OK (model={cfg.get('model')}, floor={cfg.get('min_chapter_words')})")
    return cfg


# --- 2. api key ------------------------------------------------------------
def check_key(cfg: dict) -> None:
    env_key = os.environ.get("OPENROUTER_API_KEY")
    dotenv = R.parent / ".env"
    file_key = None
    env_model = os.environ.get("OPENROUTER_MODEL")
    if dotenv.exists():
        for line in dotenv.read_text().splitlines():
            if line.startswith("OPENROUTER_API_KEY=") and len(line.split("=", 1)[1].strip()) > 5:
                file_key = True
            if line.startswith("OPENROUTER_MODEL="):
                env_model = env_model or line.split("=", 1)[1].strip()
    if not env_key and not file_key:
        find("CRITICAL", "no API key in shell env or repo .env",
             "add OPENROUTER_API_KEY to .env (bridge scripts read it as fallback)")
    else:
        ok("API key present (shell env)" if env_key else "API key present (.env fallback)")
    if env_model and cfg.get("model") and env_model != cfg["model"]:
        find("WARN", f"model mismatch: env/.env says {env_model!r}, TOML says {cfg['model']!r} — env WINS",
             "align them; TOML prices/context must match the model actually used")


# --- 3. pipeline.log signatures ---------------------------------------------
def check_api_log(cfg: dict) -> None:
    log = R / "logs/pipeline.log"
    if not log.exists():
        ok("pipeline.log: none yet")
        return
    events = []
    for line in log.read_text(errors="ignore").splitlines()[-200:]:
        try:
            events.append(json.loads(line))
        except Exception:
            continue
    succ = [e for e in events if e.get("event") == "api_call_success"]
    if succ:
        last = succ[-1]
        ctoks, chars = last.get("actual_completion_tokens", 0), last.get("content_chars", 0)
        visible = max(chars / 4, 1)
        if ctoks > 2 * visible:
            find("CRITICAL",
                 f"THINKING TAX: last call ({last.get('model')}) billed {ctoks} completion tokens "
                 f"for ~{int(visible)} tokens of visible text ({ctoks/visible:.1f}x)",
                 "reasoning model in the Writer seat — switch to a non-thinking instruct model")
        else:
            ok(f"last API call healthy: {ctoks} completion tokens, ratio {ctoks/visible:.1f}x ({last.get('model')})")
        if last.get("finish_reason") == "length":
            find("CRITICAL", "last generation TRUNCATED (finish_reason=length)",
                 "raise api_default_max_tokens_chapter in pipeline_config.toml")
    for e in events[-30:]:
        if e.get("event") == "chapter_validation_failed":
            wc, mn = e.get("word_count"), e.get("min_required")
            find("WARN", f"recent chapter rejected: {wc} words < {mn} floor",
                 "if finish_reason was 'stop' and ratio healthy: model wrote short voluntarily "
                 "(floor/target calibration); draft salvaged at prompts/chapter_draft.md.rejected.md")
        if e.get("event") == "living_doc_validation_failed":
            find("WARN", f"living doc update failed validation: {e.get('missing_or_reordered')}",
                 "update model dropped sections — check api_default_max_tokens_update / model quality")


# --- 4. bridge .out signatures ----------------------------------------------
SIGS = [
    ("api_key is required", "CRITICAL", "key missing from process env AND .env fallback",
     "restore OPENROUTER_API_KEY in .env"),
    ("Missing Authentication header", "CRITICAL",
     "key was SENT but is INVALID (verified provider quirk — misleading message)", "rotate the API key"),
    ("No cookie auth credentials found", "CRITICAL", "request went out with NO auth header",
     "env plumbing broken — check .env fallback loaded"),
    ("ContextOverflowError", "CRITICAL", "assembled prompt exceeds context budget", "trim assembled_prompt.md"),
    ("CostLimitError", "WARN", "cost cap hit — verify TOML prices match the actual model first",
     "fix price_per_1m_* or raise caps / --ignore-cost-limit deliberately"),
    ("Rate limit", "WARN", "provider rate limiting", "wait / lower frequency"),
]


def check_bridge_outs() -> None:
    outs = sorted(R.glob("logs/chapter_*/0*_writer_bridge.out"), key=lambda p: p.stat().st_mtime)
    if not outs:
        return
    latest = outs[-1]
    text = latest.read_text(errors="ignore")
    exit_lines = re.findall(r"BRIDGE_EXIT:(\d+)", text)
    if not exit_lines:
        find("WARN", f"{latest.name}: no BRIDGE_EXIT line — bridge still running or was killed",
         "if no python process is alive: harness killed detached children — add `setsid` to the launch")
        return
    if exit_lines[-1] == "0":
        ok(f"last bridge run exited 0 ({latest.parent.name})")
        return
    for needle, sev, verdict, fix in SIGS:
        if needle in text:
            find(sev, f"{latest.parent.name}: {verdict}", fix)
            return
    if "Chapter too short" in text:
        return  # already reported via pipeline.log with better data
    find("WARN", f"{latest.parent.name}: bridge exited 1 with UNKNOWN signature",
         f"escalate with evidence bundle: {latest}, logs/pipeline.log tail, STATUS.md")


# --- 4b. per-agent log states (timeout races, dead subagents) -----------------
def check_agent_logs() -> None:
    dirs = sorted([d for d in (R / "logs").glob("chapter_*") if d.is_dir()])
    if not dirs:
        return
    latest = dirs[-1]
    status = (R / "logs/STATUS.md").read_text() if (R / "logs/STATUS.md").exists() else ""
    blocked_step = None
    m = re.search(r"step: ([\d.]+) \| agent: (\w+) \| state: (BLOCKED|RUNNING)", status)
    if m:
        blocked_step = (m.group(1), m.group(2), m.group(3))
    for logf in sorted(latest.glob("[0-9]*.log")):
        txt = logf.read_text(errors="ignore")
        if "START" not in txt:
            continue
        finished = "DONE" in txt
        died = not finished and "BLOCKED" not in txt
        step_id = logf.name.split("_")[0]
        if blocked_step and blocked_step[2] == "BLOCKED" and blocked_step[0].lstrip("0") == step_id.lstrip("0"):
            if finished:
                find("WARN", f"TIMEOUT RACE at step {step_id}: harness declared timeout but "
                     f"{logf.name} shows the agent COMPLETED afterwards (DONE present)",
                     "verify the step's output artifact (e.g. update_brief.json chapter field), "
                     "then RESUME FROM THE NEXT STEP — do not re-run this one")
            elif died:
                idempotent = any(k in logf.name for k in ("fetcher", "checker", "assembler", "extractor"))
                find("WARN", f"step {step_id} agent died mid-work ({logf.name}: START without DONE/BLOCKED)",
                     "safe to retry the step as-is" if idempotent else
                     "NOT idempotent (updater) — read its log to see what it already touched before retrying")


# --- 5. state consistency -----------------------------------------------------
def check_state() -> None:
    try:
        ms = json.loads((R / "state/master_state.json").read_text())
        ps = json.loads((R / "state/process_state.json").read_text())
    except Exception as e:
        find("CRITICAL", f"state files unreadable: {e}", "inspect state/*.json")
        return
    n = ms.get("chapter_count", -1)
    on_disk = len(list((R / "chapters").glob("chapter_*.md")))
    status = (R / "logs/STATUS.md").read_text() if (R / "logs/STATUS.md").exists() else ""
    mid_run = ("state: RUNNING" in status or "state: BLOCKED" in status) and f"chapter: {n + 1:03d}" in status
    if n != on_disk:
        if mid_run and on_disk == n + 1:
            state_word = "RUNNING" if "state: RUNNING" in status else "INTERRUPTED (blocked mid-run)"
            ok(f"chapter {n + 1:03d} {state_word}: prose on disk, state not yet updated")
        else:
            find("WARN", f"chapter_count={n} but {on_disk} chapter files on disk",
                 "a chapter was added/removed without state update (or rollback leftover)")
    ptr = ms.get("next_chapter_pointer", {})
    try:
        if int(ptr.get("chapter", -1)) != n + 1:
            find("WARN", f"pointer chapter {ptr.get('chapter')} != chapter_count+1 ({n + 1})",
                 "pointer/state desync — inspect last Updater run")
    except (TypeError, ValueError):
        find("WARN", f"pointer chapter unparsable: {ptr.get('chapter')!r}", "inspect pointer")
    op = ptr.get("operation_due")
    if op and op not in ps.get("operations", {}):
        find("CRITICAL", f"pointer operation_due {op!r} not in process_state", "operation id typo/desync")
    if ptr.get("type") == "return_to_character" and not ptr.get("char_id"):
        find("CRITICAL", "pointer type return_to_character but char_id is null", "set char_id or type")
    if not FINDINGS or all("pointer" not in f[1] for f in FINDINGS):
        ok(f"state sync OK (chapter_count={n}, next={ptr.get('chapter')} {ptr.get('type')} {op})")


# --- 6. git / redo readiness ---------------------------------------------------
def check_git() -> None:
    try:
        dirty = subprocess.run(["git", "status", "--short", str(R)], capture_output=True,
                               text=True, cwd=R.parent).stdout.strip()
        last = subprocess.run(["git", "log", "--oneline", "-1"], capture_output=True,
                              text=True, cwd=R.parent).stdout.strip()
    except Exception:
        return
    if dirty:
        find("INFO", f"fiction_loop has uncommitted changes ({len(dirty.splitlines())} paths)",
             "fine mid-work; but `redo last chapter` requires a clean tree — orchestrator "
             "step 3.5 baseline-commits automatically at next run")
    else:
        ok("git tree clean")
    if last and not re.match(r"^\w+ (chapter \d|pre-chapter)", last):
        find("INFO", f"last commit is not a chapter transaction: {last!r}",
             "`redo last chapter` will refuse until a chapter commit is on top (expected before first committed chapter)")


# --- 7. STATUS ------------------------------------------------------------------
def show_status() -> None:
    p = R / "logs/STATUS.md"
    if p.exists():
        ok("STATUS: " + p.read_text().splitlines()[0][:100])


def main() -> None:
    cfg = check_config()
    check_key(cfg)
    check_api_log(cfg)
    check_bridge_outs()
    check_agent_logs()
    check_state()
    check_git()
    show_status()

    print("=" * 62)
    print("FICTION_LOOP ANALYST")
    print("=" * 62)
    for m in OK:
        print(f"  ok  {m}")
    if not FINDINGS:
        print("\nNo findings. If something still looks wrong, the signature is new:")
        print("escalate with logs/pipeline.log tail + latest logs/chapter_*/ + STATUS.md")
    else:
        order = {"CRITICAL": 0, "WARN": 1, "INFO": 2}
        for sev, verdict, fix in sorted(FINDINGS, key=lambda f: order[f[0]]):
            print(f"\n[{sev}] {verdict}")
            print(f"       fix: {fix}")
    sys.exit(1 if any(f[0] == "CRITICAL" for f in FINDINGS) else 0)


if __name__ == "__main__":
    main()
