# PDF Processing Utilities

A modular Python toolkit for PDF document processing, including text extraction, text-to-speech (TTS) conversion, and batch image-to-PDF compilation.

---

## Features

- **Text Extraction (`read_pdf.py`):** Extract text content from single or multi-page PDF documents using modern `pypdf` with fallback support for `PyPDF2`.
- **Text-to-Speech Conversion (`read_pdf.py`):** Optional speech synthesis utilizing `pyttsx3` with configurable speech rate and voice selection.
- **Batch Image-to-PDF (`image2pdf.py`):** Lossless conversion of image collections (`PNG`, `JPG`, `JPEG`, `GIF`, `BMP`, `TIFF`, `WEBP`) into unified PDF documents with deterministic sorting.
- **Headless & Cross-Platform Friendly:** Safe execution on Linux, macOS, and Windows without graphical dependencies.

---

## Installation

Ensure dependencies are installed using `uv`:

```bash
uv sync --extra dev
```

Key dependencies:
- `pypdf`: PDF parsing and text extraction.
- `img2pdf`: Lossless image-to-PDF compilation.
- `pyttsx3` *(optional)*: For offline text-to-speech audio rendering (`uv add pyttsx3`).

---

## Command-Line Usage

### 1. Extract Text & Convert to Speech (`read_pdf.py`)

```bash
# Convert a PDF to speech audio
uv run python pdf/read_pdf.py --file pdf/git-cheatsheet.pdf --output cheatsheet.mp3

# Specify custom voice index
uv run python pdf/read_pdf.py --file document.pdf --output narration.mp3 --voice 1
```

### 2. Batch Convert Images to PDF (`image2pdf.py`)

```bash
# Convert all images in the pdf/images directory to a single PDF
uv run python pdf/image2pdf.py --directory pdf/images --output document.pdf

# Specify custom directory and output path
uv run python pdf/image2pdf.py --directory ./photos --output portfolio.pdf
```

---

## Python API Usage

```python
from pdf import extract_text_from_pdf, convert_images_to_pdf

# Extract text from a document
text = extract_text_from_pdf("pdf/git-cheatsheet.pdf")
print(f"Extracted {len(text)} characters")

# Compile directory of images to a PDF
success = convert_images_to_pdf(
    source="pdf/images",
    output_path="compiled.pdf",
    image_formats=["png", "jpg", "jpeg", "gif"],
)
```

---

## Testing

Run unit tests via `pytest`:

```bash
uv run pytest tests/test_pdf.py
```
