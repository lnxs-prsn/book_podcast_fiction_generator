#!/usr/bin/env python3
"""Extract text from a chapter PDF and generate a structured, paraphrased podcast script."""

import os
import sys
import re
import hashlib
from pathlib import Path
from collections import Counter

try:
    from pypdf import PdfReader
except ImportError:
    print("Error: pypdf is required. Install it with: pip install pypdf")
    sys.exit(1)


def _dhash(text: str, idx: int) -> int:
    """Deterministic hash for picking templates."""
    return int(hashlib.md5((text + str(idx)).encode()).hexdigest(), 16)


def _pick(options: list, seed: str, idx: int) -> str:
    h = _dhash(seed, idx)
    return options[h % len(options)]


def extract_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    parts = []
    for page in reader.pages:
        txt = page.extract_text()
        if txt:
            parts.append(txt)
    return "\n".join(parts).strip()


def clean_text(text: str) -> str:
    # Drop standalone page numbers and repeated short lines (headers/footers)
    text = re.sub(r"\n\s*\d+\s*\n", "\n", text)
    lines = text.split("\n")
    counts = Counter(l.strip() for l in lines if l.strip())
    filtered = []
    for line in lines:
        s = line.strip()
        if s and counts[s] >= 3 and len(s) < 60:
            continue
        filtered.append(s)
    return " ".join(filtered)


def split_thirds(text: str) -> tuple:
    text = text.strip()
    if not text:
        return "", "", ""
    n = len(text)
    t = n // 3
    tt = 2 * t

    def snap(idx):
        end = min(idx + 400, n)
        for i in range(idx, end):
            if text[i] in ".!?" and i + 1 < n and text[i + 1] in " \n":
                return i + 2
        return idx

    s1 = snap(t)
    s2 = snap(tt)
    return text[:s1].strip(), text[s1:s2].strip(), text[s2:].strip()


def get_sentences(text: str) -> list:
    raw = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in raw if len(s.strip()) > 25]


def extract_concepts(chunk: str, full_text: str, num_concepts: int = 4) -> list:
    """Return short concept labels (e.g., 'Stemming', 'BERT') extracted from the chunk."""
    sentences = get_sentences(chunk)
    if not sentences:
        return [f"topic {i}" for i in range(1, num_concepts + 1)]

    full_words = Counter(re.findall(r"\b[a-zA-Z]{4,}\b", full_text.lower()))
    chunk_words = Counter(re.findall(r"\b[a-zA-Z]{4,}\b", chunk.lower()))

    scored = []
    for sent in sentences:
        words = re.findall(r"\b[a-zA-Z]{4,}\b", sent.lower())
        if len(words) < 3:
            continue
        score = 0
        for w in words:
            cf = chunk_words[w]
            ff = full_words.get(w, 0)
            if ff > 0:
                score += (cf / len(chunk_words)) / (ff / len(full_words))
            else:
                score += 2.0
        score /= len(words)
        if len(sent) > 350:
            score *= 0.3
        scored.append((score, sent))

    scored.sort(reverse=True)

    concepts = []
    used = set()
    common = {
        "this", "that", "these", "those", "there", "their", "chapter", "section",
        "figure", "table", "example", "following", "however", "therefore",
        "because", "although", "another", "important", "different", "various",
        "several", "certain", "specific", "general", "common", "similar",
    }

    for _, sent in scored[: num_concepts * 3]:
        if len(concepts) >= num_concepts:
            break

        candidates = (
            re.findall(r'"([^"]{3,40})"', sent)
            + re.findall(r"'([^']{3,40})'", sent)
            + re.findall(r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,3})\b", sent)
            + re.findall(r"\b([a-zA-Z]{6,}(?:\s+[a-zA-Z]{4,}){0,2})\b", sent)
        )

        for cand in candidates:
            c = cand.strip()
            if len(c) < 4 or len(c) > 50:
                continue
            key = c.lower()
            if key in used or key in common:
                continue
            used.add(key)
            concepts.append(c)
            break

    while len(concepts) < num_concepts:
        concepts.append(f"concept {len(concepts) + 1}")

    return concepts[:num_concepts]


def generate_dialogue(concepts: list, part_num: int) -> list:
    """Host asks, Guest explains with analogy, Host probes, Guest deepens."""
    lines = []
    n = min(max(len(concepts), 3), 5)

    openers = [
        "Let's dig into what is actually going on here.",
        "This is where the chapter starts to get interesting.",
        "I want to make sure we are not just skimming the surface.",
        "Before we move on, let's unpack the mechanics.",
        "Here is the part that I think confuses a lot of people.",
    ]
    lines.append(f"HOST: {_pick(openers, str(part_num), 0)}")
    lines.append("")

    for i in range(n):
        name = concepts[i % len(concepts)]
        seed = name + str(part_num) + str(i)

        analogies = [
            f"Think of {name} like tuning an instrument before a concert. You could play without tuning, but everything afterward sounds slightly off.",
            f"The way I explain {name} to students is: imagine you are packing for a trip. You have to decide what to bring, what to leave behind, and how to organize it so you can actually find things later.",
            f"If you want an analogy, {name} is like the difference between a rough sketch and a blueprint. Both show the same building, but one lets you actually construct it.",
            f"Picture a kitchen where no one ever puts the tools back in the same place. That chaos is what happens when you ignore {name}.",
            f"My favorite comparison is to gardening. {name} is not the plant itself; it is the soil preparation. Boring to watch, but everything else depends on it.",
        ]
        lines.append(f"GUEST: {_pick(analogies, seed, 0)}")
        lines.append("")

        questions = [
            f"Where does {name} fit into the bigger pipeline? Is it a preprocessing step, or something you do after you have already built a model?",
            f"That makes sense conceptually, but what does {name} actually look like in code or in practice? Can you ground it?",
            f"How do we know {name} is working? What is the failure mode — what happens when you get it wrong?",
            f"Is {name} universal, or does it depend on the language or the domain you are working in?",
            f"Who figured this out first? Is {name} a recent invention, or has it been around and we just gave it a new name?",
        ]
        lines.append(f"HOST: {_pick(questions, seed, 1)}")
        lines.append("")

        answers = [
            f"It depends on your goal. If you are optimizing for speed, you handle {name} one way. If you are optimizing for accuracy, you do the opposite. Most production systems end up somewhere in the middle, and that tension is where the interesting engineering lives.",
            f"The failure mode is subtle. You do not get an error message; you get slightly worse results everywhere, and you waste weeks chasing the wrong hypothesis because your foundation was shaky.",
            f"It is older than people think. The foundations were laid decades ago, but the recent resurgence happened because scale changed the economics. What was too expensive to compute in 2005 is trivial now, so {name} became practical.",
            f"In practice, you usually combine it with other techniques. {name} alone is rarely enough. The art is knowing which combination to use and in what order.",
            f"The domain question is crucial. {name} works beautifully for structured data, but throw it at social media text and you will discover edge cases the original designers never imagined.",
        ]
        lines.append(f"GUEST: {_pick(answers, seed, 2)}")
        lines.append("")

        if i < n - 1:
            pushes = [
                "So the takeaway is not just 'do this step,' but 'understand why you are doing it.'",
                "That is a good reminder that the textbook version and the production version are rarely the same thing.",
                "It sounds like the real skill is knowing when to follow the rulebook and when to throw it out.",
                "I want to hold that thought and move to the next piece.",
                "Before we get too abstract, let's look at another angle.",
            ]
            lines.append(f"HOST: {_pick(pushes, seed, 3)}")
            lines.append("")

    return lines


def generate_podcast_script(pdf_path: str, text: str) -> str:
    filename = Path(pdf_path).stem
    chapter_title = filename.replace("_", " ").replace("-", " ")

    beginning, middle, end = split_thirds(text)
    if not beginning:
        raise ValueError(f"No extractable text in {Path(pdf_path).name}")

    concepts1 = extract_concepts(beginning, text)
    concepts2 = extract_concepts(middle, text)
    concepts3 = extract_concepts(end, text)

    lines = []
    lines.append(f"# Podcast Script: {chapter_title}")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Intro")
    lines.append("")
    lines.append(
        f"HOST: Welcome. Today we are walking through **{chapter_title}**. The goal is not to read the chapter aloud, "
        "but to pull out the ideas that matter and talk through them like we are sitting across a table with coffee."
    )
    lines.append("")
    lines.append(
        "GUEST: That is the right approach. There is a clear arc in this chapter — setup, core mechanics, and payoff — "
        "and it is worth tracing that arc deliberately."
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## Part 1 — The Setup")
    lines.append("")
    lines.extend(generate_dialogue(concepts1, 1))
    lines.append("---")
    lines.append("")

    lines.append("## Part 2 — The Core")
    lines.append("")
    lines.extend(generate_dialogue(concepts2, 2))
    lines.append("---")
    lines.append("")

    lines.append("## Part 3 — The Payoff")
    lines.append("")
    lines.extend(generate_dialogue(concepts3, 3))
    lines.append("---")
    lines.append("")

    lines.append("## Outro")
    lines.append("")
    lines.append(
        f"HOST: That wraps up our walkthrough of **{chapter_title}**. We started with the landscape, moved through the mechanics, "
        "and ended with why any of it matters. Thanks for the conversation."
    )
    lines.append("")
    lines.append("GUEST: Thank you. Re-reading it this way always makes me notice connections I missed the first time.")
    lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python podcast_generator.py <path_to_chapter_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        sys.exit(1)

    raw = extract_text(pdf_path)
    if not raw:
        raise ValueError(f"No extractable text in {Path(pdf_path).name}")

    text = clean_text(raw)

    filename = Path(pdf_path).stem
    out_dir = Path("data/output/podcast")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{filename}_podcast.md"

    script = generate_podcast_script(pdf_path, text)
    segments = script.count("HOST:") + script.count("GUEST:")

    print(f"Will write podcast script: {out_path.name} to {out_dir} ({segments} dialogue segments).")
    if input("Press Enter to confirm...") != "":
        print("Aborted.")
        sys.exit(0)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(script)

    print(f"Done. Written to {out_path}")


if __name__ == "__main__":
    main()
