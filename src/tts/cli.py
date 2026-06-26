#!/usr/bin/env python3
"""
WaveSpeed VibeVoice CLI
Turns a multi-speaker script into a single MP3 via the WaveSpeed API.
"""

import json
import logging
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


import requests
import wavespeed

# If this import fails, do NOT add sys.path.insert here.
# The fix is: export PYTHONPATH=src (or prefix: PYTHONPATH=src python ...).
from config import load_config
from podcast_script_generator.llm.exceptions import (PodcastError, TTSSubmissionError, TTSTimeoutError)


# ─── Workers ────────────────────────────────────────────────────────────────

def read_script(file_path: str) -> str:
    """
    Opens the script file and returns all the words inside as a single
    block of text. This text is the `prompt` sent to WaveSpeed.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Script not found: {file_path}")
    return path.read_text(encoding="utf-8")


def build_api_payload(script: str, speakers: dict) -> dict:
    """
    Packages the script and voice choices into the exact JSON shape
    WaveSpeed expects. The script text becomes the `prompt` field.
    """
    # Detect which speakers are actually referenced in the script.
    # Expected prefixes: "Speaker 0:", "Speaker 1:", etc.
    found = set(re.findall(r"Speaker\s+(\d+):", script))

    # Map 0-based script speaker index → 1-based API parameter name
    api_param_map = {
        "0": "speaker_1",
        "1": "speaker_2",
        "2": "speaker_3",
        "3": "speaker_4",
    }

    cfg = load_config()
    scale = float(os.environ.get("WAVESPEED_SCALE") or cfg.get("tts_scale", 1.3))
    payload = {
        "prompt": script,
        "scale": scale,
    }

    for idx in sorted(found, key=int):
        param = api_param_map.get(idx)
        if not param or not speakers.get(param):
            raise ValueError(
                f"Script references 'Speaker {idx}' but no voice is configured "
                f"for --{param.replace('_', '-')}"
            )
        payload[param] = speakers[param]

    return payload


def send_to_api(
    payload: dict,
    api_key: str,
    output_folder: str | None = None,
    max_wait_seconds: float | None = None,
) -> dict:
    """Submit to WaveSpeed, save request_id for recovery, poll with live progress.

    Saves a tts_job.json file to output_folder immediately after submission.
    If this process is killed before the download completes, run:
        python src/tts/recover.py <output_folder>/tts_job.json
    to retrieve the audio without resubmitting (and re-charging the account).

    Polling stops and raises TTSTimeoutError if the job does not complete
    within ``max_wait_seconds`` (default: WAVESPEED_MAX_WAIT_SECONDS env var
    or 3600 seconds).
    """
    job_file = Path(output_folder) / "tts_job.json" if output_folder else None

    try:
        cfg = load_config()
        wavespeed_model = (
            os.environ.get("WAVESPEED_MODEL") or cfg.get("wavespeed_model", "microsoft/vibevoice")
        )
        client = wavespeed.Client(api_key=api_key)

        # Submit only — do NOT call client.run() which blocks without saving the ID.
        request_id, _ = client._submit(wavespeed_model, payload)

        # Persist immediately so we can recover if the process is interrupted.
        if job_file:
            job_file.write_text(
                json.dumps({
                    "request_id": request_id,
                    "model": wavespeed_model,
                    "submitted_at": datetime.now().isoformat(),
                    "output_folder": str(output_folder),
                }, indent=2),
                encoding="utf-8",
            )

        logger.info(f"TTS submitted  request_id={request_id}")
        if job_file:
            logger.info(f"Recovery file  {job_file}")
        if max_wait_seconds is None:
            max_wait_seconds = float(os.environ.get("WAVESPEED_MAX_WAIT_SECONDS", 3600.0))
        deadline = time.monotonic() + max_wait_seconds

        logger.info("Polling for completion (status every 30s)...")

        start = time.monotonic()
        last_report = start

        while True:
            if time.monotonic() >= deadline:
                raise TTSTimeoutError(
                    f"TTS polling exceeded max_wait_seconds={max_wait_seconds:.0f}"
                )

            result = client._get_result(request_id)
            data = result.get("data", {})
            status = data.get("status")
            elapsed = time.monotonic() - start

            if status == "completed":
                logger.info(f"  [done] {elapsed:.0f}s")
                if job_file and job_file.exists():
                    job_file.unlink()
                return {"outputs": data.get("outputs", [])}

            if status == "failed":
                error = data.get("error") or "Unknown error"
                raise TTSSubmissionError(f"WaveSpeed job failed (id={request_id}): {error}")

            if time.monotonic() - last_report >= 30:
                logger.debug(f"  [{elapsed:.0f}s] status={status or 'processing'}...")
                last_report = time.monotonic()

            time.sleep(5)

    except (PodcastError, RuntimeError, TimeoutError):
        raise
    except Exception as exc:
        error_msg = str(exc).lower()
        if any(k in error_msg for k in ("auth", "unauthorized", "api key", "forbidden")):
            raise TTSSubmissionError(f"Authentication failed: {exc}") from exc
        if any(k in error_msg for k in ("connection", "network", "timeout", "unreachable")):
            raise TTSTimeoutError(f"WaveSpeed API is unreachable: {exc}") from exc
        raise TTSSubmissionError(f"WaveSpeed request failed: {exc}") from exc


def get_audio_url(response: dict) -> str:
    """
    Digs into the response and pulls out the first audio URL.
    WaveSpeed returns an array, but for TTS we use the first element.
    """
    outputs = response.get("outputs")
    if not outputs or not isinstance(outputs, list):
        raise ValueError("API response missing 'outputs' array.")
    return outputs[0]


def download_and_save(url: str, output_folder: str) -> str:
    """
    Downloads the audio from the link and saves it into the folder
    the user chose.
    """
    out_dir = Path(output_folder)
    if not out_dir.exists():
        raise OSError(f"Output folder does not exist: {output_folder}")
    if not os.access(out_dir, os.W_OK):
        raise OSError(f"No write permission for output folder: {output_folder}")

    # Stream download to keep memory low for large files
    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()

    # Derive filename from URL or fall back to output.mp3
    filename = Path(url.split("?")[0]).name or "output.mp3"
    if not filename.endswith(".mp3"):
        filename += ".mp3"

    dest = out_dir / filename
    with dest.open("wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return str(dest)


# ─── Manager ────────────────────────────────────────────────────────────────

def main(script_path: str, output_folder: str, api_key: str, speakers: dict) -> str:
    """
    Calls each worker in order, passes results along, and returns the
    final file path so the user sees where their audio landed.
    """
    script = read_script(script_path)
    payload = build_api_payload(script, speakers)
    response = send_to_api(payload, api_key, output_folder=output_folder)
    audio_url = get_audio_url(response)
    saved_path = download_and_save(audio_url, output_folder)
    return saved_path


# ─── Front Door ───────────────────────────────────────────────────────────────

def cli_entrypoint():
    """
    Reads what the user typed, checks the required args exist, fills in
    default voices for any speaker flags left empty, then hands clean
    values to main().
    """
    import argparse
    parser = argparse.ArgumentParser(
        description="Generate multi-speaker audio via WaveSpeed VibeVoice."
    )
    parser.add_argument("--script", required=True, help="Path to .txt dialogue file")
    parser.add_argument("--output", required=True, help="Folder to save the .mp3")
    parser.add_argument(
        "--api-key",
        default=None,
        help="WaveSpeed API key (falls back to WAVESPEED_API_KEY env var)",
    )
    _s = load_config().get("speakers", {})
    parser.add_argument(
        "--speaker-1", default=_s.get("speaker_1", "en-Alice_woman"), help="Voice for Speaker 0"
    )
    parser.add_argument(
        "--speaker-2", default=_s.get("speaker_2", "en-Carter_man"), help="Voice for Speaker 1"
    )
    parser.add_argument("--speaker-3", default=_s.get("speaker_3"), help="Voice for Speaker 2")
    parser.add_argument("--speaker-4", default=_s.get("speaker_4"), help="Voice for Speaker 3")

    args = parser.parse_args()

    # Resolve API key: CLI flag beats environment variable
    api_key = args.api_key or os.environ.get("WAVESPEED_API_KEY")
    if not api_key:
        parser.error(
            "No API key provided. Pass --api-key or set the WAVESPEED_API_KEY "
            "environment variable."
        )

    speakers = {
        "speaker_1": args.speaker_1,
        "speaker_2": args.speaker_2,
        "speaker_3": args.speaker_3,
        "speaker_4": args.speaker_4,
    }

    try:
        final_path = main(args.script, args.output, api_key, speakers)
        sys.stdout.write(str(final_path) + "\n")
    except FileNotFoundError as exc:
        sys.stderr.write(f"Error: {exc}\n")
        sys.exit(2)
    except (PodcastError, ValueError, OSError) as exc:
        sys.stderr.write(f"Error: {exc}\n")
        sys.exit(1)


if __name__ == "__main__":
    cli_entrypoint()