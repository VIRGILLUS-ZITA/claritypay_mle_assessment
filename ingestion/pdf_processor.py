import fitz
from pathlib import Path

PDF_PATH = Path("data/sample_merchant_summary.pdf")


def extract_pdf_text(path: Path = PDF_PATH) -> str:
    text = []
    with fitz.open(path) as doc:
        for page in doc:
            text.append(page.get_text())
    return "\n".join(text)
