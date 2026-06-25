# SESSION.md

# SESSION — Build Podcast Script Generator

## Project
Multi-angle learning engine. Stage 2: transform a single chapter PDF into a structured podcast script via cloud API.

## Active Task
Build a Python script that takes one chapter PDF, extracts its text, sends it to a cloud LLM API with a podcast-generation prompt, and writes the response as a markdown script.

## Stack
Python 3.11+. Use `pypdf` for text extraction. Use `requests` for API calls (stdlib `urllib` if you prefer zero dependencies). Output is Markdown.

## Rules
- One Python file. No classes, no tests, no CLI framework.
- Input: a single chapter PDF file path.
- Output: a `.md` file in `data/output/podcast/` named after the input (e.g., `01_Chapter_Title_podcast.md`).
- API Configuration:
  - Read API key from environment variable only (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`). If missing, raise `EnvironmentError` immediately with clear instructions.
  - Hardcode `MAX_TOKENS = 4000` per call. No parameter override.
  - Hardcode a single-shot prompt that instructs the model to produce HOST/GUEST dialogue covering the full chapter text.
- Processing:
  1. Extract all text from the PDF using `pypdf`.
  2. If extracted text is empty, raise `ValueError` with the filename.
  3. Estimate token count using a simple heuristic: `len(text) // 4` characters per token. If estimate exceeds `MAX_TOKENS`, raise `ValueError` telling the user the text is too long and suggesting they split the chapter.
  4. Print a cost preview to stdout: `API call estimated cost: $X.XXX for ~N tokens. Continue? [y/n]`
  5. Read one line from stdin. If the response is not exactly `y` or `Y`, print `Aborted.` and exit with code 0.
  6. Make the API call.
  7. Write the API response directly to the output markdown file.
- Before writing the file, print: `Will write podcast script: [filename] to [path]`. Then call `input("Press Enter to confirm file write...")` and only proceed if the user presses Enter.

## Never Do
- Do not batch process multiple PDFs. One invocation, one PDF, one API call.
- Do not implement retry logic, exponential backoff, or rate limiting. If the API fails, let the exception propagate.
- Do not cache API responses or log token usage to disk.
- Do not write docstrings beyond a single one-line description at the top.
- Do not create `requirements.txt`, `setup.py`, or packaging files.
- Do not allow the user to override `MAX_TOKENS` via CLI argument or config file.

## Done When
A single `.py` file exists that, given a chapter PDF path, extracts text, enforces the token cap, shows cost preview, requires two human confirmations (one for API call, one for file write), makes exactly one API call, and writes one markdown podcast script.