# Optical Character Recognition (OCR) Image-to-Text Extraction

A modular, cross-platform Python toolkit for extracting text from images using Tesseract OCR and Pillow (`PIL`).

---

## Features

- **Multi-Format Image Support:** Extract text from PNG, JPG, JPEG, BMP, GIF, and TIFF images.
- **Image Preprocessing Pipeline:** Automated contrast enhancement, grayscale normalization, sharpening, and median noise filtering for increased OCR precision.
- **Cross-Platform Auto-Discovery:** Seamlessly discovers Tesseract binaries on Linux (`/usr/bin/tesseract`), macOS Homebrew paths, and standard Windows installation paths.
- **Batch Directory Processing:** Recursive and non-recursive directory scanning with formatted text summary exporting.
- **Robust Exception Handling:** Informative diagnostic errors when system OCR binaries or language packs (`tessdata`) are missing.

---

## Prerequisites & Installation

### 1. Install System Tesseract OCR Binary

Tesseract OCR requires a system binary installation:

- **Debian / Ubuntu:**
  ```bash
  sudo apt-get install tesseract-ocr tesseract-ocr-eng
  ```
- **macOS (Homebrew):**
  ```bash
  brew install tesseract
  ```
- **Windows:**
  Install from [UB-Mannheim Tesseract Releases](https://github.com/UB-Mannheim/tesseract/wiki) or via Chocolatey:
  ```powershell
  choco install tesseract
  ```

### 2. Install Python Dependencies

```bash
uv sync --extra dev
```

Key dependencies:
- `pytesseract`: Python wrapper for Google's Tesseract-OCR Engine.
- `pillow`: Image processing, filtering, and manipulation.

---

## Command-Line Usage

### 1. Extract Text from a Single Image

```bash
# Basic extraction
uv run python text_extraction_image/image_to_text.py --image text_extraction_image/image2.png

# With image preprocessing enabled
uv run python text_extraction_image/image_to_text.py --image invoice.jpg --preprocess

# Specify language
uv run python text_extraction_image/image_to_text.py --image spanish_menu.png --language spa
```

### 2. Batch Process a Directory of Images

```bash
# Extract from directory and save results to text file
uv run python text_extraction_image/image_to_text.py --directory ./documents --output results.txt

# Recursive directory traversal
uv run python text_extraction_image/image_to_text.py --directory ./scans --recursive --output all_text.txt
```

---

## Python API Usage

```python
from text_extraction_image import (
    configure_tesseract,
    is_tesseract_available,
    preprocess_image,
    extract_text_from_image,
    extract_text_from_directory,
)

# Verify environment
if is_tesseract_available():
    text = extract_text_from_image("text_extraction_image/image2.png", preprocess=True)
    print(text)

# Batch processing
results = extract_text_from_directory(
    directory="text_extraction_image", output_file="extracted.txt"
)
```

---

## Testing

Run unit tests via `pytest`:

```bash
uv run pytest tests/test_ocr.py
```
