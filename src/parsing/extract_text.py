from pathlib import Path
from pdf2image import convert_from_path
import pytesseract

# OCR config
custom_oem_psm_config = r'--oem 3 --psm 6'

def extract_text_psm6(filepath: Path) -> str:
    """
    Extract text from a PDF using pytesseract with PSM 6.

    Args:
        filepath (Path): Path to the PDF file.

    Returns:
        str: The full extracted text from all pages.
    """
    pages = convert_from_path(filepath, dpi=300)
    return "".join(
        pytesseract.image_to_string(page, config=custom_oem_psm_config, lang='nld')
        for page in pages
    )
