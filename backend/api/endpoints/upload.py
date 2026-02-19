from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
import uuid
from backend.services.ingestion import IngestionService
from backend.services.normalizer import normalize
from backend.core.models import NormalizationResult

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {
    # Documents
    ".pdf", ".docx", ".txt", ".csv",
    # Images (handled by OCR.space)
    ".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".gif",
}



@router.post("/", response_model=NormalizationResult)
async def upload_and_normalize(file: UploadFile = File(...)):
    """
    Full pipeline endpoint:
    1. Accept file upload (PDF, DOCX, TXT, CSV)
    2. Extract raw text via IngestionService
    3. Run Normalization Engine to produce structured Exam JSON
    Returns a NormalizationResult with the structured exam and any warnings.
    """
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{file_ext}'. Allowed: {ALLOWED_EXTENSIONS}"
        )

    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_ext}")

    # Save file to disk
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save error: {str(e)}")

    # Step 1: Extract raw text
    try:
        extraction = IngestionService.process_file(file_path, file_ext)
        raw_text = extraction.get("raw_text", "")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text extraction failed: {str(e)}")

    if not raw_text.strip():
        raise HTTPException(
            status_code=422,
            detail="No text could be extracted from the file. "
                   "If this is a scanned document, please provide an OCR API key."
        )

    # Step 2: Normalize into structured Exam
    try:
        result = normalize(raw_text, source_file=file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Normalization failed: {str(e)}")

    return result
