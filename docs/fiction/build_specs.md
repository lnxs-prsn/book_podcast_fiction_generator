# Build Specs: Fiction Seed Generator

References: [initial_plan.md](initial_plan.md) | [initial_build_specs.md](initial_build_specs.md)

Each phase is self-contained. Complete all passes in a phase before moving to the next.
Commit after every pass.

---

## Phase 01 — Module Scaffold

**Goal:** Skeleton exists. Module is importable. No logic yet.

### Pass 1 — Copy templates

Copy `docs/fiction/directive_templates/*.md` → `src/fiction/seed_gen/templates/`.
Verify all 5 files are present:

```bash
ls src/fiction/seed_gen/templates/
# expected: curriculum.md  full_map.md  living_doc.md  style_contract.md  world_laws.md
```

Commit.

### Pass 2 — Create module skeleton

Create the following files:

**`src/fiction/seed_gen/__main__.py`**
```python
from .cli import main
main()
```

**`src/fiction/seed_gen/cli.py`** — stub only:
```python
def main():
    print("fiction-seed-gen: ok")
```

Create empty directories:
- `src/fiction/seed_gen/prompts/` — add a `.gitkeep`

Verify:
```bash
python -m src.fiction.seed_gen
# expected output: fiction-seed-gen: ok
```

Commit.

---

## Phase 02 — Template Loading

**Goal:** `load_templates()` works and fails clearly if templates are missing.

### Pass 1 — Imports and constants

Add to `cli.py`:

```python
import argparse
import re
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
PDF_CHAR_LIMIT = 120_000

EXPECTED_TEMPLATES = [
    "world_laws.md", "curriculum.md", "style_contract.md",
    "full_map.md", "living_doc.md",
]
```

Verify imports resolve without error (run `python -m src.fiction.seed_gen`).

Commit.

### Pass 2 — `load_templates()`

```python
def load_templates() -> dict[str, str]:
    missing = [f for f in EXPECTED_TEMPLATES if not (TEMPLATES_DIR / f).exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing bundled templates in {TEMPLATES_DIR}: {missing}\n"
            f"Copy from docs/fiction/directive_templates/"
        )
    return {f: (TEMPLATES_DIR / f).read_text(encoding="utf-8") for f in EXPECTED_TEMPLATES}
```

Verify: call `load_templates()` in `main()` and print the keys. Confirm all 5 appear.
Then remove the debug print.

Commit.

---

## Phase 03 — Pass 1 (Genre Evaluation)

**Goal:** Given a PDF, print 3–5 genre proposals from the LLM. Validate before showing to user.

### Pass 1 — `truncate_pdf_text()` and `parse_args()`

```python
def truncate_pdf_text(text: str) -> str:
    if len(text) <= PDF_CHAR_LIMIT:
        return text
    print(f"[warning] PDF text truncated from {len(text):,} to {PDF_CHAR_LIMIT:,} characters.")
    return text[:PDF_CHAR_LIMIT] + "\n\n[... PDF truncated due to context limit ...]"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fiction seed generator")
    parser.add_argument("source_pdf", help="Path to source book PDF")
    parser.add_argument("output_dir", help="Directory to write output files")
    return parser.parse_args()
```

Commit.

### Pass 2 — Write `prompts/pass1_genres.txt`

The prompt file must:

- Contain the placeholder `{TEMPLATES}` where the 5 structural templates will be injected
- Instruct the LLM to read the book text after the `---` separator
- Instruct the LLM to read the 5 structural templates as criteria for what each output file must contain
- Ask it to extract 15–25 teachable domain concepts from the book
- Ask it to propose 3–5 fiction genres, ranked by fit
- For each genre specify: world sketch, how concepts map to genre mechanics, why it satisfies template criteria (progression stages, physical grounding, failure modes, time scaling, narrative engine), protagonist archetype, one example arc hook
- Output format: `Genre 1: ...`, `Genre 2: ...` — numbered, one per block
- After genre proposals, output the extracted concept list under the exact header `## Extracted Concepts` (one concept per line)

The `## Extracted Concepts` header is machine-read by `collect_user_plan()` — it must appear verbatim.

Commit.

### Pass 3 — `build_pass1_prompt()` and `validate_pass1_response()`

```python
def _format_templates(templates: dict[str, str]) -> str:
    return "\n\n".join(
        f"### {name}\n{content}" for name, content in templates.items()
    )


def build_pass1_prompt(templates: dict[str, str]) -> str:
    prompt = (PROMPTS_DIR / "pass1_genres.txt").read_text(encoding="utf-8")
    return prompt.replace("{TEMPLATES}", _format_templates(templates))


def validate_pass1_response(response: str) -> None:
    if not re.search(r"(?i)^genre\s+\d+\s*:", response, re.MULTILINE):
        print("\n--- Raw LLM response ---")
        print(response)
        print("------------------------")
        raise ValueError(
            "Pass 1 returned no genre proposals. "
            "Raw response printed above. Check your API key, model, and PDF content."
        )
```

Commit.

### Pass 4 — Wire Pass 1 in `main()`

```python
def main() -> None:
    try:
        args = parse_args()
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        templates = load_templates()
        book_text = truncate_pdf_text(extract_pdf(args.source_pdf))
        pass1_prompt = build_pass1_prompt(templates)

        print("Running Pass 1: genre evaluation...")
        pass1_response = call_api(pdf_text=book_text, prompt_text=pass1_prompt)
        validate_pass1_response(pass1_response)
        print(pass1_response)

    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
```

Verify: run against a real PDF. Confirm 3–5 genre proposals print to terminal.
If LLM call is too slow for testing, stub `call_api` temporarily to return a hardcoded fixture.

Commit.

---

## Phase 04 — Interactive Q&A

**Goal:** `collect_user_plan()` gathers and validates all 6 inputs. Returns a clean `UserPlan` dict.

### Pass 1 — Extract concept list from Pass 1 response

```python
def _parse_concept_list(pass1_response: str) -> list[str]:
    match = re.search(r"## Extracted Concepts\n(.*?)(?:\n##|\Z)", pass1_response, re.DOTALL)
    if not match:
        return []
    lines = [l.strip().lstrip("-•* ") for l in match.group(1).strip().splitlines()]
    return [l for l in lines if l]
```

Commit.

### Pass 2 — `_prompt_field()` helper and genre choice

```python
def _prompt_field(prompt: str, validator, max_retries: int = 3) -> str:
    for _ in range(max_retries):
        value = input(prompt).strip()
        result = validator(value)
        if result is not None:
            return result
        # validator returns None to signal invalid — loop reprompts
    print("Too many invalid attempts. Aborting.", file=sys.stderr)
    sys.exit(1)
```

Genre choice validator: accepts integer in `[1, N]` or the word `"custom"`.

Commit.

### Pass 3 — Full `collect_user_plan()`

Implements all 6 Q&A fields with validation per the contract in `initial_build_specs.md`:

| Field | Validation |
| --- | --- |
| Genre choice | Integer in range or `"custom"` |
| Protagonist name | Non-empty after strip |
| Protagonist background | Non-empty after strip |
| Concept list | Display extracted list, Enter to keep or retype; min 5 items |
| Climax concept | Must match one item in concept_list (case-insensitive) |
| Additions | Empty string accepted |

Returns `UserPlan` dict with exact keys defined in `initial_build_specs.md`.

Commit.

---

## Phase 05 — Pass 2 (File Generation)

**Goal:** Given the approved plan, generate and write all 5 output files.

### Pass 1 — Write `prompts/pass2_files.txt`

The prompt file must contain placeholders: `{APPROVED_PLAN}`, `{PASS1_PROPOSALS}`, `{TEMPLATES}`.

Must instruct the LLM to:

- Read the approved plan and Pass 1 proposals as the genre + concept brief
- Read the 5 structural templates as the required output structure for each file
- Generate exactly 5 files using `### FILE: filename.md` headers (required by `parse_output()`)
- Embed the living doc section headers verbatim — list them explicitly in the prompt:
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
- `curriculum.md`: 7-arc table — Hard Concept, Easy Pairing, Narrative Engine per arc
- `full_map.md`: 5 translation tables + time scaling + 1 before/after prose example
- `living_doc.md`: all sacred section headers, seeded for chapter 0

Commit.

### Pass 2 — `build_pass2_prompt()` and `_format_user_plan()`

```python
def _format_user_plan(user_plan: dict) -> str:
    return (
        f"Genre: {user_plan['genre_text']}\n"
        f"Protagonist: {user_plan['protagonist_name']}\n"
        f"Background: {user_plan['protagonist_background']}\n"
        f"Concepts: {', '.join(user_plan['concept_list'])}\n"
        f"Climax concept: {user_plan['climax_concept']}\n"
        f"Additional notes: {user_plan['additions'] or 'none'}"
    )


def build_pass2_prompt(user_plan: dict, pass1_response: str, templates: dict[str, str]) -> str:
    prompt = (PROMPTS_DIR / "pass2_files.txt").read_text(encoding="utf-8")
    return (
        prompt
        .replace("{APPROVED_PLAN}", _format_user_plan(user_plan))
        .replace("{PASS1_PROPOSALS}", pass1_response)
        .replace("{TEMPLATES}", _format_templates(templates))
    )
```

Commit.

### Pass 3 — `write_config_toml()` and wire Pass 2 in `main()`

`write_config_toml()`: write the hardcoded `CONFIG_TOML` string from `initial_build_specs.md`
directly to `output_dir / "config.toml"`. Do not use `save_output()`.

Add Pass 2 to `main()` after Q&A:

```python
print("\nRunning Pass 2: generating files...")
pass2_prompt = build_pass2_prompt(user_plan, pass1_response, templates)
pass2_response = call_api(pdf_text="", prompt_text=pass2_prompt)
files = parse_output(pass2_response)
save_output(files, str(output_dir))
write_config_toml(output_dir)
print(f"\nSeed files written to {output_dir}.")
print(f"Review and edit them, then run: novel-pipeline --config {output_dir}/config.toml")
```

Commit.

---

## Phase 06 — Verification

**Goal:** Confirm the full flow works end-to-end against a real PDF.

### Pass 1 — Run end-to-end

```bash
python -m src.fiction.seed_gen <path/to/book.pdf> /tmp/seed_test
```

Check:
- Pass 1 prints 3–5 genre proposals
- Q&A loop runs cleanly, reprompts on bad input
- Pass 2 runs and writes 5 `.md` files + `config.toml` to `/tmp/seed_test`

Commit.

### Pass 2 — Validate output

```bash
ls /tmp/seed_test
# expected: curriculum.md  full_map.md  living_doc.md  style_contract.md  world_laws.md  config.toml

grep "=== LIVING DOCUMENT ===" /tmp/seed_test/living_doc.md
grep "--- CURRENT STATE ---" /tmp/seed_test/living_doc.md
grep "--- NOTES FOR AI ---" /tmp/seed_test/living_doc.md
```

All 9 sacred living doc headers must be present.

### Pass 3 — Dry-run pipeline

From `output_dir`, run the novel pipeline dry-run:

```bash
cd /tmp/seed_test
novel-pipeline --config config.toml --dry-run
```

Must load all 4 static docs without error.

Commit.

---

## Phase Log

| Phase | Status | Notes |
| --- | --- | --- |
| 01 — Scaffold | pending | |
| 02 — Template loading | pending | |
| 03 — Pass 1 | pending | |
| 04 — Q&A | pending | |
| 05 — Pass 2 | pending | |
| 06 — Verification | pending | |
