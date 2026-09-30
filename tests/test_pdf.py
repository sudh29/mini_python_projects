"""Unit tests for pdf module (read_pdf and image2pdf)."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pypdf
import pytest
from PIL import Image

from pdf.image2pdf import convert_images_to_pdf
from pdf.read_pdf import (
    convert_text_to_speech,
    extract_text_from_pdf,
    process_pdf_to_speech,
)


def test_extract_text_from_pdf_cheatsheet():
    """Verify text extraction from existing sample PDF."""
    pdf_path = Path("pdf/git-cheatsheet.pdf")
    assert pdf_path.exists(), "Sample PDF git-cheatsheet.pdf must exist"

    text = extract_text_from_pdf(str(pdf_path))
    assert isinstance(text, str)
    assert len(text) > 100
    assert "git" in text.lower()


def test_extract_text_from_pdf_nonexistent(tmp_path):
    """Verify FileNotFoundError on nonexistent PDF file."""
    nonexistent = tmp_path / "does_not_exist.pdf"
    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf(str(nonexistent))


def test_convert_images_to_pdf_directory(tmp_path):
    """Test converting a directory of images into a valid PDF."""
    img_dir = tmp_path / "imgs"
    img_dir.mkdir()

    # Create synthetic test images
    for i in range(3):
        img = Image.new("RGB", (100, 100), color=(i * 40, i * 60, i * 80))
        img.save(img_dir / f"page_{i}.png")

    output_pdf = tmp_path / "result.pdf"
    success = convert_images_to_pdf(str(img_dir), str(output_pdf))

    assert success is True
    assert output_pdf.exists()

    # Verify generated PDF with pypdf
    reader = pypdf.PdfReader(str(output_pdf))
    assert len(reader.pages) == 3


def test_convert_images_to_pdf_sequence(tmp_path):
    """Test converting a sequence of image paths into a valid PDF."""
    img_paths = []
    for i in range(2):
        p = tmp_path / f"test_{i}.jpg"
        img = Image.new("RGB", (80, 80), color=(100, 150, 200))
        img.save(p)
        img_paths.append(p)

    output_pdf = tmp_path / "seq_result.pdf"
    success = convert_images_to_pdf(img_paths, str(output_pdf))

    assert success is True
    assert output_pdf.exists()

    reader = pypdf.PdfReader(str(output_pdf))
    assert len(reader.pages) == 2


def test_convert_images_to_pdf_empty_dir(tmp_path):
    """Test converting an empty directory returns False."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    out = tmp_path / "out.pdf"

    assert convert_images_to_pdf(str(empty_dir), str(out)) is False
    assert not out.exists()


def test_convert_images_to_pdf_invalid_source():
    """Test converting a nonexistent path raises ValueError."""
    with pytest.raises(ValueError, match="not found"):
        convert_images_to_pdf("/path/that/definitely/does/not/exist")


def test_convert_text_to_speech_mock(tmp_path):
    """Test convert_text_to_speech with mocked pyttsx3."""
    mock_engine = MagicMock()
    mock_pyttsx3 = MagicMock()
    mock_pyttsx3.init.return_value = mock_engine
    mock_engine.getProperty.return_value = [MagicMock(id="voice1")]

    out_file = tmp_path / "speech.mp3"

    with patch.dict(sys.modules, {"pyttsx3": mock_pyttsx3}):
        success = convert_text_to_speech("Hello world test", str(out_file))
        assert success is True
        mock_engine.save_to_file.assert_called_once_with(
            "Hello world test", str(out_file)
        )
        mock_engine.runAndWait.assert_called_once()


def test_process_pdf_to_speech_mock(tmp_path):
    """Test end-to-end PDF to speech conversion with mocked pyttsx3."""
    mock_engine = MagicMock()
    mock_pyttsx3 = MagicMock()
    mock_pyttsx3.init.return_value = mock_engine
    mock_engine.getProperty.return_value = []

    out_file = tmp_path / "cheatsheet.mp3"

    with patch.dict(sys.modules, {"pyttsx3": mock_pyttsx3}):
        success = process_pdf_to_speech("pdf/git-cheatsheet.pdf", str(out_file))
        assert success is True
        mock_engine.save_to_file.assert_called_once()
