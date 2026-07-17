# File-state machine — starter file set (copy the blocks into a new project)

Minimum viable chassis for AI-session-operated work. Create these files, then
grow only by declaration (new cycle type = new registry row + new cycle doc).

## 1. `RUN.md` (root) — the operating manual

```markdown
# RUN.md — operating manual

This project is a file-state machine operated by disposable sessions. One
session runs one cycle; all durable state lives in files; every cycle ends in
exactly one commit.

## Kickoff (give a fresh session this line)
> Read RUN.md, run the start checklist, then do exactly what it says.

## Start checklist (every session, before any work)
1. `git status` — clean tree, or STOP and investigate the journal.
2. Read `core/cycle_registry.md` + your cycle's doc in `cycles/`.
3. Journal INTENT before acting (write-ahead).

## End ritual
Clean tree (one cycle commit) or a journaled dirty state. Nothing else.
```

## 2. `core/cycle_registry.md` — one row per cycle type

```markdown
| cycle type | unit of work | owned state files | gate |
|---|---|---|---|
| <type> | <one completed X> | <files only this cycle writes> | <check command> |
```

## 3. `cycles/<type>.md` — the step procedure

Numbered steps a session follows verbatim; each step names the files it
reads/writes; the last steps are always: run the gate, commit with the cycle
id as the message prefix.

## 4. `state/journal.md` — append-only, write-ahead

```markdown
<ISO ts> INTENT <cycle-id> — <what I am about to do>
<ISO ts> OUTCOME <cycle-id> — OK|FAIL — <evidence: hashes, test counts>
```

## 5. Structured truth beside prose truth

`build_status.json` (machine-readable phase/pass state; done = commit hash,
never a claim) + `BUILD_LOG.md` (prose rationale). Never duplicate one in the
other.

## Growth rule (the invariant that keeps the chassis honest)

Adding a new cycle type may touch ONLY: a registry row, its own `cycles/`
doc, its own gate function slot, its own state files. If it needs a core
change, you found a design leak — fix the design deliberately, don't patch
the chassis in passing. Prove it occasionally: land a whole new cycle type
and diff — core files must show zero changes.
