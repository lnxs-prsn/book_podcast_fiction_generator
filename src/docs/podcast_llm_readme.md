# pdf2llm — PDF-to-LLM CLI

Send a PDF + a prompt to an LLM via OpenRouter, get back one or more files written to disk.

## Install

```bash
pip install -r requirements.txt
export OPENROUTER_API_KEY=sk-or-...
```

Requires Python 3.10+.

## Usage

```bash
python main.py <pdf_path> <prompt_path> <output_dir>
```

Example:

```bash
python main.py paper.pdf prompt.txt ./out
```

Where `prompt.txt` might contain:

```
Read this paper and produce two files.

### FILE: summary.txt
A 3-paragraph summary.

### FILE: keywords.txt
One keyword per line, max 10.
```

The script will write `summary.txt` and `keywords.txt` into `./out/`.

## Response format

The model is expected to emit files separated by headers of the form:

```
### FILE: filename.ext
<content>

### FILE: other.ext
<content>
```

If no `### FILE:` headers are present, the entire response is saved as `output.txt`.

## Module map

| File             | Responsibility                                         |
|------------------|--------------------------------------------------------|
| `parse_args.py`  | CLI args → `(pdf_path, prompt_path, output_dir)`       |
| `extract_pdf.py` | PDF → text (via `pymupdf`)                             |
| `read_prompt.py` | Read prompt `.txt` file                                |
| `call_api.py`    | Send to OpenRouter, return raw text                    |
| `parse_output.py`| Split response into `(filename, content)` tuples       |
| `save_output.py` | Write tuples to disk (with path-traversal guard)       |
| `main.py`        | Wire the pipeline, handle errors                       |
| `test_all.py`    | Unit + end-to-end tests (mocked API, no key needed)    |

## Tests

```bash
python test_all.py
```

Runs 38 checks across all six functions plus a full pipeline run with the API
call mocked, so no API key is needed for tests.

## Error behavior

Fail loud, no silent swallowing:

- Wrong arg count → prints `Usage: ...` to stderr, exits 1.
- Missing PDF/prompt → `FileNotFoundError` with the path.
- Unreadable PDF / no text → `ValueError` with the path.
- Empty prompt → `ValueError` with the path.
- Missing `OPENROUTER_API_KEY` → `KeyError` in `main.py`'s handler, exits 1.
- Unsafe filename from the model (`..` or absolute path) → `ValueError`.
- Any other exception → printed with its type, exit 1.
