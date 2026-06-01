# API Reference

## Table of Contents

- [Conventions](#conventions)
- [System](#system)
- [Auth](#auth)
- [Progress](#progress)
- [Bookmarks](#bookmarks)
- [Quiz Scores](#quiz-scores)
- [Solver History](#solver-history)
- [Common Errors](#common-errors)

## Conventions

Base URL in local development:

```text
http://127.0.0.1:8002
```

Protected routes use:

```http
Authorization: Bearer <access_token>
```

Error payloads generally use:

```json
{ "detail": "Message." }
```

## System

### `GET /`

Returns service metadata and an endpoint index.

### `GET /docs`

Returns the custom HTML API documentation page.

### `GET /api/health`

Response:

```json
{ "status": "ok" }
```

## Auth

### `POST /api/auth/signup`

Creates a user and returns a bearer token.

Request:

```json
{
  "username": "ada",
  "password": "secret123",
  "email": "ada@example.com"
}
```

Validation:

- `username` must be at least 3 characters.
- `password` must be at least 6 characters.
- `email` is optional.

Response `201`:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user": { "id": 1, "username": "ada" }
}
```

### `POST /api/auth/login`

Authenticates an existing user.

Request:

```json
{
  "username": "ada",
  "password": "secret123"
}
```

Response `200`:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user": { "id": 1, "username": "ada" }
}
```

### `GET /api/auth/me`

Requires auth. Returns the current user profile.

Response:

```json
{
  "id": 1,
  "username": "ada",
  "email": "ada@example.com",
  "created_at": 1710000000
}
```

## Progress

### `GET /api/progress/`

Requires auth. Returns the current user's learning snapshot.

Response:

```json
{
  "completedSections": { "partial-1": true },
  "quizScores": {
    "partial-1-mcq": { "score": 2, "total": 3 }
  },
  "bookmarks": [
    {
      "id": "partial-1",
      "title": "Partial derivatives",
      "path": "/partial-derivatives/1",
      "addedAt": 1710000000
    }
  ],
  "solverUses": 1
}
```

### `POST /api/progress/section/complete`

Requires auth. Marks a section complete.

Request:

```json
{ "section_id": "partial-1" }
```

Response:

```json
{ "ok": true, "section_id": "partial-1" }
```

### `DELETE /api/progress/section/{section_id}`

Requires auth. Removes a completed section marker.

Response:

```json
{ "ok": true }
```

## Bookmarks

### `GET /api/bookmarks/`

Requires auth. Returns bookmarks in newest-first order.

### `POST /api/bookmarks/`

Requires auth. Adds a bookmark if it does not already exist.

Request:

```json
{
  "id": "vector-1",
  "title": "Vector calculus",
  "path": "/vector-calculus/1"
}
```

Response `201`:

```json
{ "ok": true }
```

### `DELETE /api/bookmarks/{bm_id}`

Requires auth. Removes a bookmark.

Response:

```json
{ "ok": true }
```

## Quiz Scores

### `GET /api/quiz/`

Requires auth. Returns scores keyed by quiz id.

```json
{
  "partial-1-mcq": { "score": 2, "total": 3 }
}
```

### `POST /api/quiz/`

Requires auth. Saves a score. Existing SQLite scores keep the best score and update `total` and `taken_at`.

Request:

```json
{
  "quiz_id": "partial-1-mcq",
  "score": 2,
  "total": 3
}
```

Response `201`:

```json
{ "ok": true }
```

## Solver History

### `POST /api/solver/log`

Auth is optional. If a valid user token is present, the use is stored; otherwise the route still returns success.

Request:

```json
{
  "expression": "d/dx x^2",
  "result": "2x"
}
```

Response:

```json
{ "ok": true }
```

### `GET /api/solver/history`

Returns the last 50 solver history rows for an authenticated user. If no valid token is present, the current implementation returns an empty list.

## Common Errors

| Status | Meaning |
| --- | --- |
| `400` | Invalid JSON or missing required fields |
| `401` | Missing/invalid authentication |
| `404` | Authenticated user no longer exists |
| `409` | Username already taken |
| `500` | Storage/configuration error |
