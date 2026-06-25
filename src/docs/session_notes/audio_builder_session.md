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
```
Speaker 0: Welcome to the show.
Speaker 1: Thanks for having me.
Speaker 0: Let's get into it.
```
- `Speaker 0` = host
- `Speaker 1` = expert
- Raw text, no JSON, no special encoding

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

## What Is Not In Scope
- Webhook handling
- Polling loop (SDK handles it)
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
