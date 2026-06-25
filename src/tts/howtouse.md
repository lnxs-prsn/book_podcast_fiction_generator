# WaveSpeed VibeVoice CLI — How to Use

## Basic run

```bash
python cli.py \
  --script ./podcast.txt \
  --output ./audio/ \
  --api-key ws_live_xxxxxxxx \
  --speaker-1 en-Alice_woman \
  --speaker-2 en-Carter_man
```

## Script format

The script must contain only `Speaker N:` lines (0-based, up to 4 speakers):

```text
Speaker 0: Welcome to the show.
Speaker 1: Thanks for having me.
Speaker 0: Let's get into it.
```

`Speaker 0:` → `speaker_1` voice param, `Speaker 1:` → `speaker_2`, and so on.
See `tts_session.md` for the full normalisation table.

## If the process is killed mid-run

Generation takes 10–20 minutes. If the terminal drops or the process is killed,
the job keeps running on WaveSpeed's servers. Recover the audio without resubmitting:

```bash
WAVESPEED_API_KEY=... python src/tts/recover.py data/output/audio/<chapter>/tts_job.json
```

`tts_job.json` is written to the output folder immediately after submission.
See `recover.py --help` or `tts_session.md` → "Long-running jobs and recovery".
