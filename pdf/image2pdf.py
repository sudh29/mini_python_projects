"""
Convert multiple image files to a single PDF document.

This module provides utilities to batch convert image files (PNG, JPG, JPEG)
into a single consolidated PDF file.

Features:
- Convert multiple image formats to PDF
- Batch processing support
- Configurable output directory
- Error handling for invalid images
- Logging support

Usage:
    python image2pdf.py --directory /path/to/images/ --output result.pdf
"""

import logging
import sys
from collections.abc import Sequence
from pathlib import Path

import img2pdf

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

DEFAULT_IMAGE_FORMATS = ["png", "jpg", "jpeg", "bmp", "tiff", "webp", "gif"]


def convert_images_to_pdf(
    source: str | Path | Sequence[str | Path],
    output_path: str | Path = "output.pdf",
    image_formats: list[str] | None = None,
) -> bool:
    """
    Convert images to a single PDF file.

    Args:
        source: Path to directory containing images, or a sequence of image file paths
        output_path: Path where PDF will be saved (default: output.pdf)
        image_formats: List of file extensions to process if source is a directory

    Returns:
        bool: True if successful, False otherwise

    Raises:
        ValueError: If source directory doesn't exist
        IOError: If PDF write operation fails
    """
    if image_formats is None:
        image_formats = DEFAULT_IMAGE_FORMATS

    try:
        image_list: list[str] = []

        if isinstance(source, (str, Path)):
            source_path = Path(source)
            if not source_path.exists():
                raise ValueError(f"Image source path not found: {source}")

            if source_path.is_dir():
                image_files = set()
                for fmt in image_formats:
                    clean_fmt = fmt.lstrip(".").lower()
                    for file_path in source_path.glob(f"*.{clean_fmt}"):
                        image_files.add(file_path)
                    for file_path in source_path.glob(f"*.{clean_fmt.upper()}"):
                        image_files.add(file_path)

                if not image_files:
                    logger.warning(f"No matching images found in directory {source}")
                    return False

                logger.info(f"Found {len(image_files)} images to convert")
                image_list = [str(img) for img in sorted(image_files)]
            else:
                image_list = [str(source_path)]
        else:
            image_list = [str(Path(p)) for p in source if Path(p).exists()]
            if not image_list:
                logger.warning("No valid existing image paths provided in sequence")
                return False

        # Ensure output directory exists
        output_file_path = Path(output_path)
        if output_file_path.parent:
            output_file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file_path, "wb") as pdf_file:
            pdf_file.write(img2pdf.convert(image_list))

        logger.info(f"PDF successfully created: {output_file_path}")
        return True

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Error converting images to PDF: {str(e)}")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert images to PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert all images in current directory
  python image2pdf.py

  # Specify custom input and output directories
  python image2pdf.py --directory ./photos --output result.pdf

  # Convert images from specific directory
  python image2pdf.py --directory /path/to/images --output combined.pdf
        """,
    )
    parser.add_argument(
        "--directory",
        type=str,
        default=".",
        help="Directory containing images (default: current directory)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="output.pdf",
        help="Output PDF file path (default: output.pdf)",
    )

    args = parser.parse_args()

    try:
        success = convert_images_to_pdf(args.directory, args.output)
        sys.exit(0 if success else 1)
    except ValueError as e:
        logger.error(f"Invalid input: {str(e)}")
        sys.exit(1)
    except OSError as e:
        logger.error(f"File operation failed: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)
