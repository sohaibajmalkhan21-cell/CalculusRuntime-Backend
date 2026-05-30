"""Quiz scores router."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

import aiosqlite
from db import get_db
from auth_utils import get_current_user_id

router = APIRouter()


class QuizScoreBody(BaseModel):
    quiz_id: str
    score: int
    total: int


@router.get("/")
async def list_scores(
    user_id: int = Depends(get_current_user_id),
    db: aiosqlite.Connection = Depends(get_db),
):
    async with db.execute(
        "SELECT quiz_id, score, total, taken_at FROM quiz_scores WHERE user_id = ? ORDER BY taken_at DESC",
        (user_id,),
    ) as cur:
        return {
            row["quiz_id"]: {"score": row["score"], "total": row["total"]}
            async for row in cur
        }


@router.post("/", status_code=201)
async def save_score(
    body: QuizScoreBody,
    user_id: int = Depends(get_current_user_id),
    db: aiosqlite.Connection = Depends(get_db),
):
    # Only update if new score is better
    await db.execute(
        """INSERT INTO quiz_scores (user_id, quiz_id, score, total) VALUES (?, ?, ?, ?)
           ON CONFLICT(user_id, quiz_id) DO UPDATE SET
             score = CASE WHEN excluded.score > score THEN excluded.score ELSE score END,
             total = excluded.total,
             taken_at = strftime('%s','now')""",
        (user_id, body.quiz_id, body.score, body.total),
    )
    await db.commit()
    return {"ok": True}
