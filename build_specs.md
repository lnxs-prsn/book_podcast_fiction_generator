# Build Specs — Missing Vision Components

Phases are built one at a time. Each phase is self-contained. Passes are commit-level units of work inside a phase.

---

## Phase 1 — Fix broken integration path

The `run_chapter.py` integration script imports from `src/podcast/llm/` but the actual directory is `src/podcast_script_generator/llm/`. The pipeline cannot run LLM mode end-to-end until this is resolved.

### Pass 1 — Correct the import path in run_chapter.py
- Fix the `sys.path.insert` call in `run_chapter.py` `run_llm()` from `src/podcast/llm/` to `src/podcast_script_generator/llm/`
- Smoke-test: run `python run_chapter.py data/chapters/01_chapter_... --llm --skip-audio` and confirm no ImportError

---

## Phase 2 — Podcast mode selection architecture

Right now the LLM script generator is hardwired to one prompt file and one style (2-person HOST/EXPERT). The vision requires 4 selectable modes. This phase builds the mode-switching plumbing without yet writing the new mode prompts.

### Pass 1 — Split prompt into per-mode files
- Create `src/podcast_script_generator/llm/prompts/` directory
- Move existing `prompt.txt` to `prompts/mode_2person.txt`
- Add stub files for the three other modes: `mode_4person.txt`, `mode_code.txt`, `mode_realworld.txt`, `mode_fiction_meta.txt` (placeholder text, not final prompts)

### Pass 2 — Add --mode flag to the script generator
- Update `src/podcast_script_generator/llm/parse_args.py` to accept a `--mode` argument with choices: `2person` (default), `4person`, `code`, `realworld`, `fiction_meta`
- Update `src/podcast_script_generator/llm/read_prompt.py` to resolve the prompt file based on the chosen mode
- No change to `main.py` logic yet — just the arg parsing and file resolution

### Pass 3 — Wire mode through run_chapter.py
- Add `--mode` flag to `run_chapter.py`
- Pass it through to the LLM generator call
- Default remains `2person` so existing behaviour is unchanged

---

## Phase 3 — 4-person podcast format

The TTS layer already supports 4 speakers. This phase writes the prompt and verifies the full 4-speaker path end-to-end.

### Pass 1 — Write the 4-person prompt
- Write `prompts/mode_4person.txt`
- 4 named voices: HOST (listener proxy), EXPERT (deep authority), CRITIC (challenges assumptions), NEWCOMER (asks naive questions that expose gaps)
- Output format must use `Speaker 0:` / `Speaker 1:` / `Speaker 2:` / `Speaker 3:` prefixes so TTS picks them up without modification
- Target length same as 2-person: ~3,900–4,200 words

### Pass 2 — Update _to_speaker_format() for 4-person output
- Extend the regex map in `run_chapter.py` `_to_speaker_format()` to handle CRITIC: → Speaker 2: and NEWCOMER: → Speaker 3:
- Verify TTS CLI receives all 4 speaker voices when mode is `4person`
- Smoke-test: run on one chapter with `--mode 4person`, confirm MP3 contains 4 distinct voices

---

## Phase 4 — Code semantics/reasoning podcast mode

A mode designed for chapters with code examples. The podcast does not teach syntax — it teaches why the code was written the way it was and what it accomplishes conceptually.

### Pass 1 — Write the code semantics/reasoning prompt
- Write `prompts/mode_code.txt`
- For every code snippet encountered: two beats — Semantics (what the code does at a human level), then Reasoning (why it was written that way, what alternative was rejected and why)
- HOST surfaces "what would go wrong if you did it differently" questions
- Explicitly instruct the model: do not dictate or spell out code; describe intent and consequence
- 2-person format (reuse HOST/EXPERT voices, Speaker 0/1 output)

### Pass 2 — Test on a code-heavy chapter
- Run the mode against a chapter known to have code examples (e.g. Chapter 5 or 6 from the NLP book)
- Verify the output avoids code dictation and focuses on semantics/reasoning
- Adjust prompt if the model drifts back to reading code aloud

---

## Phase 5 — Real-world context podcast mode

A mode where the chapter content is discussed in relation to a current event the user provides (e.g. a recent zero-day vulnerability, a product launch, a news story).

### Pass 1 — Design the context injection interface
- Decide: context is passed as a plain text string via `--context "..."` or as a path to a text file via `--context-file path.txt`
- Decision: support both — `--context` for short inline text, `--context-file` for longer documents
- Document the interface in `src/podcast_script_generator/llm/prompts/mode_realworld.txt` header comments

### Pass 2 — Write the real-world context prompt
- Write `prompts/mode_realworld.txt` with a `{CURRENT_EVENT}` placeholder that gets substituted at runtime
- Prompt instructs the model to open with the real-world event, then use the chapter content as the explanatory lens
- The event is the hook; the book content is the answer
- 2-person format, Speaker 0/1 output

### Pass 3 — Add --context / --context-file to CLI and wire substitution
- Add `--context` and `--context-file` flags to `run_chapter.py` and `parse_args.py`
- In `read_prompt.py`, after loading `mode_realworld.txt`, substitute `{CURRENT_EVENT}` with the provided context string
- If mode is `realworld` and neither flag is provided, exit with a clear error message

---

## Phase 6 — Fiction meta-commentary podcast mode

A mode where the podcast discusses how the technical book content was adapted into a fictional story — what translated well, what was lost, where the fiction diverged from the source material.

### Pass 1 — Design the fiction input interface
- This mode needs two inputs: the chapter PDF (source material) and the corresponding fiction chapter(s)
- Add `--fiction-dir` flag to `run_chapter.py` — a path to the fiction pipeline output directory
- The runner finds the fiction chapter(s) whose name matches the source chapter stem and injects that text alongside the PDF content

### Pass 2 — Write the fiction meta-commentary prompt
- Write `prompts/mode_fiction_meta.txt`
- Two placeholders: `{TECHNICAL_CONTENT}` (from the PDF) and `{FICTION_CONTENT}` (from the fiction output)
- Prompt: HOST and EXPERT reflect on the translation — what concepts survived intact, what got abstracted into metaphor, where the fiction had to simplify or distort
- Useful as a capstone episode for each chapter
- 2-person format, Speaker 0/1 output

### Pass 3 — Wire fiction content injection in run_chapter.py
- When `--mode fiction_meta` and `--fiction-dir` are provided, load the matching fiction chapter text
- Substitute both placeholders before sending to the LLM
- If `--fiction-dir` is missing for this mode, exit with a clear error

---

## Phase 7 — Batch whole-book runner

A single entry point that takes the full `data/chapters/` directory and produces a script + MP3 for every chapter without manual intervention.

### Pass 1 — Build the basic batch runner
- Create `src/run_book.py`
- Reads all PDFs from `data/chapters/` (sorted by filename prefix number)
- Calls `run_chapter.py` logic for each chapter (import and call directly, not subprocess)
- Accepts the same `--llm`, `--skip-audio`, `--mode` flags and passes them through to each chapter run
- Prints a one-line status per chapter as it completes: `[ok]`, `[skip]`, or `[fail]`

### Pass 2 — Add skip-existing / resume logic
- Before processing a chapter, check if the output script already exists in `data/output/scripts/`
- If it exists (and `--force` is not set), print `[skip]` and move on
- Add `--force` flag to reprocess chapters that already have output

### Pass 3 — Progress reporting and error summary
- Track which chapters succeeded, were skipped, and failed
- At the end of the run, print a summary table: total / succeeded / skipped / failed
- If any chapters failed, list them by name with their error message
- Write the summary to `data/output/run_summary.txt` alongside the audio/script output
