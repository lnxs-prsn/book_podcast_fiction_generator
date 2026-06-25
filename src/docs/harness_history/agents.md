# AGENTS.md — Multi-Angle Learning Engine

## Identity
A pipeline that transforms books into multiple learning formats: podcast scripts, xianxia-fiction retellings, and animation storyboards. All formats are generated in parallel from sliced chapter text. No format is input for another.

## Stack
- Python 3.11+ for all stages
- File-based passing between stages (JSON, PDF, Markdown)
- Local processing preferred; cloud APIs allowed only with explicit human confirmation per call

## Where Things Live
- Stage scripts live flat in `src/` or at repo root until complexity justifies folders
- `data/raw/` — source books
- `data/processed/chapters/` — chapter slices (PDFs)
- `data/processed/extracted/` — chapter text extracts (Markdown/JSON)
- `data/output/podcast/` — podcast scripts
- `data/output/xianxia/` — xianxia fiction retellings
- `data/output/animation/` — animation storyboards

## Architecture Rules
- Stages are scripts, not services. Input files → output files.
- Stages never import each other. Communication is through the filesystem only.
- The pipeline forks after slicing. Every generator stage reads from `data/processed/extracted/` or `data/processed/chapters/`, never from another generator's output.
- All paths are passed as arguments or read from a JSON config. No hardcoded paths.
- Keep code flat and linear. No classes or abstraction layers until the second use case demands them.

## Execution Rule
- Before writing files, print exactly what will be written (filename, count, destination) and wait for user confirmation.
- Cloud API calls require a second confirmation: print estimated cost and token count, then wait for explicit `[y/n]` input before executing the call.

## Commands
- Run a stage: `python &lt;script&gt;.py`
- Validate: `python -c "import os; assert os.path.getsize('output.pdf') &gt; 0"`

## Guardrails
- Never commit processed data or outputs to git.
- Never use Jupyter notebooks for pipeline code.
- Never add packaging, linting, or CI configuration unless explicitly requested.
- Never introduce a new file format without documenting it here.
- Never hardcode API keys. Read from environment variables only.
- Never design a stage that consumes another generator's output. All generators are siblings, not ancestors.