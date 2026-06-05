# Plan: Fiction Seed Generator (2A Assist Layer)

## What and Why

The fiction pipeline (`novel_pipeline`) requires 5 human-authored template files before it can generate chapters:
- `world_laws.md` — world bible / metaphor rules
- `curriculum.md` — which concepts taught in which arc
- `style_contract.md` — prose voice rules
- `full_map.md` — full domain ↔ fiction translation tables
- `living_doc.md` — mutable state document (seeded before chapter 1)

Creating these from scratch takes hours. This feature adds an optional assist layer: given a source book PDF, it drafts all 5 files + a wired `config.toml`, so the human starts from a reviewed draft rather than a blank page. Vision.md 2A remains human-dependent — this is a scaffold, not a replacement.

**Key insight:** The 5 template files are not just output — they encode the criteria for what makes pedagogy fiction work. They are used as input to evaluate and suggest genres before any files are generated.

---

## New Module

`src/fiction/seed_gen/`

```
src/fiction/seed_gen/
  __main__.py            entry point
  cli.py                 full flow orchestration
  prompts/
    pass1_genres.txt     LLM prompt: read PDF + templates, suggest genres that fit
    pass2_files.txt      LLM prompt: generate all 5 files from approved genre + plan
  templates/             bundled instructive templates (copied from docs/fiction/directive_templates/)
    world_laws.md
    curriculum.md
    style_contract.md
    full_map.md
    living_doc.md
```

**Template source:** `docs/fiction/directive_templates/` is the editable source of truth for the 5 instructive templates. Copy them into `src/fiction/seed_gen/templates/` once when setting up the module. The bundled copies are what the tool loads at runtime — do not regenerate or overwrite them on each run.

Run as:
```bash
python -m fiction_seed_gen <source.pdf> <output_dir>
```

---

## Reuse (do not rewrite)

| What | From |
|---|---|
| `extract_pdf(pdf_path)` | `src/podcast_script_generator/llm/extract_pdf.py` |
| `call_api(pdf_text, prompt_text)` | `src/podcast_script_generator/llm/call_api.py` |
| `parse_output(response_text)` | `src/podcast_script_generator/llm/parse_output.py` |
| `save_output(files, output_dir)` | `src/podcast_script_generator/llm/save_output.py` |

Import pattern (same as `run_chapter.py`):
```python
import sys
from pathlib import Path
SRC = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SRC / "podcast_script_generator" / "llm"))
from extract_pdf import extract_pdf
from call_api import call_api
from parse_output import parse_output
from save_output import save_output
```

---

## Two-Pass Flow

### Pass 1 — Genre evaluation

1. `extract_pdf()` on the source PDF
2. Load the 5 bundled instructive templates from `src/fiction/seed_gen/templates/` as criteria reference.
   These are structural templates (they define what each output file must contain), not filled examples.
   They are static — loaded read-only, never written to.
3. Send PDF text + template content to LLM with `pass1_genres.txt` prompt
4. LLM reads the book AND the templates, then returns 3–5 genre options. For each genre it explains:
   - What the fictional world looks like
   - How the domain concepts map to the genre's mechanics
   - Why it satisfies the template criteria (narrative engine, physical grounding, failure modes, time scaling)
   - What kind of protagonist archetype fits
   - One example arc hook

Example output:

```text
Genre 1: Cultivation / martial arts
  World: power stages map to system architecture maturity
  Why it works: natural progression stages, scarcity mechanics, physical grounding
  Protagonist: apprentice starting from zero
  Arc hook: first arc — body as distributed system

Genre 2: Alchemy / crafting
  World: material transformation maps to data transformation pipelines
  Why it works: failure-and-retry is central, recipes = schemas
  Protagonist: guild apprentice learning forbidden formulae
  Arc hook: first arc — unstable reagents = dirty data

Genre 3: Heist fiction
  World: coordinated team roles map to microservices
  Why it works: planning + execution = design + deployment, betrayal = cascading failure
  Protagonist: rookie brought in for one job
  Arc hook: first arc — the job that goes wrong teaches redundancy
```

### Interactive Q&A (after Pass 1)
Print the genre proposals, then ask:

1. **Genre choice** — pick one of the numbered options (or describe a custom genre)
2. **Protagonist name** — free text (e.g. "Amina")
3. **Protagonist background / setting** — free text (e.g. "young woman, coastal East Africa")
4. **Confirm concept list** — print the AI's extracted concepts, Enter to keep or type changes
5. **Central / hardest concept** — which one should be the climax of the novel
6. **Anything the AI missed** — free text additions

Collect into a `UserPlan` dict.

### Q&A Validation Contract

**Principle:** the CLI validates all user input before anything reaches the LLM. Raw input never goes into a prompt.

**`UserPlan` structure** (exact keys and types passed to `{APPROVED_PLAN}`):

```python
UserPlan = {
    "genre_index": int,           # 1-based index into the offered genre list
    "genre_text": str,            # full genre block copied verbatim from Pass 1 output
    "protagonist_name": str,      # non-empty after strip
    "protagonist_background": str, # non-empty after strip
    "concept_list": list[str],    # min 5 items; each item non-empty after strip
    "climax_concept": str,        # must be an exact match to one item in concept_list
    "additions": str,             # may be empty string; never None
}
```

**Per-field rules:**

| Field | Bad input | Action |
| --- | --- | --- |
| Genre choice | Out of range integer | Reprompt: "Enter a number between 1 and N:" |
| Genre choice | Non-integer | Reprompt: same message |
| Genre choice | The word "custom" | Prompt for free-text genre description; store in `genre_text`, set `genre_index = 0` |
| Protagonist name | Empty after strip | Reprompt: "Name cannot be empty:" |
| Protagonist background | Empty after strip | Reprompt: "Background cannot be empty:" |
| Concept list edit | Fewer than 5 items after edit | Warn and reprompt: "Need at least 5 concepts." |
| Climax concept | Not found in concept_list (case-insensitive) | Reprompt: "Must match one of the listed concepts:" |
| Additions | Empty / blank | Store as empty string `""` — valid, no reprompt |

**Maximum retries:** 3 reprompts per field, then abort with a clear error message. Do not loop forever.

### Pass 2 — File generation

1. Build a combined prompt: `pass2_files.txt` + Pass 1 genre proposals + Q&A answers (injected as `{APPROVED_PLAN}`) + full content of the 5 bundled instructive templates (same files as Pass 1, so the LLM knows the required structure of each output file)
2. Single LLM call
3. LLM returns all 5 files using the `### FILE: filename.md` header convention (already supported by `parse_output()`)
4. Parse via `parse_output()` → dict of `{filename: content}`
5. Write the 5 `.md` files via `save_output()`
6. Write `config.toml` separately in `cli.py` — `save_output()` is for LLM-produced `.md` files only; do not extend it

### Write output

- 5 `.md` files → `<output_dir>/` via `save_output()`
- `config.toml` → `<output_dir>/config.toml` written directly by `cli.py` from a hardcoded template string
- Print: `Seed files written to <output_dir>. Review and edit them, then run: novel-pipeline --config config.toml`

---

## Generated config.toml

```toml
model = "openrouter/free"
context_limit = 200000
context_safety_margin = 8000
price_per_1m_input_tokens = 0.001
price_per_1m_output_tokens = 0.001

static_doc_paths = [
    "./world_laws.md",
    "./curriculum.md",
    "./style_contract.md",
    "./full_map.md",
]

living_doc_path = "./living_doc.md"
output_dir = "./chapters"

chapters_per_session = 3
min_chapter_words = 800
max_retries = 3
timeout_seconds = 120

cost_limit_usd_per_session = 5.00
cost_limit_usd_total = 50.00
expected_output_tokens_chapter = 4000
expected_output_tokens_update = 2000

log_path = "./pipeline.log"
state_file_path = "./.pipeline_state.json"
spend_file_path = "./.pipeline_spend.json"

required_living_doc_sections = [
    "=== LIVING DOCUMENT ===",
    "--- CURRENT STATE ---",
    "--- ACTIVE VOCABULARY ---",
    "--- TERMS LEARNED BUT NOT YET OWNED ---",
    "--- TERMS INTRODUCED THIS ARC ---",
    "--- ACTIVE FORESHADOWING ---",
    "--- PROTAGONIST LENS ---",
    "--- NEXT CHAPTER TARGET ---",
    "--- NOTES FOR AI ---",
]
```

Note: `min_chapter_words = 800` not 1500, since the current default model is a free-tier model with shorter outputs.

---

## Prompt Design

### pass1_genres.txt

The prompt receives:

- The source book text (from PDF extraction)
- The full content of the 5 bundled instructive templates from `src/fiction/seed_gen/templates/`
  (structural criteria — they tell the LLM what each output file must contain, not what to copy)

It instructs the LLM to:

- Extract 15–25 teachable domain concepts from the book
- Evaluate which fiction genres could carry those concepts
- For each genre: explain how it satisfies the template criteria (progression stages, physical grounding, failure modes, time scaling, narrative engine variety)
- Propose 3–5 genre options, ranked by fit
- For each option: world sketch, protagonist archetype, one example arc hook
- Output in a clear numbered format so the human can pick one

### pass2_files.txt

The prompt receives `{APPROVED_PLAN}` which contains:

- The chosen genre and its world sketch
- Protagonist name + background from Q&A
- Confirmed concept list + hardest concept + additions

It instructs the LLM to:

- Generate exactly 5 files using `### FILE: world_laws.md` headers
- Embed the required living doc section headers verbatim (these are sacred)
- `curriculum.md`: 7-arc table with hard/easy concepts + narrative engines
- `full_map.md`: 5+ translation tables + time scaling + 1 before/after prose example
- `living_doc.md`: exact required section headers, seeded for chapter 1

---

## CLI Interface

```
python -m fiction_seed_gen <source.pdf> <output_dir>

positional:
  source.pdf    Path to source book PDF
  output_dir    Directory to write files (created if absent)

env:
  OPENROUTER_API_KEY    required
  OPENROUTER_MODEL      optional, overrides model for generation calls
```

---

## Files to Create

| File | Lines est. | Purpose |
|---|---|---|
| `src/fiction/seed_gen/__main__.py` | ~3 | `from .cli import main; main()` |
| `src/fiction/seed_gen/cli.py` | ~140 | Full flow: args → extract → pass1 → Q&A → pass2 → write |
| `src/fiction/seed_gen/prompts/pass1_genres.txt` | ~40 | Pass 1 prompt (genre evaluation against template criteria) |
| `src/fiction/seed_gen/prompts/pass2_files.txt` | ~70 | Pass 2 prompt with `{APPROVED_PLAN}` |
| `src/fiction/seed_gen/templates/` | — | Copy from `docs/fiction/directive_templates/` once at setup. Do not regenerate. |

No new dependencies. Uses the existing `src/.venv` (fitz and requests already installed).

---

## Verification

1. Run against any chapter PDF already in the project
2. Confirm Pass 1 output shows 3–5 genre options with reasoning tied to template criteria
3. Pick a genre, answer Q&A with a different protagonist than Amina
4. Confirm all 5 `.md` files written to output dir
5. Confirm `config.toml` written with correct relative paths
6. Run `novel-pipeline --config <output_dir>/config.toml --dry-run` from `<output_dir>` — must load all 4 static docs without error
