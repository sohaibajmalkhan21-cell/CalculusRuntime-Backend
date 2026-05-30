"""Auth router — signup, login, token, me."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import Optional

import aiosqlite
from db import get_db
from auth_utils import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user_id,
)

router = APIRouter()


class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=6, max_length=128)
    email: Optional[str] = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/signup", response_model=AuthResponse, status_code=201)
async def signup(body: SignupRequest, db: aiosqlite.Connection = Depends(get_db)):
    # Check username taken
    async with db.execute(
        "SELECT id FROM users WHERE username = ?", (body.username,)
    ) as cur:
        if await cur.fetchone():
            raise HTTPException(status_code=409, detail="Username already taken.")

    hashed = hash_password(body.password)
    async with db.execute(
        "INSERT INTO users (username, email, hashed_pw) VALUES (?, ?, ?)",
        (body.username, body.email, hashed),
    ) as cur:
        user_id = cur.lastrowid
    await db.commit()

    token = create_access_token({"sub": str(user_id)})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user_id, "username": body.username},
    }


@router.post("/token", response_model=AuthResponse)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: aiosqlite.Connection = Depends(get_db),
):
    async with db.execute(
        "SELECT id, username, hashed_pw FROM users WHERE username = ?", (form.username,)
    ) as cur:
        row = await cur.fetchone()

    if not row or not verify_password(form.password, row["hashed_pw"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )

    token = create_access_token({"sub": str(row["id"])})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": row["id"], "username": row["username"]},
    }


@router.post("/login", response_model=AuthResponse)
async def login_json(body: SignupRequest, db: aiosqlite.Connection = Depends(get_db)):
    """JSON login endpoint (easier for fetch calls)."""
    async with db.execute(
        "SELECT id, username, hashed_pw FROM users WHERE username = ?", (body.username,)
    ) as cur:
        row = await cur.fetchone()

    if not row or not verify_password(body.password, row["hashed_pw"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password.")

    token = create_access_token({"sub": str(row["id"])})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": row["id"], "username": row["username"]},
    }


@router.get("/me")
async def me(
    user_id: int = Depends(get_current_user_id),
    db: aiosqlite.Connection = Depends(get_db),
):
    async with db.execute(
        "SELECT id, username, email, created_at FROM users WHERE id = ?", (user_id,)
    ) as cur:
        row = await cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found.")
    return dict(row)
