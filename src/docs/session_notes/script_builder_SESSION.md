# SESSION — PDF-to-LLM CLI Builder
## One Function At A Time

Copy one SECTION, paste it into chat, get the code back. Do not build the next section until the current one is committed and tested.

---

## Global Context (Paste Once Per New Chat)

We are building a Python CLI with these contracts:

| Function | Input | Output |
|----------|-------|--------|
| `parse_args` | `sys.argv` | `(pdf_path, prompt_path, output_dir)` |
| `extract_pdf` | `pdf_path: str` | `pdf_text: str` |
| `read_prompt` | `prompt_path: str` | `prompt_text: str` |
| `call_api` | `pdf_text, prompt_text` | `response_text: str` |
| `parse_output` | `response_text: str` | `[(filename, content), ...]` |
| `save_output` | `files, output_dir` | side effect: files written |

**Stack:** Python 3.10+, `pymupdf` (fitz), `urllib.request` (stdlib HTTP). No frameworks, no vendor SDKs.
**Philosophy:** Fail loud. No silent swallowing.

---

## Mandatory Gate — Answer Before Coding

For every section, the AI must answer these 3 questions and **WAIT for human approval**:

1. **What could break in this function given the contract and expected inputs?**
2. **If we change this later, what downstream functions break?**
3. **Is this minimal viable, or over-engineered?**

After answering, stop with: **"WAITING FOR HUMAN APPROVAL TO PROCEED."**

---

## SECTION 1 — parse_args

Build a Python function called `parse_args`.

**Signature:**
```python
def parse_args() -> tuple[str, str, str]:
```

**What it does:** Reads three positional CLI arguments and validates they exist.

**Input:** `sys.argv` — three positional arguments:
1. `pdf_path` — must exist as a file
2. `prompt_path` — must exist as a file
3. `output_dir` — directory path (create if missing)

**Output:** `(pdf_path: str, prompt_path: str, output_dir: str)`

**Requirements:**
- Use `argparse` or `sys.argv` slicing
- If fewer than 3 arguments, print `Usage: script.py <pdf_path> <prompt_path> <output_dir>` and exit non-zero
- Validate `pdf_path` and `prompt_path` exist; raise `FileNotFoundError` with the path if not
- Validate `output_dir`: create with `os.makedirs(..., exist_ok=True)` if it does not exist
- Return the three strings

**Return only the function and any imports it needs. No main block, no tests.**

**WAITING FOR HUMAN APPROVAL TO PROCEED.**

---

## SECTION 2 — extract_pdf

Build a Python function called `extract_pdf`.

**Signature:**
```python
def extract_pdf(pdf_path: str) -> str:
```

**What it does:** Takes a PDF path and returns all text as a single string.

**Input:** `pdf_path` — readable PDF file

**Output:** `pdf_text: str` — all text, pages joined with `

`

**Requirements:**
- Use `pymupdf` (import as `fitz`)
- Iterate pages, extract text, join with `

`
- If file cannot be opened or has no extractable text, raise `ValueError` with the path
- Close the document properly

**Return only the function and any imports it needs. No main block, no tests.**

**WAITING FOR HUMAN APPROVAL TO PROCEED.**

---

## SECTION 3 — read_prompt

Build a Python function called `read_prompt`.

**Signature:**
```python
def read_prompt(prompt_path: str) -> str:
```

**What it does:** Reads a `.txt` file and returns its contents.

**Input:** `prompt_path` — readable text file

**Output:** `prompt_text: str` — full contents, trailing whitespace stripped only

**Requirements:**
- Open with `utf-8` encoding
- Strip trailing whitespace only (preserve internal formatting)
- If file cannot be opened, raise `ValueError` with the path
- If file is empty, raise `ValueError`

**Return only the function and any imports it needs. No main block, no tests.**

**WAITING FOR HUMAN APPROVAL TO PROCEED.**

---

## SECTION 4 — call_api

Build a Python function called `call_api`.

**Signature:**
```python
def call_api(pdf_text: str, prompt_text: str) -> str:
```

**What it does:** Sends PDF text + prompt to OpenRouter and returns the response string.

**Input:**
- `pdf_text` — extracted PDF content
- `prompt_text` — instructions for the model

**Output:** `response_text: str` — raw model reply

**Message format:**
Send a single user message structured as:
```
{prompt_text}

---

{pdf_text}
```

**Requirements:**

- Use `urllib.request` (stdlib only — no vendor SDKs)
- Read API key from environment variable `OPENROUTER_API_KEY` — do not hardcode
- POST to `https://openrouter.ai/api/v1/chat/completions`
- Set `max_tokens` to `4096`
- Return only `data["choices"][0]["message"]["content"]`
- If the API call fails, let the exception propagate — do not swallow errors

**Return only the function and any imports it needs. No main block, no tests.**

**WAITING FOR HUMAN APPROVAL TO PROCEED.**

---

## SECTION 5 — parse_output

Build a Python function called `parse_output`.

**Signature:**
```python
def parse_output(response_text: str) -> list[tuple[str, str]]:
```

**What it does:** Parses the LLM response into `(filename, content)` tuples.

**Input:** `response_text` — raw string from the LLM

**Output:** `[(filename, content), ...]` — list of file pairs

**Format the LLM uses:**

Multiple files are separated by this exact header:
```
### FILE: filename.ext
```
Everything after that line until the next `### FILE:` header (or end of string) is that file's content.

If **no** `### FILE:` headers exist at all, treat the entire response as a single file named `output.txt`.

**Example input:**
```
### FILE: summary.txt
This is the summary.

### FILE: keywords.txt
keyword1
keyword2
```

**Example output:**
```python
[("summary.txt", "This is the summary."), ("keywords.txt", "keyword1
keyword2")]
```

**Requirements:**
- Strip leading and trailing whitespace from each file's content
- Filenames come from the header exactly as written after `### FILE: `
- Use only the standard library — no third-party packages
- If no files are found (not even a single `output.txt` fallback), raise `ValueError` with a snippet of the response

**Return only the function and any imports it needs. No main block, no tests.**

**WAITING FOR HUMAN APPROVAL TO PROCEED.**

---

## SECTION 6 — save_output

Build a Python function called `save_output`.

**Signature:**
```python
def save_output(files: list[tuple[str, str]], output_dir: str) -> None:
```

**What it does:** Writes `(filename, content)` pairs to disk.

**Input:**
- `files` — list of `(filename, content)` tuples
- `output_dir` — directory path

**Output:** Nothing. Side effect: files written.

**Requirements:**
- Create `output_dir` with `os.makedirs(..., exist_ok=True)` if missing
- For each `(filename, content)`, write to `os.path.join(output_dir, filename)` in `utf-8`
- **Path traversal guard:** If `filename` contains `..` or is an absolute path, raise `ValueError`
- Overwrite existing files by default
- Print: `Wrote N files to {output_dir}`

**Return only the function and any imports it needs. No main block, no tests.**

**WAITING FOR HUMAN APPROVAL TO PROCEED.**

---

## SECTION 7 — main & wiring

**What exists:** All 6 functions are built and individually tested.

Build a `main.py` file that wires the pipeline:

```python
pdf_path, prompt_path, output_dir = parse_args()
pdf_text = extract_pdf(pdf_path)
prompt_text = read_prompt(prompt_path)
response_text = call_api(pdf_text, prompt_text)
files = parse_output(response_text)
save_output(files, output_dir)
```

**Requirements:**
- Wrap in `try/except` to catch expected errors and print clean messages to `stderr`
- Add `if __name__ == "__main__": main()`
- No new logic. Just wiring and error presentation.

**WAITING FOR HUMAN APPROVAL TO PROCEED.**

---

## SECTION 8 — requirements.txt

```
pymupdf>=1.24.0
```

No analysis needed. Just create the file.

---

## Build Checklist

- [ ] Section 1 committed and tested
- [ ] Section 2 committed and tested
- [ ] Section 3 committed and tested
- [ ] Section 4 committed and tested
- [ ] Section 5 committed and tested
- [ ] Section 6 committed and tested
- [ ] Section 7 committed and end-to-end tested
- [ ] Section 8 committed
- [ ] README with usage example (optional)

**End of SESSION.md**
