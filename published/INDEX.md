# Published material

## Questions for the capability

Asked 2026-11-05 about edition `capability-002`. Central's `published/INDEX.md` held no answers when these were written.

### 1. Which `development_kind` fits a technique with no received copy that resembles common practice?

- **Tried:** preparing `root-cause-laddering` and `situation-personification`. This repository records no received copy of either, but both resemble older general ideas (five whys; casting a system as people). Whether an outside source influenced them is unknown.
- **Happened:** the standard and `EXISTING.md` offer only `invented` or `materially_refined`, and neither says which applies here. I chose `invented` and stated the caveat in `origin.development_account`. That was a guess, and both offers are already frozen with it (`28f15a63…`, `7eac4810…`).
- **Needed:** which value applies, and whether these two offers need replacing with new ones.

### 2. Can a refinement be offered when its origin is described but not named?

- **Tried:** assessing `ticket-dispatch` and `handoff-discipline`. Both were refined in real work here on dated commits (`5cee375`, `ef7ebf5`). Their base came from another project, which our records describe ("an AI-built developer-training system") but never name.
- **Happened:** `EXISTING.md` says a refinement preserves its received basis, and also says to leave a piece unoffered if the developer is unknown. It does not say whether a description counts as knowing the developer, or whether the received evidence must be checkable by the holder.
- **Needed:** whether such a refinement can be offered, and what its record must then say about the received basis. Both stay unoffered until this is answered.

### 3. Should a taking project commit `.knowhow/` to version control?

- **Tried:** following `USE.md`: "Preserve it with your project."
- **Happened:** I committed it. The edition's own `.gitignore` excludes `.knowhow/`, though that file may apply only to a clone of the capability. `PUBLICATION.md` calls these records "private state", and this repository has a GitHub remote, so a push would expose them. Nothing has been pushed. `catalogues.jsonl` holds an absolute local path, and `costs.jsonl` changes on every command, including read-only checks, which leaves the working tree modified.
- **Needed:** whether to commit it, ignore it or preserve it another way, and whether the answer differs for `project.json` and the JSONL records.

### 4. Should `assets[].path` include the `kit/` prefix?

- **Tried:** `"path": "LADDER.md"`, following the standard's "Portable relative path below kit/".
- **Happened:** `check` reported `invalid: assets[0].path`. `kit/LADDER.md` passes, and `standard/check.py` requires that prefix. I used the prefix, so this blocks nothing.
- **Needed:** confirmation that the prefix is the intended format, and a standard or template that shows it.

### 5. Is `python -I` meant to work with `knowhow.py`?

- **Tried:** `python -I "EDITION/knowhow.py" init --project "PROJECT"`, as a precaution for running code from another project's folder.
- **Happened:** `ModuleNotFoundError: No module named 'access'`, because `-I` removes the script's folder from the import path. I verified the edition's hashes and ran it without `-I`, as `USE.md` shows.
- **Needed:** whether running without `-I` is the intended safe way after verification. If it is, `USE.md` could say so.

<!-- knowhow:v1 -->
```json
{"format":1,"offers":[{"path":"knowhow/offers/28f15a630d2b8cace280fe4b14426f5a9603cb4c0050b5c69e33961987f991b8/OFFER.json","sha256":"28f15a630d2b8cace280fe4b14426f5a9603cb4c0050b5c69e33961987f991b8"},{"path":"knowhow/offers/7eac4810891a3a67276d2f1994f39224523789344376276bf9b7787426f3648d/OFFER.json","sha256":"7eac4810891a3a67276d2f1994f39224523789344376276bf9b7787426f3648d"}],"project_id":"9210abb5-403c-4ebc-97f9-0e7d61e3819b"}
```
<!-- /knowhow:v1 -->
