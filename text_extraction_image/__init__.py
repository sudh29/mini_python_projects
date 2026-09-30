"""Image OCR and text extraction package."""

from text_extraction_image.image_to_text import (
    configure_tesseract,
    extract_text_from_directory,
    extract_text_from_image,
    is_tesseract_available,
    preprocess_image,
)

__all__ = [
    "configure_tesseract",
    "is_tesseract_available",
    "preprocess_image",
    "extract_text_from_image",
    "extract_text_from_directory",
]
