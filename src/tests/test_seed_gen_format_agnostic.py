"""Format-agnostic tests for fiction/seed_gen/cli.py."""

import ast
import sys
from pathlib import Path
from unittest import mock

import pytest

SRC_DIR = Path(__file__).parent.parent


def test_seed_gen_uses_registry_for_epub(tmp_path):
    """get_extractor is called with an .epub path."""
    import fiction.seed_gen.cli as sg

    fake_text = "fake epub text"
    mock_extractor = mock.MagicMock(return_value=fake_text)

    with mock.patch.object(sg, "get_extractor", return_value=mock_extractor), \
         mock.patch.object(sg, "create_client", return_value=mock.MagicMock()), \
         mock.patch.object(sg, "load_templates", return_value={f: "" for f in [
             "world_laws.md", "curriculum.md", "style_contract.md", "full_map.md", "living_doc.md",
         ]}), \
         mock.patch.object(sg, "build_pass1_prompt", return_value="pass1"), \
         mock.patch.object(sg, "call_api", return_value=(
             "### Genre 1: Action\n## Extracted Concepts\n- A\n- B\n- C\n- D\n- E"
         )), \
         mock.patch.object(sg, "collect_user_plan", return_value={
             "genre_index": 1, "genre_text": "Action", "protagonist_name": "X",
             "protagonist_background": "Y", "concept_list": ["A","B","C","D","E"],
             "climax_concept": "A", "additions": "",
         }), \
         mock.patch.object(sg, "build_pass2_prompt", return_value="pass2"), \
         mock.patch.object(sg, "parse_output", return_value={}), \
         mock.patch.object(sg, "save_output"), \
         mock.patch.object(sg, "write_config_toml"), \
         mock.patch("sys.argv", ["seed_gen", "fake.epub", str(tmp_path)]):
        try:
            sg.main()
        except SystemExit:
            pass
        sg.get_extractor.assert_called_once_with("fake.epub")
        mock_extractor.assert_called_once_with("fake.epub")


def test_seed_gen_uses_registry_for_pdf(tmp_path):
    """get_extractor is called with a .pdf path."""
    import fiction.seed_gen.cli as sg

    fake_text = "fake pdf text"
    mock_extractor = mock.MagicMock(return_value=fake_text)

    with mock.patch.object(sg, "get_extractor", return_value=mock_extractor), \
         mock.patch.object(sg, "create_client", return_value=mock.MagicMock()), \
         mock.patch.object(sg, "load_templates", return_value={f: "" for f in [
             "world_laws.md", "curriculum.md", "style_contract.md", "full_map.md", "living_doc.md",
         ]}), \
         mock.patch.object(sg, "build_pass1_prompt", return_value="pass1"), \
         mock.patch.object(sg, "call_api", return_value=(
             "### Genre 1: Action\n## Extracted Concepts\n- A\n- B\n- C\n- D\n- E"
         )), \
         mock.patch.object(sg, "collect_user_plan", return_value={
             "genre_index": 1, "genre_text": "Action", "protagonist_name": "X",
             "protagonist_background": "Y", "concept_list": ["A","B","C","D","E"],
             "climax_concept": "A", "additions": "",
         }), \
         mock.patch.object(sg, "build_pass2_prompt", return_value="pass2"), \
         mock.patch.object(sg, "parse_output", return_value={}), \
         mock.patch.object(sg, "save_output"), \
         mock.patch.object(sg, "write_config_toml"), \
         mock.patch("sys.argv", ["seed_gen", "fake.pdf", str(tmp_path)]):
        try:
            sg.main()
        except SystemExit:
            pass
        sg.get_extractor.assert_called_once_with("fake.pdf")


def test_seed_gen_source_pdf_argument_unchanged():
    """source_pdf positional argument still present in cli.py."""
    source = (SRC_DIR / "fiction" / "seed_gen" / "cli.py").read_text()
    tree = ast.parse(source)
    add_argument_calls = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and n.func.attr == "add_argument"
    ]
    positional_names = []
    for call in add_argument_calls:
        for arg in call.args:
            if isinstance(arg, ast.Constant) and not str(arg.value).startswith("-"):
                positional_names.append(arg.value)
    assert "source_pdf" in positional_names


def test_seed_gen_pdf_char_limit_unchanged():
    """PDF_CHAR_LIMIT constant still defined in cli.py."""
    source = (SRC_DIR / "fiction" / "seed_gen" / "cli.py").read_text()
    assert "PDF_CHAR_LIMIT" in source


def test_seed_gen_unsupported_format_propagates(tmp_path):
    """UnsupportedFormatError propagates for unregistered extension."""
    from format_adapters.registry import UnsupportedFormatError
    import fiction.seed_gen.cli as sg

    with mock.patch.object(sg, "load_templates", return_value={f: "" for f in [
             "world_laws.md", "curriculum.md", "style_contract.md", "full_map.md", "living_doc.md",
         ]}), \
         mock.patch.object(sg, "create_client", return_value=mock.MagicMock()), \
         mock.patch("sys.argv", ["seed_gen", "fake.docx", str(tmp_path)]):
        with pytest.raises((SystemExit, UnsupportedFormatError)):
            sg.main()
