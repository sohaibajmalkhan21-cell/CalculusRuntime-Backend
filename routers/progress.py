"""Progress router — completed sections, full progress snapshot."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

import aiosqlite
from db import get_db
from auth_utils import get_current_user_id

router = APIRouter()


class SectionBody(BaseModel):
    section_id: str


@router.get("/")
async def get_progress(
    user_id: int = Depends(get_current_user_id),
    db: aiosqlite.Connection = Depends(get_db),
):
    """Return full progress snapshot for the current user."""
    # Completed sections
    async with db.execute(
        "SELECT section_id, completed_at FROM sections WHERE user_id = ?", (user_id,)
    ) as cur:
        sections = {row["section_id"]: True async for row in cur}

    # Quiz scores
    async with db.execute(
        "SELECT quiz_id, score, total, taken_at FROM quiz_scores WHERE user_id = ?",
        (user_id,),
    ) as cur:
        quiz_scores = {
            row["quiz_id"]: {"score": row["score"], "total": row["total"]}
            async for row in cur
        }

    # Bookmarks
    async with db.execute(
        "SELECT bm_id, title, path, added_at FROM bookmarks WHERE user_id = ? ORDER BY added_at DESC",
        (user_id,),
    ) as cur:
        bookmarks = [
            {
                "id": row["bm_id"],
                "title": row["title"],
                "path": row["path"],
                "addedAt": row["added_at"],
            }
            async for row in cur
        ]

    # Solver history count
    async with db.execute(
        "SELECT COUNT(*) as cnt FROM solver_history WHERE user_id = ?", (user_id,)
    ) as cur:
        row = await cur.fetchone()
        solver_count = row["cnt"] if row else 0

    return {
        "completedSections": sections,
        "quizScores": quiz_scores,
        "bookmarks": bookmarks,
        "solverUses": solver_count,
    }


@router.post("/section/complete")
async def mark_complete(
    body: SectionBody,
    user_id: int = Depends(get_current_user_id),
    db: aiosqlite.Connection = Depends(get_db),
):
    await db.execute(
        """INSERT INTO sections (user_id, section_id) VALUES (?, ?)
           ON CONFLICT(user_id, section_id) DO UPDATE SET completed=1""",
        (user_id, body.section_id),
    )
    await db.commit()
    return {"ok": True, "section_id": body.section_id}


@router.delete("/section/{section_id}")
async def unmark_complete(
    section_id: str,
    user_id: int = Depends(get_current_user_id),
    db: aiosqlite.Connection = Depends(get_db),
):
    await db.execute(
        "DELETE FROM sections WHERE user_id = ? AND section_id = ?",
        (user_id, section_id),
    )
    await db.commit()
    return {"ok": True}


@router.get("/sections")
async def get_completed_sections(
    user_id: int = Depends(get_current_user_id),
    db: aiosqlite.Connection = Depends(get_db),
):
    async with db.execute(
        "SELECT section_id, completed_at FROM sections WHERE user_id = ?", (user_id,)
    ) as cur:
        return {row["section_id"]: True async for row in cur}
