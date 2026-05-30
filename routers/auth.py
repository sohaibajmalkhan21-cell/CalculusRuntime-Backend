"""Auth routes — signup, login, me."""

from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import JSONResponse

import db
from auth_utils import hash_password, verify_password, create_token, require_user, err


async def signup(request: Request):
    try:
        body = await request.json()
    except Exception:
        return err(400, "Invalid JSON.")

    username = (body.get("username") or "").strip()
    password = body.get("password") or ""
    email = body.get("email") or None

    if len(username) < 3:
        return err(400, "Username must be at least 3 characters.")
    if len(password) < 6:
        return err(400, "Password must be at least 6 characters.")

    existing = await db.fetchone("SELECT id FROM users WHERE username = ?", (username,))
    if existing:
        return err(409, "Username already taken.")

    hashed = hash_password(password)
    user_id = await db.execute(
        "INSERT INTO users (username, email, hashed_pw) VALUES (?, ?, ?)",
        (username, email, hashed),
    )
    token = create_token(user_id)
    return JSONResponse(
        {
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": user_id, "username": username},
        },
        status_code=201,
    )


async def login(request: Request):
    try:
        body = await request.json()
    except Exception:
        return err(400, "Invalid JSON.")

    username = (body.get("username") or "").strip()
    password = body.get("password") or ""

    row = await db.fetchone(
        "SELECT id, username, hashed_pw FROM users WHERE username = ?", (username,)
    )
    if not row or not verify_password(password, row["hashed_pw"]):
        return err(401, "Incorrect username or password.")

    token = create_token(row["id"])
    return JSONResponse(
        {
            "access_token": token,
            "token_type": "bearer",
            "user": {"id": row["id"], "username": row["username"]},
        }
    )


async def me(request: Request):
    user_id = require_user(request)
    if not user_id:
        return err(401, "Not authenticated.")
    row = await db.fetchone(
        "SELECT id, username, email, created_at FROM users WHERE id = ?", (user_id,)
    )
    if not row:
        return err(404, "User not found.")
    return JSONResponse(row)


routes = [
    Route("/signup", signup, methods=["POST"]),
    Route("/login", login, methods=["POST"]),
    Route("/me", me, methods=["GET"]),
]
