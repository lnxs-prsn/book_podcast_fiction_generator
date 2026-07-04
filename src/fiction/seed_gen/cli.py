import argparse
import logging
import re
import sys
from pathlib import Path

from llm.env import resolve_from_env
from llm.exceptions import LLMConfigError
from llm.factory import create_client

from format_adapters import get_extractor
from podcast_script_generator.llm.call_api import call_api
from podcast_script_generator.llm.exceptions import ScriptGenerationError
from podcast_script_generator.llm.parse_output import parse_output
from podcast_script_generator.llm.save_output import save_output

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates"
PROMPTS_DIR = Path(__file__).parent / "prompts"
PDF_CHAR_LIMIT = 120_000

EXPECTED_TEMPLATES = [
    "world_laws.md", "curriculum.md", "style_contract.md",
    "full_map.md", "living_doc.md",
]


def load_templates() -> dict[str, str]:
    missing = [f for f in EXPECTED_TEMPLATES if not (TEMPLATES_DIR / f).exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing bundled templates in {TEMPLATES_DIR}: {missing}\n"
            f"Copy from docs/fiction/directive_templates/"
        )
    return {f: (TEMPLATES_DIR / f).read_text(encoding="utf-8") for f in EXPECTED_TEMPLATES}


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


def _format_templates(templates: dict[str, str]) -> str:
    return "\n\n".join(
        f"### {name}\n{content}" for name, content in templates.items()
    )


def build_pass1_prompt(templates: dict[str, str]) -> str:
    prompt = (PROMPTS_DIR / "pass1_genres.txt").read_text(encoding="utf-8")
    return prompt.replace("{TEMPLATES}", _format_templates(templates))


def validate_pass1_response(response: str) -> None:
    # Accept "Genre N:", "**Genre N:**", "### Genre N:", "### **Genre N:**" etc.
    if not re.search(r"(?i)^[#*\s]*genre\s+\d+\s*[:\*]", response, re.MULTILINE):
        print("\n--- Raw LLM response ---")
        print(response)
        print("------------------------")
        raise ValueError(
            "Pass 1 returned no genre proposals. "
            "Raw response printed above. Check your API key, model, and PDF content."
        )


def _prompt_field(prompt: str, validator, max_retries: int = 3) -> str:
    for _ in range(max_retries):
        value = input(prompt).strip()
        result = validator(value)
        if result is not None:
            return result
    print("Too many invalid attempts. Aborting.", file=sys.stderr)
    sys.exit(1)


def _parse_concept_list(pass1_response: str) -> list[str]:
    match = re.search(r"## Extracted Concepts[^\n]*\n(.*?)(?:\n##|\Z)", pass1_response, re.DOTALL)
    if not match:
        return []
    lines = [l.strip().lstrip("-•* ") for l in match.group(1).strip().splitlines()]
    return [l for l in lines if l]


def collect_user_plan(pass1_response: str) -> dict:
    concept_list = _parse_concept_list(pass1_response)

    # Count genres in pass1 response — handle "Genre N:" and "### Genre N:" variants
    genre_lines = re.findall(r"(?im)^[#*\s]*genre\s+(\d+)\s*[:\*]", pass1_response)
    n_genres = max((int(x) for x in genre_lines), default=5)

    # --- Genre choice ---
    genre_index = None
    genre_text = ""
    print(f"\nGenre proposals above. Enter 1–{n_genres} to select, or 'custom' for your own genre.")
    for attempt in range(3):
        raw = input("Genre choice: ").strip()
        if raw.lower() == "custom":
            genre_index = 0
            genre_text = input("Enter your custom genre description: ").strip()
            if not genre_text:
                genre_text = "custom"
            break
        try:
            idx = int(raw)
            if 1 <= idx <= n_genres:
                genre_index = idx
                # Extract the matching genre block — handle both "Genre N:" and "### Genre N:" variants
                pattern = rf"(?im)^[#*\s]*genre\s+{idx}\s*[:\*].*?(?=^[#*\s]*genre\s+\d+\s*[:\*]|\Z)"
                m = re.search(pattern, pass1_response, re.DOTALL | re.MULTILINE)
                genre_text = m.group(0).strip() if m else f"Genre {idx}"
                break
        except ValueError:
            pass
        print(f"Enter a number between 1 and {n_genres}, or 'custom'.")
    else:
        print("Too many invalid attempts. Aborting.", file=sys.stderr)
        sys.exit(1)

    # --- Protagonist name ---
    protagonist_name = _prompt_field(
        "Protagonist name: ",
        lambda v: v if v else None,
    )

    # --- Protagonist background ---
    protagonist_background = _prompt_field(
        "Protagonist background: ",
        lambda v: v if v else None,
    )

    # --- Concept list ---
    if concept_list:
        print("\nExtracted concepts:")
        for i, c in enumerate(concept_list, 1):
            print(f"  {i}. {c}")
        raw = input("\nPress Enter to keep this list, or type a comma-separated replacement: ").strip()
        if raw:
            edited = [x.strip() for x in raw.split(",") if x.strip()]
            for attempt in range(3):
                if len(edited) >= 5:
                    concept_list = edited
                    break
                print("Need at least 5 concepts.")
                raw = input("Enter comma-separated concepts (min 5): ").strip()
                edited = [x.strip() for x in raw.split(",") if x.strip()]
            else:
                if len(edited) < 5:
                    print("Too many invalid attempts. Aborting.", file=sys.stderr)
                    sys.exit(1)
    else:
        print("No concepts extracted from Pass 1. Enter concepts manually.")
        for attempt in range(3):
            raw = input("Enter comma-separated concepts (min 5): ").strip()
            edited = [x.strip() for x in raw.split(",") if x.strip()]
            if len(edited) >= 5:
                concept_list = edited
                break
            print("Need at least 5 concepts.")
        else:
            print("Too many invalid attempts. Aborting.", file=sys.stderr)
            sys.exit(1)

    # --- Climax concept ---
    concept_lower = [c.lower() for c in concept_list]
    print("\nConcepts:", ", ".join(concept_list))
    climax_concept = _prompt_field(
        "Climax concept (must match one of the above): ",
        lambda v: v if v.lower() in concept_lower else None,
    )

    # --- Additions ---
    additions = input("Any additional notes or requests? (press Enter to skip): ").strip()

    return {
        "genre_index": genre_index,
        "genre_text": genre_text,
        "protagonist_name": protagonist_name,
        "protagonist_background": protagonist_background,
        "concept_list": concept_list,
        "climax_concept": climax_concept,
        "additions": additions,
    }


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


def write_config_toml(output_dir: Path) -> None:
    (output_dir / "config.toml").write_text(CONFIG_TOML, encoding="utf-8")


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


def main() -> None:
    try:
        args = parse_args()
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=str(output_dir / "seed_gen.log"),
            level=logging.DEBUG,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )

        templates = load_templates()
        book_text = truncate_pdf_text(get_extractor(args.source_pdf)(args.source_pdf))
        pass1_prompt = build_pass1_prompt(templates)

        try:
            client = create_client(**resolve_from_env())
        except LLMConfigError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        print("Running Pass 1: genre evaluation...")
        pass1_response = call_api(pdf_text=book_text, prompt_text=pass1_prompt, llm=client, timeout=120.0)
        validate_pass1_response(pass1_response)
        print(pass1_response)

        user_plan = collect_user_plan(pass1_response)

        print("\nRunning Pass 2: generating files...")
        pass2_prompt = build_pass2_prompt(user_plan, pass1_response, templates)
        pass2_response = call_api(pdf_text="", prompt_text=pass2_prompt, llm=client, timeout=120.0)
        files = parse_output(pass2_response)
        save_output(files, str(output_dir))
        write_config_toml(output_dir)
        print(f"\nSeed files written to {output_dir}.")
        print(f"Review and edit them, then run: PYTHONPATH=src python src/cli/fiction.py --config {output_dir}/config.toml")

    except (ValueError, ScriptGenerationError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Unexpected error: {e}\n")
        logger.exception("Unhandled exception in seed_gen")
        sys.exit(1)


if __name__ == "__main__":
    main()
