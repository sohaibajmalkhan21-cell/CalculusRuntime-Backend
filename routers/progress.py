"""Progress routes — full snapshot, mark/unmark sections."""

from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse

import db
from auth_utils import require_user, err


async def get_progress(request: Request):
    user_id = require_user(request)
    if not user_id:
        return err(401, "Not authenticated.")

    section_rows = await db.fetchall(
        "SELECT section_id FROM sections WHERE user_id = ?", (user_id,)
    )
    completed_sections = {r["section_id"]: True for r in section_rows}

    quiz_rows = await db.fetchall(
        "SELECT quiz_id, score, total FROM quiz_scores WHERE user_id = ?", (user_id,)
    )
    quiz_scores = {
        r["quiz_id"]: {"score": r["score"], "total": r["total"]} for r in quiz_rows
    }

    bm_rows = await db.fetchall(
        "SELECT bm_id, title, path, added_at FROM bookmarks "
        "WHERE user_id = ? ORDER BY added_at DESC",
        (user_id,),
    )
    bookmarks = [
        {
            "id": r["bm_id"],
            "title": r["title"],
            "path": r["path"],
            "addedAt": r["added_at"],
        }
        for r in bm_rows
    ]

    solver_count = (
        await db.scalar(
            "SELECT COUNT(*) FROM solver_history WHERE user_id = ?", (user_id,)
        )
        or 0
    )

    return JSONResponse(
        {
            "completedSections": completed_sections,
            "quizScores": quiz_scores,
            "bookmarks": bookmarks,
            "solverUses": solver_count,
        }
    )


async def mark_complete(request: Request):
    user_id = require_user(request)
    if not user_id:
        return err(401, "Not authenticated.")
    try:
        body = await request.json()
    except Exception:
        return err(400, "Invalid JSON.")

    section_id = (body.get("section_id") or "").strip()
    if not section_id:
        return err(400, "section_id required.")

    await db.execute(
        "INSERT INTO sections (user_id, section_id) VALUES (?, ?) "
        "ON CONFLICT(user_id, section_id) DO UPDATE SET completed=1",
        (user_id, section_id),
    )
    return JSONResponse({"ok": True, "section_id": section_id})


async def unmark_complete(request: Request):
    user_id = require_user(request)
    if not user_id:
        return err(401, "Not authenticated.")

    section_id = request.path_params.get("section_id", "")
    await db.execute(
        "DELETE FROM sections WHERE user_id = ? AND section_id = ?",
        (user_id, section_id),
    )
    return JSONResponse({"ok": True})


routes = [
    Route("/", get_progress, methods=["GET"]),
    Route("/section/complete", mark_complete, methods=["POST"]),
    Route("/section/{section_id}", unmark_complete, methods=["DELETE"]),
]
