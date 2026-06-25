# Phase 07 Bugfix — Speaker label normalisation for WaveSpeed compliance

**Discovered during:** end-to-end run of Phase 07 batch runner with gpt-oss-120b model.

## What was broken

### Bug 1 — ALEX:/JORDAN: not converted
The `mode_2person` prompt instructs the model to use `ALEX:` and `JORDAN:` as speaker labels.
`_to_speaker_format()` had no rules for these names, so the script file kept raw `ALEX:` /
`JORDAN:` labels. WaveSpeed scans for `Speaker N:` patterns and found nothing — no voices
would be assigned.

### Bug 2 — Section headers and metadata reaching TTS
The gpt-oss-120b model (and potentially others) adds lines like:
  `**ESTIMATED WORD COUNT:** 4,030`
  `**COLD OPEN (1 min)**`
These were not speaker lines but passed through to the TTS prompt unchanged.

### Speaker numbering clarification (not a bug — verified)
Confusion arose about whether WaveSpeed uses 0-based or 1-based speaker numbers in the prompt
text. Verified against live API docs and an empirically working audio sample:

- **Prompt text uses 0-based**: `Speaker 0:`, `Speaker 1:`, `Speaker 2:`, `Speaker 3:`
- **API params are 1-based in name**: `speaker_1`, `speaker_2`, `speaker_3`, `speaker_4`
- `tts/cli.py` `api_param_map` bridges the offset correctly: `{"0": "speaker_1", ...}`
- Do NOT change either side — the existing mapping is correct and verified.

## Fixes applied

### `src/run_chapter.py` — `_to_speaker_format()`

1. Added ALEX/JORDAN conversion rules (bold and plain variants):
   ```python
   s = re.sub(r"^\*\*ALEX:\*\*\s*",   "Speaker 0: ", s)
   s = re.sub(r"^ALEX:\s*",            "Speaker 0: ", s)
   s = re.sub(r"^\*\*JORDAN:\*\*\s*",  "Speaker 1: ", s)
   s = re.sub(r"^JORDAN:\s*",          "Speaker 1: ", s)
   ```

2. Added final filter — drops any line that is not `Speaker N:` after all substitutions:
   ```python
   merged = [s for s in merged if re.match(r"^Speaker \d+:", s)]
   ```

3. Expanded docstring to document the full normalisation table and the 0-based/1-based
   offset rule so future maintainers do not re-investigate this.

### `src/docs/session_notes/tts_session.md`

Updated Script Format section with:
- Confirmed format (`Speaker 0:` through `Speaker 3:`)
- Explanation of the 0-based/1-based offset and why it exists
- Full normalisation table covering every LLM label variant → Speaker N: mapping
- Rule: if a future model uses different character names, add to `_to_speaker_format()`,
  never change the numbering scheme

## Verified

- All 12 label variants convert correctly with zero non-Speaker lines in output ✓
- ch02 script re-processed: 53 clean speaker lines, 0 noise lines ✓
- `tts/cli.py` unchanged — api_param_map was already correct ✓

---

# Phase 07 Bugfix — TTS job recovery on long-running generation

**Discovered during:** pre-flight review before first real WaveSpeed run.

## Problem

`send_to_api()` called `client.run()` which is a blocking synchronous wait with no
timeout. Two risks:
1. Terminal shows nothing for 15+ minutes — no way to tell if it's alive or hung
2. `request_id` is internal to `client.run()` and never surfaced — if the process
   is killed (terminal drop, Ctrl-C, network loss), the job continues on WaveSpeed's
   servers but the audio URL is permanently lost and the credit is spent

## Fix applied

### `src/tts/cli.py`

- Replaced `client.run()` with a split submit + manual poll loop:
  1. `client._submit()` → gets `request_id` immediately
  2. Writes `tts_job.json` to the audio output folder before waiting
  3. Polls `client._get_result()` every 5s; prints a status line every 30s
  4. On completion, deletes `tts_job.json`
  5. On failure or interrupt, `tts_job.json` is left on disk for recovery
- `send_to_api()` now accepts `output_folder` param
- `main()` passes `output_folder` through

Sample output during a run:
```
TTS submitted  request_id=abc123
Recovery file  data/output/audio/02_chapter_.../tts_job.json
Polling for completion (status every 30s)...
  [30s] status=processing...
  [60s] status=processing...
  [done] 87s
```

### `src/tts/recover.py` (new)

If the process is killed mid-wait:
```
WAVESPEED_API_KEY=... python src/tts/recover.py data/output/audio/02_.../tts_job.json
```
or with explicit args:
```
WAVESPEED_API_KEY=... python src/tts/recover.py <request_id> <output_folder>
```
Polls the existing job and downloads the audio — no resubmission, no re-charge.
