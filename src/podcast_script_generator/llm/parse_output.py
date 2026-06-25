"""Section 5: parse_output — split LLM response into (filename, content) tuples."""

import re

# Match a line that begins with `### FILE: ` followed by a filename.
# Anchored to line start (MULTILINE); captures everything after the prefix on that line.
_FILE_HEADER = re.compile(r"^### FILE:\s*(.+?)\s*$", re.MULTILINE)


def parse_output(response_text: str) -> list[tuple[str, str]]:
    """Parse the LLM response into a list of (filename, content) tuples.

    Files are separated by `### FILE: filename.ext` headers, one per line.
    Content for a file runs from just after its header to the next header (or EOF),
    with leading/trailing whitespace stripped.

    If no headers are present at all, the whole response is returned as a single
    ("output.txt", <stripped response>) tuple.

    Raises ValueError if no files can be produced (e.g., headers present but the
    stripped response is otherwise empty in a way that yields nothing).
    """
    matches = list(_FILE_HEADER.finditer(response_text))

    if not matches:
        stripped = response_text.strip()
        if not stripped:
            snippet = response_text[:200]
            raise ValueError(f"No files found in response. Snippet: {snippet!r}")
        return [("output.txt", stripped)]

    files: list[tuple[str, str]] = []
    for i, m in enumerate(matches):
        filename = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(response_text)
        content = response_text[start:end].strip()
        files.append((filename, content))

    if not files:
        snippet = response_text[:200]
        raise ValueError(f"No files found in response. Snippet: {snippet!r}")

    return files
