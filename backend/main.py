import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.router import router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="ExamForge — Exam Reliability Analyzer",
    version="1.0.0",
    description="Analyzes exam quality using Classical Test Theory metrics and duplicate detection.",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# In production set ALLOWED_ORIGINS="https://yourfrontend.com" in .env
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(router, prefix="/api")


@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "service": "ExamForge API",
        "version": "1.0.0",
        "docs": "/docs",
    }

# ── Frontend (Production / Docker) ────────────────────────────────────────────
frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_react_app(full_path: str):
        # Serve index.html for all undefined routes (React Router support)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
