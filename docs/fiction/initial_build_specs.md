# Build Specs: Fiction Seed Generator

Reference: [initial_plan.md](initial_plan.md)

---

## Build Order

1. Copy `docs/fiction/directive_templates/*.md` → `src/fiction/seed_gen/templates/`
2. Create `src/fiction/seed_gen/__main__.py`
3. Create `src/fiction/seed_gen/cli.py` — stub `main()` that prints "ok" and exits
4. Implement `load_templates()` and verify all 5 files load
5. Write `src/fiction/seed_gen/prompts/pass1_genres.txt`
6. Implement Pass 1: `extract_pdf` → `truncate_pdf_text` → `build_pass1_prompt` → `call_api` → `validate_pass1_response` → print
7. Implement `collect_user_plan()` with full validation (see Validation section)
8. Write `src/fiction/seed_gen/prompts/pass2_files.txt`
9. Implement Pass 2: `build_pass2_prompt` → `call_api` → `parse_output` → `save_output`
10. Implement `write_config_toml()`
11. Verify end-to-end against a real PDF (see Verification in initial_plan.md)

---

## File: `src/fiction/seed_gen/__main__.py`

```python
from .cli import main
main()
```

---

## File: `src/fiction/seed_gen/cli.py`

### Imports and path setup

```python
import argparse
import sys
from pathlib import Path

SRC = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SRC / "podcast_script_generator" / "llm"))

from extract_pdf import extract_pdf
from call_api import call_api
from parse_output import parse_output
from save_output import save_output

TEMPLATES_DIR = Path(__file__).parent / "templates"
PROMPTS_DIR = Path(__file__).parent / "prompts"
```

### Function signatures and contracts

#### `parse_args() -> argparse.Namespace`

Two positional arguments: `source_pdf` (str) and `output_dir` (str).
No optional flags. Fail fast with argparse default error if either is missing.

#### `load_templates() -> dict[str, str]`

Load all 5 `.md` files from `TEMPLATES_DIR`. Return `{filename: content}`.
Raise `FileNotFoundError` with a clear message if any of the 5 expected files is missing:
`world_laws.md`, `curriculum.md`, `style_contract.md`, `full_map.md`, `living_doc.md`.

```python
EXPECTED_TEMPLATES = [
    "world_laws.md", "curriculum.md", "style_contract.md",
    "full_map.md", "living_doc.md",
]
```

#### `truncate_pdf_text(text: str) -> str`

Hard limit: **120,000 characters** (well within free-tier context windows after adding prompt + templates).

```python
PDF_CHAR_LIMIT = 120_000

def truncate_pdf_text(text: str) -> str:
    if len(text) <= PDF_CHAR_LIMIT:
        return text
    truncated = text[:PDF_CHAR_LIMIT]
    print(f"[warning] PDF text truncated from {len(text):,} to {PDF_CHAR_LIMIT:,} characters.")
    return truncated + "\n\n[... PDF truncated due to context limit ...]"
```

Called in `main()` immediately after `extract_pdf()`, before building any prompt.
Do not truncate inside `extract_pdf()` — keep truncation visible at the call site.

#### `build_pass1_prompt(templates: dict[str, str]) -> str`

Load `PROMPTS_DIR / "pass1_genres.txt"`. Inject the 5 templates into it by replacing
the `{TEMPLATES}` placeholder with the concatenated template contents (each prefixed by
its filename as a header). Return the completed prompt string.

The PDF text is NOT injected here — it is passed separately as `pdf_text` to `call_api`.

#### `validate_pass1_response(response: str) -> None`

Called immediately after Pass 1 `call_api()` returns, before printing or entering Q&A.
Raises `ValueError` if the response contains no parseable genre proposals.

Detection rule: the response must contain at least one line matching `Genre \d+:` (case-insensitive).

```python
import re

def validate_pass1_response(response: str) -> None:
    if not re.search(r"(?i)^genre\s+\d+\s*:", response, re.MULTILINE):
        print("--- Raw LLM response ---")
        print(response)
        print("------------------------")
        raise ValueError(
            "Pass 1 returned no genre proposals. "
            "Raw response printed above. Check your API key, model, and PDF content."
        )
```

On `ValueError`: catch in `main()`, print the message, and `sys.exit(1)`. Do not enter Q&A.

#### `build_pass2_prompt(user_plan: dict, pass1_response: str, templates: dict[str, str]) -> str`

Load `PROMPTS_DIR / "pass2_files.txt"`. Inject two placeholders:

- `{APPROVED_PLAN}` — formatted string built from `user_plan` (see UserPlan section)
- `{PASS1_PROPOSALS}` — the raw Pass 1 response text
- `{TEMPLATES}` — same concatenated template block as in Pass 1

Return the completed prompt string.
Pass 2 does not send pdf_text — call `call_api(pdf_text="", prompt_text=...)`.

#### `collect_user_plan(pass1_response: str) -> dict`

Runs the interactive Q&A. See Validation Contract below for per-field rules.
Returns a `UserPlan` dict (see UserPlan section).

#### `write_config_toml(output_dir: Path) -> None`

Write `config.toml` directly from the hardcoded template string below.
Do NOT use `save_output()` for this — `save_output()` is for LLM-produced `.md` files only.

#### `main() -> None`

```
parse_args()
→ load_templates()
→ extract_pdf(source_pdf)              # returns str
→ truncate_pdf_text(book_text)         # hard limit 120,000 chars; warns if truncated
→ build_pass1_prompt(templates)        # returns str
→ call_api(pdf_text=book_text, prompt_text=pass1_prompt)
→ validate_pass1_response(response)    # raises ValueError + sys.exit(1) if no genres found
→ print Pass 1 response
→ collect_user_plan(pass1_response) → user_plan dict
→ build_pass2_prompt(user_plan, pass1_response, templates)
→ call_api(pdf_text="", prompt_text=pass2_prompt)
→ parse_output(pass2_response)         # returns list[tuple[str, str]]
→ save_output(files, str(output_dir))
→ write_config_toml(output_dir)
→ print success message
```

**Error handling in `main()`:** wrap the full flow in a `try/except` that catches `RuntimeError`
(from `call_api` after exhausted retries) and `ValueError` (from `validate_pass1_response`).
Print `f"Error: {e}"` to stderr and `sys.exit(1)`. Do not let tracebacks reach the user.

---

## Reused Function Call Patterns

Exact signatures from `src/podcast_script_generator/llm/`:

```python
extract_pdf(pdf_path: str) -> str
call_api(pdf_text: str, prompt_text: str) -> str
parse_output(response_text: str) -> list[tuple[str, str]]
save_output(files: list[tuple[str, str]], output_dir: str) -> None
```

**`call_api` combining behavior:** if `pdf_text` is non-empty, the message sent to the LLM
is `f"{prompt_text}\n\n---\n\n{pdf_text}"`. If `pdf_text=""`, only `prompt_text` is sent.

**Pass 1 call:**
```python
response = call_api(pdf_text=book_text, prompt_text=pass1_prompt)
```

**Pass 2 call:**
```python
response = call_api(pdf_text="", prompt_text=pass2_prompt)
```
All context for Pass 2 (approved plan, Pass 1 proposals, templates) is in `pass2_prompt`.

**`save_output` note:** takes `output_dir` as `str`, not `Path`. Pass `str(output_dir)`.

---

## UserPlan Dict

```python
UserPlan = {
    "genre_index": int,            # 1-based; 0 if custom genre
    "genre_text": str,             # full genre block from Pass 1 output, or free-text if custom
    "protagonist_name": str,       # non-empty, stripped
    "protagonist_background": str, # non-empty, stripped
    "concept_list": list[str],     # min 5 items, each non-empty stripped string
    "climax_concept": str,         # exact match (case-insensitive) to one item in concept_list
    "additions": str,              # may be empty string ""
}
```

Format `UserPlan` for `{APPROVED_PLAN}` injection as a readable block:

```
Genre: {genre_text}
Protagonist: {protagonist_name}
Background: {protagonist_background}
Concepts: {concept_list joined with ", "}
Climax concept: {climax_concept}
Additional notes: {additions or "none"}
```

---

## Validation Contract

**Principle:** CLI validates all input before anything reaches the LLM. Raw user input never enters a prompt.
**Max retries per field:** 3. On 4th failure, print error and `sys.exit(1)`.

| Field | Bad input | Action |
| --- | --- | --- |
| Genre choice | Non-integer | Reprompt: `"Enter a number between 1 and N:"` |
| Genre choice | Integer out of range | Reprompt: same message |
| Genre choice | `"custom"` (case-insensitive) | Prompt for free-text genre; set `genre_index=0`, store in `genre_text` |
| Protagonist name | Empty after strip | Reprompt: `"Name cannot be empty:"` |
| Protagonist background | Empty after strip | Reprompt: `"Background cannot be empty:"` |
| Concept list edit | Fewer than 5 items after edit | Warn and reprompt: `"Need at least 5 concepts."` |
| Climax concept | Not in concept_list (case-insensitive) | Reprompt: `"Must match one of the listed concepts:"` |
| Additions | Empty / blank | Accept — store as `""`, no reprompt |

**Concept list display and edit:**
Print the AI-extracted concepts as a numbered list. User presses Enter to accept as-is,
or types a replacement list (comma-separated). After edit, strip each item and drop empty strings.

---

## Prompt Files

### `prompts/pass1_genres.txt`

Must contain the placeholder `{TEMPLATES}`.
Must instruct the LLM to:

1. Read the book text that follows the `---` separator
2. Read the 5 structural templates in `{TEMPLATES}` — these define the required structure of each output file
3. Extract 15–25 teachable domain concepts from the book
4. Propose 3–5 fiction genres that can carry those concepts
5. For each genre, provide:
   - What the fictional world looks like
   - How the domain concepts map to the genre's mechanics
   - Why it satisfies the template criteria (progression stages, physical grounding, failure modes, time scaling, narrative engine variety)
   - Protagonist archetype
   - One example arc hook
6. Output in a numbered format: `Genre 1: ...`, `Genre 2: ...` etc.
7. After the genre proposals, print the extracted concept list under the header `## Extracted Concepts`

The concept list under `## Extracted Concepts` is what `collect_user_plan()` displays to the user
for confirmation. The prompt must guarantee this section appears and is parseable.

### `prompts/pass2_files.txt`

Must contain placeholders: `{APPROVED_PLAN}`, `{PASS1_PROPOSALS}`, `{TEMPLATES}`.
Must instruct the LLM to:

1. Read the approved plan in `{APPROVED_PLAN}` and the Pass 1 genre proposals in `{PASS1_PROPOSALS}`
2. Read the 5 structural templates in `{TEMPLATES}` — generate output that satisfies every structural requirement in each template
3. Generate exactly 5 files using `### FILE: filename.md` headers (one per file, required by `parse_output()`)
4. The sacred living doc section headers must appear verbatim (list them explicitly in the prompt):
   ```
   === LIVING DOCUMENT ===
   --- CURRENT STATE ---
   --- ACTIVE VOCABULARY ---
   --- TERMS LEARNED BUT NOT YET OWNED ---
   --- TERMS INTRODUCED THIS ARC ---
   --- ACTIVE FORESHADOWING ---
   --- PROTAGONIST LENS ---
   --- NEXT CHAPTER TARGET ---
   --- NOTES FOR AI ---
   ```
5. `curriculum.md`: 7-arc table with hard/easy concepts + narrative engines
6. `full_map.md`: 5+ translation tables + time scaling + 1 before/after prose example
7. `living_doc.md`: seeded for chapter 0 (not yet started)

---

## `config.toml` Template String

Written by `write_config_toml(output_dir: Path)` directly. No LLM involvement.

```python
CONFIG_TOML = """\
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
"""
```

---

## Corrections to initial_plan.md

These were wrong in the plan — the build spec is authoritative:

- `parse_output()` returns `list[tuple[str, str]]`, not `dict`. The plan said "dict of `{filename: content}`" — incorrect.
- Pass 2 calls `call_api(pdf_text="", prompt_text=...)`, not `call_api(pdf_text=book_text, ...)`. The raw PDF is not needed in Pass 2; all context is in the prompt.
