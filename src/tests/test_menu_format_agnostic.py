"""Tests for menu.ask_pdf — format-agnostic acceptance/rejection via registry."""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure menu.py can be imported with its sys.path manipulation
_PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))


def _get_menu():
    import importlib
    import importlib.util
    spec = importlib.util.spec_from_file_location("menu", str(_PROJECT_ROOT / "menu.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_ask_pdf_accepts_registered_epub():
    menu = _get_menu()
    with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
        epub_path = f.name
    try:
        with patch.object(menu, "registered_extensions", return_value=[".epub", ".pdf"]), \
             patch("builtins.input", return_value=epub_path):
            result = menu.ask_pdf("Source book")
        assert result == Path(epub_path).resolve()
    finally:
        os.unlink(epub_path)


def test_ask_pdf_accepts_registered_pdf():
    menu = _get_menu()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        pdf_path = f.name
    try:
        with patch.object(menu, "registered_extensions", return_value=[".epub", ".pdf"]), \
             patch("builtins.input", return_value=pdf_path):
            result = menu.ask_pdf("Source book")
        assert result == Path(pdf_path).resolve()
    finally:
        os.unlink(pdf_path)


def test_ask_pdf_rejects_unregistered_extension():
    menu = _get_menu()
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        txt_path = f.name
    try:
        with patch.object(menu, "registered_extensions", return_value=[".epub", ".pdf"]), \
             patch("builtins.input", return_value=txt_path):
            result = menu.ask_pdf("Source book")
        assert result is None
    finally:
        os.unlink(txt_path)
