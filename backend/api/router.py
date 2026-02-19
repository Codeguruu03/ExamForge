from fastapi import APIRouter
from backend.api.endpoints import upload, analyze, similarity

router = APIRouter()

# POST /api/upload/     →  Phase 1+2: Upload + Ingestion + Normalization
router.include_router(upload.router, prefix="/upload", tags=["Ingestion & Normalization"])

# POST /api/analyze/    →  Phase 3: Classical Test Theory Analysis
router.include_router(analyze.router, prefix="/analyze", tags=["Statistical Analysis"])

# POST /api/similarity/ →  Phase 4: Duplicate & Near-Duplicate Detection
router.include_router(similarity.router, prefix="/similarity", tags=["Similarity Detection"])


