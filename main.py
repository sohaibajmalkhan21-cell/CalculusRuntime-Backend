"""
CalcVoyager Backend
FastAPI + SQLite — auth, progress, bookmarks, quiz scores
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db import init_db
from routers import auth, progress, bookmarks, quiz, solver_proxy

app = FastAPI(title="CalcVoyager API", version="1.0.0")

# ── CORS ──────────────────────────────────────────────────────────────────────
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    await init_db()


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(progress.router, prefix="/api/progress", tags=["progress"])
app.include_router(bookmarks.router, prefix="/api/bookmarks", tags=["bookmarks"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["quiz"])
app.include_router(solver_proxy.router, prefix="/api/solver", tags=["solver"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}
