# HANDOFF — 2026-07-18 DeepSeek switch + step-8 404 — for the next AI

Written by the senior instance mid-diagnosis at owner's request; the owner is
starting a fresh instance. Roles per `handoff-2026-07-17-clone-audit.md` §0
unchanged. Read `handoff-2026-07-17-ch6-postmortem-fixes.md` for the conduct
hardening this run just validated.

## 1. State: run-ready on DeepSeek, blocked at step 8 by a 404

- Owner switched the Writer to **deepseek-v4-pro via DeepSeek's direct API**
  (qwen quota exhausted; book already multi-model — spend log: qwen3.7-plus
  ch1–3, qwen3-max ch4–5; quality is chassis-enforced, LAW 14).
- `.env` at repo root: key + `OPENROUTER_URL=https://api.deepseek.com/v1/chat/completions`
  + `OPENROUTER_MODEL=deepseek-v4-pro`. NEVER cat/grep `.env` (conduct §2).
- `pipeline_config.toml`: model/prices/caps updated (commits cea216a, d1c381b).
  deepseek-v4-pro is a REASONING model (hidden thinking tokens billed as
  completion): chapter/update caps raised to 12000/16000; analyst THINKING TAX
  downgraded CRITICAL→WARN deliberately.
- Smoke-verified 2026-07-18 (~$0.0001, logged in spend file): key, endpoint,
  model id all work through the project's own client.
- Analyst stale-receipt fix (b1ae048): a missing-key bridge failure ages to
  INFO once a key exists, so the STEP 0 gate isn't tripped by old receipts.

## 2. The 2026-07-18 ~00:39 run — hardening WORKED, then 404

A fresh Qwen-companion run executed the post-mortem fixes correctly: STEP 0
analyst gate ran, baseline commit 16fc94b, REAL timestamps in all logs, Writer
`rm -f`'d the stale draft, and on error it stopped and ran the analyst — no
silent self-healing. Steps 4–7.5 completed; `assembled_prompt.md` is intact
and committed. Then step 8:

    API error: OpenRouter returned 404:      ← EMPTY body
    BRIDGE_EXIT:1

Residual conduct bug (second offense, cosmetic): the Writer's terminal log
line was again `DONE — Error:` instead of `BLOCKED`; the analyst is immune to
this now, but the writer spawn prompt/spec could state it explicitly.

## 3. 404 diagnosis — nearly closed, one check remains

**Evidence (verified by the senior, 2026-07-18):** the EXACT failing request
shape — same client class, model `deepseek-v4-pro`, `max_tokens=12000`, URL
from `.env` — **succeeds from a plain repo-root shell** (reply "ok", 40
completion tokens). Key, URL value, model id, and token cap are all
individually proven good. The bridge's preflight log confirms it sent a
standard payload.

**Therefore the bridge process saw a DIFFERENT api_url.** Prime suspect: the
Qwen companion harness exports its own `OPENROUTER_URL` (or the owner's
companion config does) into its shell — and in `invoke_writer.py` the shell
env WINS over `.env` by design. If that exported value is a BASE url (e.g.
`https://api.deepseek.com` without `/v1/chat/completions`, the OpenAI-SDK
`base_url` convention), a raw POST to it returns exactly this: 404 with an
empty body.

**To confirm (inside the Qwen companion session, before anything else):**
run `echo $OPENROUTER_URL` and `echo $OPENROUTER_MODEL` — these two exact
commands only; never `env | grep OPENROUTER` (that would print the key).

**Fix options once confirmed:**
- Session fix: `unset OPENROUTER_URL` (or export the full /v1/chat/completions
  URL) in the Qwen session before kickoff.
- Durable fix (LAW 6, recommended as a small ticket): in `invoke_writer.py` /
  `refresh_living_doc.py` (or the client), normalize `api_url` — if its path
  does not end in `/chat/completions`, append `/v1/chat/completions`. Add a
  `returned 404` signature to analyst.py SIGS pointing at the env-override
  cause.

## 4. To resume

1. Confirm/clear the env override (§3), then re-run the RUN.md kickoff in a
   fresh Qwen session. Artifacts from steps 4–7.5 are fresh; the orchestrator
   may resume at step 8 per its spec (assembled_prompt.md intact) — its own
   pointer logic handles this.
2. Chapter 006 review when it lands (senior or owner): F14 life progression
   nameable+visible; correct_approach continuity for char_001; anchor
   manifestation differs from ch5's "seen". First-ever return-chapter review.
3. After ch6: watch the analyst's THINKING TAX WARN ratio on the first real
   chapter — if reasoning dwarfs prose, revisit model choice or budgets.
4. Open queue: unchanged from `handoff-2026-07-17-clone-audit.md` §5.
