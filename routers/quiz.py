"""Quiz scores routes."""

from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse

import db
from auth_utils import require_user, err


async def list_scores(request: Request):
    user_id = require_user(request)
    if not user_id:
        return err(401, "Not authenticated.")

    rows = await db.fetchall(
        "SELECT quiz_id, score, total FROM quiz_scores "
        "WHERE user_id = ? ORDER BY taken_at DESC",
        (user_id,),
    )
    return JSONResponse(
        {r["quiz_id"]: {"score": r["score"], "total": r["total"]} for r in rows}
    )


async def save_score(request: Request):
    user_id = require_user(request)
    if not user_id:
        return err(401, "Not authenticated.")
    try:
        body = await request.json()
    except Exception:
        return err(400, "Invalid JSON.")

    quiz_id = (body.get("quiz_id") or "").strip()
    score = body.get("score")
    total = body.get("total")

    if not quiz_id or score is None or total is None:
        return err(400, "quiz_id, score, and total are required.")

    await db.execute(
        "INSERT INTO quiz_scores (user_id, quiz_id, score, total) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(user_id, quiz_id) DO UPDATE SET "
        "  score = CASE WHEN excluded.score > score THEN excluded.score ELSE score END, "
        "  total = excluded.total, "
        "  taken_at = strftime('%s','now')",
        (user_id, quiz_id, int(score), int(total)),
    )
    return JSONResponse({"ok": True}, status_code=201)


routes = [
    Route("/", list_scores, methods=["GET"]),
    Route("/", save_score, methods=["POST"]),
]
