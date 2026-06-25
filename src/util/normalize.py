import re


def normalize_speakers(text: str) -> str:
    """Convert speaker label variants to clean 'Speaker N: content' lines for TTS.

    WaveSpeed VibeVoice expects Speaker 0: / Speaker 1: / Speaker 2: / Speaker 3:
    in the prompt text. Those map to API params speaker_1 / speaker_2 / speaker_3 /
    speaker_4 respectively (0-based in text, 1-based in param names — that offset is
    handled in tts/cli.py build_api_payload()).

    All label variants the LLM may emit are normalised here:

        mode_2person  — ALEX: / **ALEX:**      → Speaker 0:
                        JORDAN: / **JORDAN:**  → Speaker 1:
        all modes     — HOST: / **H:**         → Speaker 0:
                        EXPERT:/GUEST: / **E:** / EXPERT Jordan: → Speaker 1:
                        CRITIC:                → Speaker 2:
                        NEWCOMER:              → Speaker 3:
        already clean — Speaker N: / **Speaker N:** → kept as-is
    """
    lines = []
    for line in text.split("\n"):
        s = line.strip()
        if not s or s.startswith("#") or s == "---":
            continue
        s = re.sub(r"^\*\*\[[\d:,\s\-]+\]\*\*\s*", "", s)  # strip [0:00-6:00] markers
        # Markdown-bold speaker labels: **Speaker N:** (with optional role description)
        s = re.sub(r"^\*\*(Speaker\s+\d+):\*\*\s*(?:\([^)]*\))?\s*", r"\1: ", s)
        # mode_2person character names (bold or plain): ALEX = host, JORDAN = expert
        s = re.sub(r"^\*\*ALEX:\*\*\s*", "Speaker 0: ", s)
        s = re.sub(r"^ALEX:\s*", "Speaker 0: ", s)
        s = re.sub(r"^\*\*JORDAN:\*\*\s*", "Speaker 1: ", s)
        s = re.sub(r"^JORDAN:\s*", "Speaker 1: ", s)
        # Named EXPERT/GUEST with or without bold: **EXPERT Jordan:** / EXPERT Jordan:
        s = re.sub(r"^\*\*(?:EXPERT|GUEST)\s+\w+:\*\*\s*", "Speaker 1: ", s)
        s = re.sub(r"^(?:EXPERT|GUEST)\s+\w+:\s*", "Speaker 1: ", s)
        s = re.sub(r"^HOST:\s*", "Speaker 0: ", s)
        s = re.sub(r"^(GUEST|EXPERT):\s*", "Speaker 1: ", s)
        s = re.sub(r"^CRITIC:\s*", "Speaker 2: ", s)
        s = re.sub(r"^NEWCOMER:\s*", "Speaker 3: ", s)
        s = re.sub(r"^\*\*H:\*\*\s*", "Speaker 0: ", s)
        s = re.sub(r"^\*\*E:\*\*\s*", "Speaker 1: ", s)
        if s:
            lines.append(s)

    # Merge standalone label lines ("Speaker N: ") with the following content line.
    # Happens when the LLM puts the speaker label and dialogue on separate lines.
    merged = []
    i = 0
    while i < len(lines):
        s = lines[i]
        if re.match(r"^Speaker \d+:\s*$", s) and i + 1 < len(lines):
            nxt = lines[i + 1]
            if not re.match(r"^Speaker \d+:", nxt):
                merged.append(s.rstrip() + " " + nxt)
                i += 2
                continue
        merged.append(s)
        i += 1

    # Drop anything that is not a Speaker N: line — section headers, word-count
    # estimates, and other model-added noise must not reach the TTS prompt.
    merged = [s for s in merged if re.match(r"^Speaker \d+:", s)]

    return "\n\n".join(merged)
