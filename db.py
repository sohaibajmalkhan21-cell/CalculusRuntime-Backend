"""
SQLite database — single file, zero config.
Tables: users, sections, bookmarks, quiz_scores, solver_history
"""

import aiosqlite
import os

DB_PATH = os.getenv("DB_PATH", "calcvoyager.db")


async def get_db():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(
            """
            PRAGMA journal_mode=WAL;

            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT    UNIQUE NOT NULL,
                email       TEXT    UNIQUE,
                hashed_pw   TEXT    NOT NULL,
                created_at  INTEGER NOT NULL DEFAULT (strftime('%s','now'))
            );

            CREATE TABLE IF NOT EXISTS sections (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                section_id  TEXT    NOT NULL,
                completed   INTEGER NOT NULL DEFAULT 1,
                completed_at INTEGER NOT NULL DEFAULT (strftime('%s','now')),
                UNIQUE(user_id, section_id)
            );

            CREATE TABLE IF NOT EXISTS bookmarks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                bm_id       TEXT    NOT NULL,
                title       TEXT    NOT NULL,
                path        TEXT    NOT NULL,
                added_at    INTEGER NOT NULL DEFAULT (strftime('%s','now')),
                UNIQUE(user_id, bm_id)
            );

            CREATE TABLE IF NOT EXISTS quiz_scores (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                quiz_id     TEXT    NOT NULL,
                score       INTEGER NOT NULL,
                total       INTEGER NOT NULL,
                taken_at    INTEGER NOT NULL DEFAULT (strftime('%s','now')),
                UNIQUE(user_id, quiz_id)
            );

            CREATE TABLE IF NOT EXISTS solver_history (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                expression  TEXT,
                result      TEXT,
                created_at  INTEGER NOT NULL DEFAULT (strftime('%s','now'))
            );
        """
        )
        await db.commit()
