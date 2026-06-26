#!/usr/bin/env python3
"""
Recover a WaveSpeed TTS job after the main process was interrupted.

When send_to_api() submits a job it saves a tts_job.json file to the audio
output folder. If the process is killed before the download completes, the
job is still running (or completed) on WaveSpeed's servers — this script
polls the saved request_id and downloads the audio without resubmitting.

Usage:
    python src/tts/recover.py <path/to/tts_job.json>
    python src/tts/recover.py <request_id> <output_folder>

Requires:
    WAVESPEED_API_KEY env var (same key used during submission)
"""

import json
import os
import sys
import time
from pathlib import Path

import requests
import wavespeed

from podcast_script_generator.llm.exceptions import TTSTimeoutError


def poll_and_download(
    request_id: str,
    output_folder: str,
    api_key: str,
    max_wait_seconds: float | None = None,
) -> str:
    client = wavespeed.Client(api_key=api_key)
    out_dir = Path(output_folder)
    out_dir.mkdir(parents=True, exist_ok=True)

    if max_wait_seconds is None:
        max_wait_seconds = float(os.environ.get("WAVESPEED_MAX_WAIT_SECONDS", 3600.0))
    deadline = time.monotonic() + max_wait_seconds

    print(f"Recovering job  request_id={request_id}")
    print("Polling for completion (status every 30s)...")

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
            print(f"  [done] {elapsed:.0f}s")
            outputs = data.get("outputs", [])
            if not outputs:
                raise ValueError("Job completed but response has no outputs")
            url = outputs[0]

            filename = Path(url.split("?")[0]).name or "output.mp3"
            if not filename.endswith(".mp3"):
                filename += ".mp3"
            dest = out_dir / filename

            print(f"Downloading to {dest} ...")
            r = requests.get(url, stream=True, timeout=60)
            r.raise_for_status()
            with dest.open("wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"Saved: {dest}")

            job_file = out_dir / "tts_job.json"
            if job_file.exists():
                job_file.unlink()

            return str(dest)

        if status == "failed":
            error = data.get("error") or "Unknown error"
            raise RuntimeError(f"Job failed (id={request_id}): {error}")

        if time.monotonic() - last_report >= 30:
            print(f"  [{elapsed:.0f}s] status={status or 'processing'}...")
            last_report = time.monotonic()

        time.sleep(5)


def main() -> None:
    api_key = os.environ.get("WAVESPEED_API_KEY")
    if not api_key:
        print("Error: WAVESPEED_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) == 2:
        job_path = Path(sys.argv[1])
        if not job_path.exists():
            print(f"Error: job file not found: {job_path}", file=sys.stderr)
            sys.exit(1)
        job = json.loads(job_path.read_text(encoding="utf-8"))
        request_id = job["request_id"]
        output_folder = job["output_folder"]
        print(f"Loaded job file: {job_path}")
        print(f"  submitted_at : {job.get('submitted_at', 'unknown')}")
        print(f"  model        : {job.get('model', 'unknown')}")
    elif len(sys.argv) == 3:
        request_id = sys.argv[1]
        output_folder = sys.argv[2]
    else:
        print(__doc__)
        sys.exit(1)

    try:
        poll_and_download(request_id, output_folder, api_key)
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
