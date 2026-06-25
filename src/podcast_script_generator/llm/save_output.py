"""Section 6: save_output — write (filename, content) pairs to output_dir."""

import logging
import os

logger = logging.getLogger(__name__)


def save_output(files: list[tuple[str, str]], output_dir: str) -> None:
    """Write each (filename, content) pair to output_dir as a UTF-8 file.

    - Creates output_dir if it does not exist.
    - Overwrites existing files.
    - Path-traversal guard: filenames containing '..' or that are absolute paths
      raise ValueError.
    """
    os.makedirs(output_dir, exist_ok=True)

    for filename, content in files:
        # Reject anything that could escape output_dir or target an arbitrary location.
        if ".." in filename or os.path.isabs(filename):
            raise ValueError(f"Unsafe filename: {filename}")

        path = os.path.join(output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    logger.debug(f"Wrote {len(files)} files to {output_dir}")
