from fastapi import APIRouter
from backend.api.endpoints import upload

router = APIRouter()

router.include_router(upload.router, prefix="/upload", tags=["Upload"])
