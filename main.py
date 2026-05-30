"""
CalcVoyager Backend — Starlette + stdlib sqlite3
Works on Python 3.10+ including 3.14.
No pydantic, no aiosqlite, no SQLAlchemy.
"""

import os
from pathlib import Path

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse

# Load .env manually (no python-dotenv needed)
_env_file = Path(__file__).parent / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

from db import init_db
from routers.auth import routes as auth_routes
from routers.progress import routes as progress_routes
from routers.bookmarks import routes as bookmark_routes
from routers.quiz import routes as quiz_routes
from routers.solver_proxy import routes as solver_routes


async def health(request):
    return JSONResponse({"status": "ok"})


async def on_startup():
    await init_db()


ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
).split(",")

app = Starlette(
    debug=False,
    routes=[
        Route("/api/health", health),
        Mount("/api/auth", routes=auth_routes),
        Mount("/api/progress", routes=progress_routes),
        Mount("/api/bookmarks", routes=bookmark_routes),
        Mount("/api/quiz", routes=quiz_routes),
        Mount("/api/solver", routes=solver_routes),
    ],
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ],
    on_startup=[on_startup],
)
