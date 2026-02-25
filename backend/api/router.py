from fastapi import APIRouter
from backend.api.endpoints import upload, analyze, similarity, responses

router = APIRouter()

# POST /api/upload/          →  Phase 1+2: Upload + Ingestion + Normalization
router.include_router(upload.router, prefix="/upload", tags=["Ingestion & Normalization"])

# POST /api/analyze/         →  Phase 3: CTT Analysis (JSON payload)
router.include_router(analyze.router, prefix="/analyze", tags=["Statistical Analysis"])

# POST /api/similarity/      →  Phase 4: Duplicate Detection
router.include_router(similarity.router, prefix="/similarity", tags=["Similarity Detection"])

# POST /api/responses/upload →  Phase 3: CTT Analysis from CSV student responses
router.include_router(responses.router, prefix="/responses", tags=["Student Responses"])



