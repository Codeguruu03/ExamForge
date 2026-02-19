"""
Ingestion Service — Phase 1 + OCR.space Integration

Handles all document types:
  - PDF (text-based)   → PyMuPDF direct extraction
  - PDF (scanned)      → OCR.space API (auto-detected by low text yield)
  - DOCX               → python-docx
  - Images (.jpg, .png, .jpeg, .tiff, .bmp, .gif) → OCR.space API
  - CSV / TXT          → direct text read

Smart routing: if PyMuPDF yields < 50 characters from a PDF,
it is assumed to be a scanned document and falls back to OCR.space.
"""

import os
import requests
import fitz          # PyMuPDF
import docx
from dotenv import load_dotenv

load_dotenv()

OCR_SPACE_API_KEY = os.getenv("OCR_SPACE_API_KEY", "helloworld")
OCR_SPACE_URL = "https://api.ocr.space/parse/image"

# Minimum chars extracted by PyMuPDF for us to consider it text-based
TEXT_PDF_THRESHOLD = 50


class IngestionService:

    # ─── Public Router ────────────────────────────────────────────────────────

    @staticmethod
    def process_file(file_path: str, file_ext: str) -> dict:
        """
        Route the file to the correct extractor based on extension.
        Always returns: {"raw_text": str, "type": str, ...metadata}
        """
        ext = file_ext.lower()

        if ext == ".pdf":
            return IngestionService._process_pdf(file_path)

        elif ext == ".docx":
            return IngestionService._extract_from_docx(file_path)

        elif ext in {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".gif"}:
            return IngestionService._extract_from_image_ocr(file_path)

        elif ext in {".txt", ".csv"}:
            return IngestionService._extract_from_text(file_path)

        else:
            raise ValueError(f"Unsupported file extension: {ext}")

    # ─── PDF: Smart Router ────────────────────────────────────────────────────

    @staticmethod
    def _process_pdf(file_path: str) -> dict:
        """
        Try PyMuPDF first. If text yield is too low → scanned PDF → OCR.space.
        """
        text = IngestionService._pymupdf_extract(file_path)

        if len(text.strip()) >= TEXT_PDF_THRESHOLD:
            return {
                "raw_text": text,
                "type": "pdf_text",
                "pages": IngestionService._pdf_page_count(file_path),
                "ocr_used": False,
            }
        else:
            # Scanned PDF — hand off to OCR.space
            ocr_text = IngestionService._extract_via_ocr_space(
                file_path=file_path,
                file_type="pdf",
            )
            return {
                "raw_text": ocr_text,
                "type": "pdf_scanned",
                "pages": IngestionService._pdf_page_count(file_path),
                "ocr_used": True,
            }

    # ─── PyMuPDF (text-based PDF) ─────────────────────────────────────────────

    @staticmethod
    def _pymupdf_extract(file_path: str) -> str:
        try:
            doc = fitz.open(file_path)
            return "\n".join(page.get_text() for page in doc)
        except Exception as e:
            raise RuntimeError(f"PyMuPDF extraction failed: {e}")

    @staticmethod
    def _pdf_page_count(file_path: str) -> int:
        try:
            return len(fitz.open(file_path))
        except Exception:
            return 0

    # ─── DOCX ────────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_from_docx(file_path: str) -> dict:
        try:
            doc = docx.Document(file_path)
            text = "\n".join(para.text for para in doc.paragraphs if para.text.strip())
            return {"raw_text": text, "type": "docx", "ocr_used": False}
        except Exception as e:
            raise RuntimeError(f"DOCX extraction failed: {e}")

    # ─── Plain text / CSV ─────────────────────────────────────────────────────

    @staticmethod
    def _extract_from_text(file_path: str) -> dict:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            return {"raw_text": text, "type": "text", "ocr_used": False}
        except Exception as e:
            raise RuntimeError(f"Text file read failed: {e}")

    # ─── Image → OCR.space ───────────────────────────────────────────────────

    @staticmethod
    def _extract_from_image_ocr(file_path: str) -> dict:
        text = IngestionService._extract_via_ocr_space(
            file_path=file_path,
            file_type="image",
        )
        return {"raw_text": text, "type": "image_ocr", "ocr_used": True}

    # ─── OCR.space Core Call ──────────────────────────────────────────────────

    @staticmethod
    def _extract_via_ocr_space(file_path: str, file_type: str = "image") -> str:
        """
        Send a file to OCR.space API and return extracted text.

        Docs: https://ocr.space/ocrapi
        Supports: JPG, PNG, GIF, PDF, TIFF, BMP
        """
        if not OCR_SPACE_API_KEY:
            raise RuntimeError(
                "OCR_SPACE_API_KEY is not set. "
                "Add it to your .env file: OCR_SPACE_API_KEY=your_key_here"
            )

        payload = {
            "apikey": OCR_SPACE_API_KEY,
            "language": "eng",
            "isOverlayRequired": False,
            "detectOrientation": True,
            "scale": True,
            "OCREngine": 2,       # Engine 2 handles complex layouts better
            "isCreateSearchablePdf": False,
            "isSearchablePdfHideTextLayer": False,
        }

        try:
            with open(file_path, "rb") as f:
                filename = os.path.basename(file_path)
                response = requests.post(
                    OCR_SPACE_URL,
                    data=payload,
                    files={"filename": (filename, f)},
                    timeout=60,
                )

            response.raise_for_status()
            result = response.json()

            # OCR.space error handling
            if result.get("IsErroredOnProcessing"):
                error_msg = result.get("ErrorMessage", ["Unknown OCR error"])
                if isinstance(error_msg, list):
                    error_msg = " | ".join(error_msg)
                raise RuntimeError(f"OCR.space API error: {error_msg}")

            # Extract text from all parsed results (multi-page support)
            parsed_results = result.get("ParsedResults", [])
            if not parsed_results:
                raise RuntimeError("OCR.space returned no parsed results.")

            full_text = "\n".join(
                pr.get("ParsedText", "") for pr in parsed_results
            )

            return full_text.strip()

        except requests.exceptions.Timeout:
            raise RuntimeError(
                "OCR.space API timed out. "
                "The file may be too large or the service is slow."
            )
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"OCR.space network error: {e}")
