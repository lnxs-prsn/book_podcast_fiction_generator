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

## 3b. ADDENDUM (2026-07-18, later): §3 CONFIRMED — override found

The echo check ran inside the Qwen companion session: shell had
`OPENROUTER_URL=https://api.deepseek.com` (BASE url, no path) exported by the
companion harness, overriding `.env`'s full `/v1/chat/completions` endpoint.
Exactly the §3 prime suspect. Session fix approved by the senior:
`unset OPENROUTER_URL` in that session, then retry step 8 (assembled prompt
intact; do NOT edit `.env` or `pipeline_config.toml` — both proven good).

Durable fix ticketed: `tickets/T-002-normalize-api-url-404-signature.md` —
client-side URL normalization + analyst `returned 404` signature with
freshness aging + the writer.md BLOCKED wording (§2's residual bug).
**IMPLEMENTED (Codex) and ACCEPTED (senior) 2026-07-18** — all 5 checks
green; see the ticket's §6 for the pytest-availability note (`uv run
--frozen --with pytest`, never add pytest to pyproject).

Root-cause fix ticketed (owner chose the bulletproof option):
`tickets/T-003-bookgen-env-namespace.md` — rename the shared llm-channel env
vars to a project-owned `BOOKGEN_LLM_*` namespace so no external harness can
ever export a colliding name. Clean break, no aliases. Sequencing is binding:
T-002 → chapter 006 → T-003 (it depends on a T-002 line and breaks the env
contract; includes an owner step to rename `.env` keys). Scope boundary: the
`src/engines`/`src/slicer` podcast transport keeps its old names (dormant,
never under a companion shell).

## 3c. ADDENDUM (2026-07-18, later still): what is PROVEN vs OPEN

Owner challenged the diagnosis; this section is the honest ledger.

PROVEN (receipts exist):
- Chapters 1–5 generated fine with qwen writer models. The failure began at
  the DeepSeek-direct switch — the first time OPENROUTER_URL became
  load-bearing (with OpenRouter, the client's hardcoded default URL serves
  and a stale/absent var is harmless).
- Step-8 404 had an EMPTY body (bad path signature, not model-not-found).
- The identical request succeeded from a plain repo-root shell (smoke test).
- The Qwen companion session reported `echo $OPENROUTER_URL` →
  `https://api.deepseek.com` (base url) — reported by that agent in-session,
  relayed by the owner. This shell also verified its OWN env is clean.
- T-002 is implemented (Codex), accepted (senior), committed (aebc2ca): URL
  normalization + analyst 404 signature (both branches behavior-verified) —
  the 404 CLASS is closed regardless of where the override comes from.

OPEN — NOT located (do not present hypotheses as findings):
- WHERE the Qwen process got that env var. Checked and ruled out: shell
  profiles, home/.env, project .qwen/ (none exists), VSCode process env (this
  session's shells are clean). `~/.qwen/settings.json` has
  `providerMetadata.deepseek.baseUrl = https://api.deepseek.com` — the same
  value, but that it gets EXPORTED into subprocess env is UNVERIFIED
  speculation. Candidate mechanisms: (a) Qwen Code auto-loaded a stale repo
  .env at session start; (b) the extension exports provider config. Neither
  confirmed.

DISCRIMINATING TEST (owner, in progress): run the chapter-006 step-8 resume
in a CODEX session — same repo, same .env, different companion. Codex env
probe (`echo $OPENROUTER_URL`) clean + run completes → override is
Qwen-layer; T-003 stays queued behind ch6. Codex ALSO shows the base url or
404s → the Qwen-layer localization is WRONG; re-diagnose from the new
receipts, and treat §3c hypotheses as dead.

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
