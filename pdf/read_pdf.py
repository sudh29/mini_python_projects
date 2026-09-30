"""
Extract text from PDF files with optional text-to-speech conversion.

This module provides utilities to read PDF files, extract text content,
and optionally convert extracted text to speech.

Features:
- Extract text from single or multiple PDF pages
- Text-to-speech conversion support
- Configurable voice selection
- Error handling for corrupted PDFs
- Support for multiple file dialog selections
- Logging support

Usage:
    python read_pdf.py --file document.pdf --output audio.mp3
"""

import logging
from pathlib import Path

DEFAULT_PDF_PATH = "pdf/git-cheatsheet.pdf"

try:
    import pypdf as pdf_lib
except ImportError:
    try:
        import PyPDF2 as pdf_lib
    except ImportError:
        pdf_lib = None


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF file.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        str: Extracted text from all pages

    Raises:
        FileNotFoundError: If PDF file doesn't exist
        ImportError: If pypdf or PyPDF2 is not installed
        Exception: If PDF parsing fails
    """
    if pdf_lib is None:
        raise ImportError(
            "pypdf or PyPDF2 is required to extract text from PDF. Install with: uv add pypdf"
        )

    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    try:
        extracted_text = ""

        with open(pdf_path, "rb") as pdf_file:
            pdf_reader = pdf_lib.PdfReader(pdf_file)
            num_pages = len(pdf_reader.pages)

            logger.info(f"Processing {num_pages} pages from {pdf_path}")

            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text() or ""
                extracted_text += text + "\n"
                logger.debug(f"Extracted page {page_num + 1}/{num_pages}")

        logger.info(f"Successfully extracted {len(extracted_text)} characters")
        return extracted_text

    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise


def convert_text_to_speech(
    text: str, output_file: str = "audio.mp3", voice_index: int = 0, rate: int = 150
) -> bool:
    """
    Convert text to speech and save to audio file.

    Args:
        text: Text to convert to speech
        output_file: Path where audio file will be saved
        voice_index: Index of voice to use (0=default)
        rate: Speech rate in words per minute

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        import pyttsx3
    except ImportError:
        logger.error(
            "pyttsx3 is not installed. To enable text-to-speech, install with: uv add pyttsx3"
        )
        return False

    try:
        engine = pyttsx3.init()

        # Set voice properties
        voices = engine.getProperty("voices")
        if voice_index < len(voices):
            engine.setProperty("voice", voices[voice_index].id)

        engine.setProperty("rate", rate)

        logger.info(f"Converting text to speech ({len(text)} characters)")

        # Save to file
        engine.save_to_file(text, output_file)
        engine.runAndWait()

        logger.info(f"Audio saved to: {output_file}")
        return True

    except Exception as e:
        logger.error(f"Error converting text to speech: {str(e)}")
        return False


def process_pdf_to_speech(
    pdf_path: str, output_file: str = "output.mp3", voice_index: int = 0
) -> bool:
    """
    Extract text from PDF and convert to speech.

    Args:
        pdf_path: Path to PDF file
        output_file: Path for output audio file
        voice_index: Index of voice to use

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Starting PDF to speech conversion: {pdf_path}")

        # Extract text
        text = extract_text_from_pdf(pdf_path)

        if not text.strip():
            logger.warning("No text extracted from PDF")
            return False

        # Convert to speech
        success = convert_text_to_speech(text, output_file, voice_index)

        if success:
            logger.info("PDF to speech conversion completed successfully")

        return success

    except Exception as e:
        logger.error(f"Error in PDF to speech conversion: {str(e)}")
        return False


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Extract text from PDF and convert to speech"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="PDF file path (if not provided, shows file dialog or uses default)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output.mp3",
        help="Output audio file path (default: output.mp3)",
    )
    parser.add_argument(
        "--voice", type=int, default=0, help="Voice index to use (default: 0)"
    )

    args = parser.parse_args()

    # Get PDF file path
    pdf_file = args.file
    if not pdf_file:
        # Check if GUI is supported
        import os

        if os.environ.get("DISPLAY") or sys.platform == "win32":
            try:
                import tkinter as tk
                from tkinter.filedialog import askopenfilename

                root = tk.Tk()
                root.withdraw()
                pdf_file = askopenfilename(
                    title="Select PDF file",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                )
                root.destroy()
            except Exception as e:
                logger.debug(f"GUI file dialog unavailable: {e}")
                pdf_file = None

        if not pdf_file and Path(DEFAULT_PDF_PATH).exists():
            logger.info(f"Using default sample PDF: {DEFAULT_PDF_PATH}")
            pdf_file = DEFAULT_PDF_PATH

    if pdf_file:
        success = process_pdf_to_speech(pdf_file, args.output, args.voice)
        sys.exit(0 if success else 1)
    else:
        logger.warning("No PDF file selected or available")
        sys.exit(1)
