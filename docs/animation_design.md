# Animation Storyboard Pipeline — Design Document

**Status:** Parked. Not built. Design only.
**Revisit when:** LLM image/video generation costs drop to approximately $0.50–$1.00 per scene.

---

## What This Stage Does

Takes chapter text as input and produces a visual narrative storyboard — a scene-by-scene breakdown that could be handed to an animator, image generator, or used as a storyboard for a video.

This is Stage 5 in the pipeline. It is a sibling of the podcast and fiction generators, not downstream of them. It reads directly from the same chapter text that all other generators use.

```
[ CHAPTER PDF ]
      │
      ├──► Stage 2 → Podcast script → Stage 3 → Audio
      ├──► Stage 4 → Fiction chapter
      └──► Stage 5 → Animation storyboard   ← this document
```

---

## Input

- A chapter PDF (same as all other stages)
- Or optionally: a pre-extracted text file from Stage 1's output

No stage feeds this one. Storyboards are generated from source material directly.

---

## Output

A markdown storyboard file per chapter: `data/output/animation/<chapter_stem>_storyboard.md`

---

## Storyboard Format (per scene)

Each chapter produces approximately 6–10 scenes. Each scene contains:

```markdown
## Scene 3 of 8

**Setting:** A narrow practice courtyard at dusk. Stone walls. A single oil lamp.

**Characters:** Amina (foreground), Elder Wei (background, seated).

**Action:** Amina attempts the second form. Her right arm moves correctly;
her left hesitates. She freezes mid-form. Elder Wei does not react.

**Dialogue beat:**
  AMINA (internal): *The left arm does not believe the right arm has finished.*

**Visual metaphor:** Split-screen or double exposure showing the two arms
as separate systems with a gap between them — the gap is the latency.

**Teaching concept:** Asynchrony. Two processes with independent timing.
The metaphor is the gap — not the failure, but the space between.

**Mood:** Quiet frustration. No drama. The failure is technical, not emotional.

**Transition:** Cut to night. Amina sitting alone, both arms moving in sync.
```

---

## Implementation Plan (when cost allows)

### Stage 5a — Storyboard generator (text only, buildable now)

**What:** LLM call that takes chapter text and returns storyboard markdown.
No images. Pure text output.

**Cost:** ~$0.05–0.15 per chapter at current LLM rates. **Viable now.**

**File:** `src/storyboard/generate_storyboard.py`

**Interface:**
```
python src/storyboard/generate_storyboard.py <chapter.pdf>
→ data/output/animation/<stem>_storyboard.md
```

**Prompt strategy:** Send chapter text + a brief instruction set. The LLM
identifies the 6–10 key visual moments, writes each in the scene format above.
The teaching concept field ensures the visual metaphor stays pedagogically
accurate.

---

### Stage 5b — Scene image generation (requires lower cost)

**What:** For each scene in the storyboard, generate one image.

**Current cost estimate (2026):**
- Midjourney/DALL-E 3: ~$0.04–0.08 per image
- Stable Diffusion (self-hosted): ~$0.001–0.005 per image (GPU time)
- At 8 scenes per chapter, 25 chapters: 200 images total
- At $0.04/image: ~$8 total. **Already viable if quality is acceptable.**
- At $0.08/image: ~$16 total. **Marginal but feasible.**

**Prompt source:** The `Setting`, `Characters`, `Action`, and `Visual metaphor`
fields from each scene card become the image prompt.

**File:** `src/storyboard/generate_images.py`

---

### Stage 5c — Video assembly (future)

**What:** Assemble scene images + audio narration into a short animated video.

**Tools to evaluate:** Kling AI, Runway Gen-3, Pika Labs (for animating stills),
or FFmpeg with Ken Burns effect for a simpler approach.

**Current cost:** $0.10–1.00 per second of video. A 3–5 minute chapter video
would cost $18–300. **Not viable at current rates.**

**Revisit when:** Per-second generation cost drops below $0.05.

---

## Decision Needed Before Building Stage 5a

1. **Storyboard for which content?** NLP book chapters, the cultivation novel, or both?
2. **Target output?** Printable storyboard PDF, web page, or input to an image generator?
3. **Scene count per chapter?** 6 scenes is a lightweight pass; 12 is a thorough visual breakdown.

Stage 5a (text storyboard only) can be built in one session once these are decided.
It requires no new API keys if using OpenRouter (already configured).

---

## What Is NOT Needed to Start Stage 5a

- No image generation capability
- No video tools
- No new API keys
- No changes to existing stages

The text storyboard generator is a ~60 line script with one LLM call.
It can be built and tested on a single chapter in under an hour.

---

## Cost Summary

| Sub-stage | Cost per chapter | Cost for 25 chapters | Viable now? |
|---|---|---|---|
| 5a — Text storyboard | $0.05–0.15 | $1.25–3.75 | Yes |
| 5b — Scene images | $0.32–0.64 | $8–16 | Marginal |
| 5c — Video assembly | $18–300 | $450–7500 | No |
