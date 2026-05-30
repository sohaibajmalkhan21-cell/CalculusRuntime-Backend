"""Bookmarks router."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

import aiosqlite
from db import get_db
from auth_utils import get_current_user_id

router = APIRouter()


class BookmarkBody(BaseModel):
    id: str
    title: str
    path: str


@router.get("/")
async def list_bookmarks(
    user_id: int = Depends(get_current_user_id),
    db: aiosqlite.Connection = Depends(get_db),
):
    async with db.execute(
        "SELECT bm_id, title, path, added_at FROM bookmarks WHERE user_id = ? ORDER BY added_at DESC",
        (user_id,),
    ) as cur:
        return [
            {
                "id": row["bm_id"],
                "title": row["title"],
                "path": row["path"],
                "addedAt": row["added_at"],
            }
            async for row in cur
        ]


@router.post("/", status_code=201)
async def add_bookmark(
    body: BookmarkBody,
    user_id: int = Depends(get_current_user_id),
    db: aiosqlite.Connection = Depends(get_db),
):
    await db.execute(
        """INSERT INTO bookmarks (user_id, bm_id, title, path) VALUES (?, ?, ?, ?)
           ON CONFLICT(user_id, bm_id) DO NOTHING""",
        (user_id, body.id, body.title, body.path),
    )
    await db.commit()
    return {"ok": True}


@router.delete("/{bm_id}")
async def remove_bookmark(
    bm_id: str,
    user_id: int = Depends(get_current_user_id),
    db: aiosqlite.Connection = Depends(get_db),
):
    await db.execute(
        "DELETE FROM bookmarks WHERE user_id = ? AND bm_id = ?",
        (user_id, bm_id),
    )
    await db.commit()
    return {"ok": True}
