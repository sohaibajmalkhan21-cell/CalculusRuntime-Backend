# Backend Documentation

This folder documents the `backend/` subproject only.

## Purpose

The backend is the CalcVoyager persistence API. It handles:

- User signup, login, and current-user lookup.
- Learning progress.
- Bookmarks.
- Quiz scores.
- Solver usage logging.

## Stack

- Starlette
- Uvicorn
- SQLite through Python stdlib `sqlite3`
- PyJWT
- bcrypt

## Main Folders

| Path | Purpose |
| --- | --- |
| `main.py` | Starlette app, CORS, startup, embedded API docs |
| `db.py` | SQLite schema and async wrappers around blocking DB calls |
| `auth_utils.py` | Password hashing, JWT creation/verification, auth helpers |
| `routers/` | Route handlers for auth, progress, bookmarks, quiz, solver history |
| `calcvoyager.db` | Local SQLite database, generated/runtime data |

## API Surface

| Area | Routes |
| --- | --- |
| Health | `GET /api/health` |
| Auth | `POST /api/auth/signup`, `POST /api/auth/login`, `GET /api/auth/me` |
| Progress | `GET /api/progress/`, `POST /api/progress/section/complete`, `DELETE /api/progress/section/{section_id}` |
| Bookmarks | `GET /api/bookmarks/`, `POST /api/bookmarks/`, `DELETE /api/bookmarks/{bm_id}` |
| Quiz | `GET /api/quiz/`, `POST /api/quiz/` |
| Solver history | `POST /api/solver/log`, `GET /api/solver/history` |

## Local Commands

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```

The frontend currently defaults to `http://127.0.0.1:8002`, so port `8002` is the safest local backend port unless the frontend environment is changed.

## Environment Variables

```env
SECRET_KEY=replace-with-a-long-random-string
TOKEN_EXPIRE_MINUTES=10080
DB_PATH=calcvoyager.db
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Security Notes

- `SECRET_KEY` must be set before real deployment.
- The current code has a development fallback secret. That is acceptable only for local prototypes.
- CORS should be narrowed for production.
- JWTs are bearer tokens; frontend token storage choices affect XSS risk.

## Data Model

| Table | Purpose |
| --- | --- |
| `users` | User account records |
| `sections` | Completed guide sections per user |
| `bookmarks` | Saved guide/tool links per user |
| `quiz_scores` | Best quiz scores per user |
| `solver_history` | Solver usage history per user |

## Current Technical Debt

- Input validation is manual and inconsistent between routes.
- Quiz score casting should return validation errors instead of possible 500s.
- Frontend progress code does not yet use most backend progress APIs.
- Local runtime artifacts such as DB files and Python cache files should stay out of version control.

## Current Worktree Warning

At the time these docs were added, the backend submodule had an interactive rebase/conflict state. Avoid resolving or aborting that rebase unless you intentionally own that Git operation.

## Recommended Next Docs

- `docs/API_CONTRACT.md`: exact request and response examples for every route.
- `docs/ENVIRONMENT.md`: required local and production environment variables.
- `docs/TESTING.md`: backend smoke and route test instructions.
