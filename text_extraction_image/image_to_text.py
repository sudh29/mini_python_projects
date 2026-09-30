"""
Extract text from images using Optical Character Recognition (OCR).

This module provides utilities to perform OCR on image files using Tesseract,
extracting text content with support for multiple languages and preprocessing.

Features:
- Extract text from JPEG, PNG, BMP, and other image formats
- Support for multiple languages
- Image preprocessing (grayscale, contrast adjustment)
- Batch processing of multiple images
- Configurable Tesseract path for different systems
- Error handling and validation
- Logging support

Usage:
    python image_to_text.py --image photo.jpg
    python image_to_text.py --directory ./images/ --output results.txt
"""

import logging
import os
import shutil
import sys
from pathlib import Path

try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError as e:
    raise ImportError(
        f"Required packages not installed: {str(e)}\n"
        "Install with: pip install pytesseract pillow"
    )


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def configure_tesseract(
    tesseract_cmd: str | None = None,
    tessdata_dir: str | None = None,
) -> bool:
    """
    Auto-detect or configure Tesseract executable and tessdata path.

    Returns:
        bool: True if a valid executable candidate was configured, False otherwise.
    """
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    elif os.environ.get("TESSERACT_CMD"):
        pytesseract.pytesseract.tesseract_cmd = os.environ["TESSERACT_CMD"]
    elif sys.platform == "win32":
        possible_win_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
        ]
        for p in possible_win_paths:
            if os.path.exists(p):
                pytesseract.pytesseract.tesseract_cmd = p
                break
    else:
        found = shutil.which("tesseract")
        if found:
            pytesseract.pytesseract.tesseract_cmd = found
        elif sys.platform == "darwin":
            for mac_path in ["/opt/homebrew/bin/tesseract", "/usr/local/bin/tesseract"]:
                if os.path.exists(mac_path):
                    pytesseract.pytesseract.tesseract_cmd = mac_path
                    break

    if tessdata_dir:
        os.environ["TESSDATA_PREFIX"] = str(tessdata_dir)

    return is_tesseract_available()


def is_tesseract_available() -> bool:
    """
    Check if the Tesseract binary is available and executable.
    """
    cmd = getattr(pytesseract.pytesseract, "tesseract_cmd", "tesseract")
    if not cmd:
        cmd = "tesseract"

    if os.path.isabs(cmd):
        return os.path.isfile(cmd) and os.access(cmd, os.X_OK)

    return shutil.which(cmd) is not None


# Run auto-discovery on module import
configure_tesseract()


def preprocess_image(image: Image.Image) -> Image.Image:
    """
    Apply preprocessing to improve OCR accuracy.

    Args:
        image: PIL Image object

    Returns:
        Image.Image: Preprocessed image (grayscale, contrast, sharpness, median filter)
    """
    # Convert to grayscale
    processed = image.convert("L") if image.mode != "L" else image.copy()

    # Increase contrast
    enhancer = ImageEnhance.Contrast(processed)
    processed = enhancer.enhance(2)

    # Apply sharpness
    sharpness_enhancer = ImageEnhance.Sharpness(processed)
    processed = sharpness_enhancer.enhance(2)

    # Apply slight blur to remove noise
    processed = processed.filter(ImageFilter.MedianFilter())

    return processed


_preprocess_image = preprocess_image


def extract_text_from_image(
    image_path: str, language: str = "eng", preprocess: bool = False
) -> str | None:
    """
    Extract text from a single image file using OCR.

    Args:
        image_path: Path to the image file
        language: Tesseract language code (default: 'eng')
        preprocess: Whether to apply image preprocessing (default: False)

    Returns:
        str: Extracted text from the image, or None if extraction fails

    Raises:
        FileNotFoundError: If image file doesn't exist
        RuntimeError: If Tesseract executable is not found
        PIL.UnidentifiedImageError: If file is not a valid image
    """
    if not Path(image_path).exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    if not is_tesseract_available():
        raise RuntimeError(
            "Tesseract executable not found. Please install Tesseract OCR "
            "(e.g., 'sudo apt-get install tesseract-ocr' or 'brew install tesseract') "
            "or set TESSERACT_CMD environment variable."
        )

    try:
        logger.info(f"Processing image: {image_path}")

        # Open the image
        with Image.open(image_path) as image:
            # Apply preprocessing if requested
            if preprocess:
                image = preprocess_image(image)

            # Extract text using Tesseract
            text = pytesseract.image_to_string(image, lang=language)

            if text.strip():
                logger.info(f"Successfully extracted {len(text)} characters")
            else:
                logger.warning("No text detected in image")

            return text

    except pytesseract.TesseractError as te:
        logger.error(f"Tesseract OCR engine error: {te}")
        raise
    except Exception as e:
        logger.error(f"Error extracting text from image: {str(e)}")
        raise


def extract_text_from_directory(
    directory: str,
    output_file: str | None = None,
    language: str = "eng",
    recursive: bool = False,
) -> dict[str, str]:
    """
    Extract text from all images in a directory.

    Args:
        directory: Path to directory containing images
        output_file: Optional file to save all extracted text
        language: Tesseract language code
        recursive: Whether to process subdirectories

    Returns:
        dict: Dictionary mapping image paths to extracted text

    Raises:
        ValueError: If directory doesn't exist
    """
    if not os.path.isdir(directory):
        raise ValueError(f"Directory not found: {directory}")

    results = {}
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"}

    try:
        logger.info(f"Processing directory: {directory}")

        # Get all image files
        if recursive:
            image_files = []
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if Path(file).suffix.lower() in image_extensions:
                        image_files.append(os.path.join(root, file))
        else:
            image_files = [
                os.path.join(directory, f)
                for f in os.listdir(directory)
                if Path(f).suffix.lower() in image_extensions
            ]

        logger.info(f"Found {len(image_files)} image(s)")

        # Process each image
        for idx, image_file in enumerate(sorted(image_files), 1):
            try:
                logger.info(f"[{idx}/{len(image_files)}] Processing {image_file}")
                text = extract_text_from_image(image_file, language)
                results[image_file] = text if text else ""
            except Exception as e:
                logger.warning(f"Failed to process {image_file}: {str(e)}")
                results[image_file] = None

        # Save results if output file specified
        if output_file:
            _save_results(results, output_file)

        logger.info(
            f"Successfully processed {len([v for v in results.values() if v])}/{len(image_files)} images"
        )
        return results

    except Exception as e:
        logger.error(f"Error processing directory: {str(e)}")
        return {}


def _save_results(results: dict[str, str], output_file: str) -> None:
    """
    Save extracted text results to file.

    Args:
        results: Dictionary of image paths to extracted text
        output_file: Path where results will be saved
    """
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            for image_path, text in sorted(results.items()):
                f.write(f"=== {image_path} ===\n")
                if text:
                    f.write(text)
                else:
                    f.write("[No text detected]\n")
                f.write("\n\n")

        logger.info(f"Results saved to: {output_file}")
    except Exception as e:
        logger.error(f"Error saving results: {str(e)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Extract text from images using OCR")
    parser.add_argument("--image", type=str, help="Path to single image file")
    parser.add_argument(
        "--directory", type=str, help="Path to directory containing images"
    )
    parser.add_argument(
        "--output", type=str, help="Output file to save results (optional)"
    )
    parser.add_argument(
        "--language",
        type=str,
        default="eng",
        help="Tesseract language code (default: eng)",
    )
    parser.add_argument(
        "--preprocess", action="store_true", help="Apply image preprocessing before OCR"
    )
    parser.add_argument(
        "--recursive", action="store_true", help="Recursively process subdirectories"
    )

    args = parser.parse_args()

    # Process single image
    if args.image:
        try:
            text = extract_text_from_image(
                args.image, language=args.language, preprocess=args.preprocess
            )
            print("=== Extracted Text ===")
            print(text if text else "[No text detected]")
        except Exception as e:
            logger.error(f"Failed to process image: {str(e)}")
            sys.exit(1)

    # Process directory
    elif args.directory:
        results = extract_text_from_directory(
            args.directory,
            output_file=args.output,
            language=args.language,
            recursive=args.recursive,
        )
        if results:
            logger.info("Text extraction completed")
            sys.exit(0)
        else:
            logger.error("Failed to process directory")
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)
