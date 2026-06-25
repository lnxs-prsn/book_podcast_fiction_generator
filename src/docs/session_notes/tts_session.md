# SESSION.md — WaveSpeed VibeVoice CLI

## Goal
Build a Python CLI that reads a two-speaker dialogue script, sends it to the WaveSpeed VibeVoice TTS API, and saves the returned audio file locally.

---

## Stack
- Python 3.10+
- `wavespeed` SDK (`pip install wavespeed`)
- `argparse` — CLI parsing
- `requests` — audio download
- No framework, no web server

---

## Entry Point
`python main.py --script ./podcast.txt --output ./audio/ --api-key sk-xxx`

---

## CLI Flags

| Flag | Required | Default | Notes |
|------|----------|---------|-------|
| `--script` | Yes | — | Path to `.txt` dialogue file |
| `--output` | Yes | — | Folder to save `.mp3` |
| `--api-key` | Yes | — | WaveSpeed API key |
| `--speaker-1` | No | `en-Alice_woman` | Voice for `Speaker 0:` lines |
| `--speaker-2` | No | `en-Carter_man` | Voice for `Speaker 1:` lines |
| `--speaker-3` | No | — | Voice for `Speaker 2:` lines |
| `--speaker-4` | No | — | Voice for `Speaker 3:` lines |

---

## Script Format (input file)

**Verified working format** (confirmed against WaveSpeed VibeVoice API and empirically verified
with produced audio):

```
Speaker 0: Welcome to the show.
Speaker 1: Thanks for having me.
Speaker 0: Let's get into it.
```

- Labels are **0-based** in the script text: `Speaker 0:` through `Speaker 3:`
- API params are **1-based** in name: `speaker_1` through `speaker_4`
- The offset (0-based text ↔ 1-based param name) is handled in `build_api_payload()`'s
  `api_param_map`: `{"0": "speaker_1", "1": "speaker_2", "2": "speaker_3", "3": "speaker_4"}`
- `Speaker 0:` = host (voice: `speaker_1` param)
- `Speaker 1:` = expert (voice: `speaker_2` param)
- Raw text, no JSON, no special encoding

### Why the offset exists

WaveSpeed's own docs show `Speaker 1:` in examples but describe `speaker_1` as "Voice for
Speaker 0". The prompt text uses 0-based numbering; the API parameter names are 1-based. Do
not change either side — this is intentional and verified.

### LLM output → Speaker N: normalisation

The LLM may emit speaker labels in several formats. `_to_speaker_format()` in `run_chapter.py`
normalises all of them before writing the script file:

| LLM label (raw)                 | Normalised to | Notes                          |
|---------------------------------|---------------|--------------------------------|
| `ALEX:` / `**ALEX:**`           | `Speaker 0:`  | mode_2person host name         |
| `JORDAN:` / `**JORDAN:**`       | `Speaker 1:`  | mode_2person expert name       |
| `HOST:` / `**H:**`              | `Speaker 0:`  | all other modes                |
| `EXPERT:` / `GUEST:`            | `Speaker 1:`  | all other modes                |
| `**EXPERT Jordan:**`            | `Speaker 1:`  | named expert with bold         |
| `EXPERT Jordan:`                | `Speaker 1:`  | named expert plain             |
| `**E:**`                        | `Speaker 1:`  | abbreviated bold               |
| `CRITIC:`                       | `Speaker 2:`  | mode_4person only              |
| `NEWCOMER:`                     | `Speaker 3:`  | mode_4person only              |
| `Speaker N:` / `**Speaker N:**` | `Speaker N:`  | already clean, kept as-is      |

If a future model uses different character names, add a rule to `_to_speaker_format()` —
never change the Speaker N: numbering scheme or the api_param_map offset.

---

## Functions

### `cli_entrypoint()`
- Parses args with `argparse`
- Validates `--script`, `--output`, `--api-key` are present
- Builds `speakers` dict: `{"speaker_1": "en-Alice_woman", "speaker_2": "en-Carter_man", ...}` — only includes speakers that have a value
- Calls `main()`

---

### `main(script_path, output_folder, api_key, speakers) → str`
- Calls workers in order
- Returns final saved file path
- Prints path to stdout
- Errors bubble up loudly (no try/except for now)

---

### `read_script(file_path: str) → str`
- Opens file, returns full text as string
- Raises `FileNotFoundError` if missing

---

### `build_api_payload(script: str, speakers: dict) → dict`
- Returns dict with:
  - `prompt` = script text
  - `scale` = `1.3`
  - all speaker keys from `speakers` dict
- Example output:
```python
{
    "prompt": "Speaker 0: Hello.\nSpeaker 1: Hi.",
    "scale": 1.3,
    "speaker_1": "en-Alice_woman",
    "speaker_2": "en-Carter_man"
}
```

---

### `send_to_api(payload: dict, api_key: str) → dict`
- Uses `wavespeed` SDK: `Client(api_key=api_key).run("microsoft/vibevoice", payload)`
- Returns raw response dict
- Expected shape: `{"id": "...", "status": "completed", "outputs": ["https://..."]}`
- Raises `RuntimeError` if `status == "failed"`

---

### `get_audio_url(response: dict) → str`
- Returns `response["outputs"][0]`
- Raises `ValueError` if `outputs` is missing or empty

---

### `download_and_save(url: str, output_folder: str) → str`
- Downloads audio with `requests.get(url)`
- Saves as `output.mp3` inside `output_folder`
- Returns full saved path e.g. `./audio/output.mp3`
- Raises `OSError` if folder doesn't exist or no permission

---

## Call Chain
```
cli_entrypoint()
  └── main()
        ├── read_script()       → str
        ├── build_api_payload() → dict
        ├── send_to_api()       → dict
        ├── get_audio_url()     → str
        └── download_and_save() → str (printed to stdout)
```

---

## Type Chain
```
file path → [read_script]       → str
      str → [build_api_payload] → dict
     dict → [send_to_api]       → dict
     dict → [get_audio_url]     → str (URL)
      str → [download_and_save] → str (saved path)
```

---

## Available Voices
```
en-Alice_woman
en-Carter_man
en-Frank_man
en-Mary_woman_bgm
en-Maya_woman
in-Samuel_man
zh-Anchen_man_bgm
zh-Bowen_man
zh-Xinran_woman
```

---

## Long-running jobs and recovery

TTS generation for a full 30-minute podcast script can take 10–20 minutes. The process
blocks while polling. If it is killed (terminal drop, Ctrl-C, network loss), the job
**continues running on WaveSpeed's servers** — the credit is already spent. To retrieve
the audio without resubmitting:

### What happens automatically

`send_to_api()` writes a `tts_job.json` file to the audio output folder **immediately**
after submission, before the wait begins. Example path:

```
data/output/audio/02_chapter_Chapter_2_.../tts_job.json
```

Contents:

```json
{
  "request_id": "abc123",
  "model": "microsoft/vibevoice",
  "submitted_at": "2026-06-05T14:32:00",
  "output_folder": "/absolute/path/to/audio/folder"
}
```

The file is deleted automatically when the download completes successfully.

### If the process is killed

Find the `tts_job.json` file in the audio output folder and run:

```bash
WAVESPEED_API_KEY=... python src/tts/recover.py data/output/audio/<chapter>/tts_job.json
```

Or if you know the request_id and output folder directly:

```bash
WAVESPEED_API_KEY=... python src/tts/recover.py <request_id> <output_folder>
```

`recover.py` polls the existing job and downloads the audio. No resubmission. No
re-charge. The `tts_job.json` is deleted after a successful recovery.

### Progress during a normal run

```
TTS submitted  request_id=abc123
Recovery file  data/output/audio/02_chapter_.../tts_job.json
Polling for completion (status every 30s)...
  [30s] status=processing...
  [60s] status=processing...
  [done] 742s
```

---

## What Is Not In Scope

- Webhook handling
- Error pretty-printing (loud crash is fine for now)
- Multiple output files per run
- Format other than `.mp3`

---

## Open Questions / Test First
- Does WaveSpeed require `prompt` in the payload or work without it? Test both.
- If `prompt` is omitted and the API still works, no change needed. If it fails, `build_api_payload` already includes it so no fix needed.

---

## File Structure
```
project/
├── main.py        # all functions live here
├── session.md     # this file
└── audio/         # output folder (created by user, not the script)
```
