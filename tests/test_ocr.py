"""Unit tests for text_extraction_image module."""

from unittest.mock import patch

import pytest
from PIL import Image

from text_extraction_image.image_to_text import (
    configure_tesseract,
    extract_text_from_directory,
    extract_text_from_image,
    is_tesseract_available,
    preprocess_image,
)


def test_preprocess_image():
    """Verify image preprocessing converts color image to processed grayscale."""
    img = Image.new("RGB", (120, 80), color=(180, 100, 50))
    processed = preprocess_image(img)

    assert processed.size == (120, 80)
    assert processed.mode == "L"


def test_is_tesseract_available_boolean():
    """Ensure is_tesseract_available returns a clean boolean."""
    avail = is_tesseract_available()
    assert isinstance(avail, bool)


def test_configure_tesseract_custom_path():
    """Verify custom tesseract binary path can be configured."""
    with patch("shutil.which", return_value="/usr/bin/tesseract"):
        result = configure_tesseract("/usr/bin/tesseract", tessdata_dir="/tmp/tessdata")
        assert result is True


def test_extract_text_nonexistent_file(tmp_path):
    """Verify FileNotFoundError when input image path is invalid."""
    bad_img = tmp_path / "ghost.png"
    with pytest.raises(FileNotFoundError):
        extract_text_from_image(str(bad_img))


def test_extract_text_with_mock(tmp_path):
    """Verify extract_text_from_image with mocked pytesseract."""
    test_img = tmp_path / "mock_test.png"
    img = Image.new("RGB", (50, 50), color="white")
    img.save(test_img)

    with patch(
        "text_extraction_image.image_to_text.is_tesseract_available", return_value=True
    ):
        with patch(
            "pytesseract.image_to_string", return_value="Mocked OCR Text Result"
        ):
            text = extract_text_from_image(str(test_img), preprocess=True)
            assert text == "Mocked OCR Text Result"


def test_extract_text_tesseract_unavailable(tmp_path):
    """Verify RuntimeError is raised when Tesseract is not available."""
    test_img = tmp_path / "sample.png"
    Image.new("RGB", (20, 20), color="blue").save(test_img)

    with patch(
        "text_extraction_image.image_to_text.is_tesseract_available", return_value=False
    ):
        with pytest.raises(RuntimeError, match="Tesseract executable not found"):
            extract_text_from_image(str(test_img))


def test_extract_text_from_directory_mock(tmp_path):
    """Verify batch directory processing with mock and file export."""
    img_dir = tmp_path / "ocr_batch"
    img_dir.mkdir()

    for name in ["doc1.png", "doc2.jpg"]:
        Image.new("RGB", (30, 30), color="white").save(img_dir / name)

    out_file = tmp_path / "results.txt"

    with patch(
        "text_extraction_image.image_to_text.is_tesseract_available", return_value=True
    ):
        with patch("pytesseract.image_to_string", return_value="Extracted Line"):
            results = extract_text_from_directory(
                str(img_dir), output_file=str(out_file)
            )

            assert len(results) == 2
            assert out_file.exists()
            content = out_file.read_text(encoding="utf-8")
            assert "Extracted Line" in content
