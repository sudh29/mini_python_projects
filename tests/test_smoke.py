"""Smoke tests to verify development environment, imports, and uv toolchain."""

import importlib
import sys
from pathlib import Path


def test_python_version():
    """Verify supported Python runtime."""
    assert sys.version_info >= (3, 12), f"Unsupported Python version: {sys.version}"


def test_core_dependencies_import():
    """Verify that all core project dependencies can be imported cleanly."""
    core_modules = [
        "bs4",
        "img2pdf",
        "matplotlib",
        "pandas",
        "PIL",
        "pyarrow",
        "pypdf",
        "pytesseract",
        "requests",
        "seaborn",
    ]
    for module_name in core_modules:
        mod = importlib.import_module(module_name)
        assert mod is not None, f"Failed to import {module_name}"


def test_repository_structure():
    """Verify all expected project directories are present."""
    root = Path(__file__).resolve().parent.parent
    expected_dirs = [
        "dashboard_prototype",
        "game",
        "multi_threading",
        "music_player",
        "notepad",
        "pdf",
        "python_training",
        "text_extraction_image",
        "web_scraping",
    ]
    for directory in expected_dirs:
        dir_path = root / directory
        assert dir_path.is_dir(), f"Expected directory missing: {directory}"
