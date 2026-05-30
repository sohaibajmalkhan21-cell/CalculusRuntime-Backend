"""Solver usage logging routes."""

from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse

import db
from auth_utils import require_user, err


async def log_use(request: Request):
    """Frontend calls this after each solver interaction."""
    user_id = require_user(request)
    try:
        body = await request.json()
    except Exception:
        body = {}

    expression = body.get("expression") or None
    result = body.get("result") or None

    if user_id:
        await db.execute(
            "INSERT INTO solver_history (user_id, expression, result) VALUES (?, ?, ?)",
            (user_id, expression, result),
        )
    return JSONResponse({"ok": True})


async def get_history(request: Request):
    user_id = require_user(request)
    if not user_id:
        return JSONResponse([])

    rows = await db.fetchall(
        "SELECT expression, result, created_at FROM solver_history "
        "WHERE user_id = ? ORDER BY created_at DESC LIMIT 50",
        (user_id,),
    )
    return JSONResponse(rows)


routes = [
    Route("/log", log_use, methods=["POST"]),
    Route("/history", get_history, methods=["GET"]),
]
