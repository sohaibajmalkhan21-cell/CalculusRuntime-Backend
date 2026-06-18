-- ============================================
-- ORIGINAL SUPABASE TABLES (WERE ALREADY THERE)
-- ============================================

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id          SERIAL PRIMARY KEY,
    username    TEXT    UNIQUE NOT NULL,
    email       TEXT    UNIQUE,
    hashed_pw   TEXT    NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sections Table (Progress Tracking)
CREATE TABLE IF NOT EXISTS sections (
    id           SERIAL PRIMARY KEY,
    user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    section_id   TEXT    NOT NULL,
    completed    BOOLEAN DEFAULT true,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, section_id)
);

-- Bookmarks Table
CREATE TABLE IF NOT EXISTS bookmarks (
    id        SERIAL PRIMARY KEY,
    user_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    bm_id     TEXT    NOT NULL,
    title     TEXT    NOT NULL,
    path      TEXT    NOT NULL,
    added_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, bm_id)
);

-- Quiz Scores Table
CREATE TABLE IF NOT EXISTS quiz_scores (
    id        SERIAL PRIMARY KEY,
    user_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    quiz_id   TEXT    NOT NULL,
    score     INTEGER NOT NULL,
    total     INTEGER NOT NULL,
    taken_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, quiz_id)
);

-- Solver History Table
CREATE TABLE IF NOT EXISTS solver_history (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    expression TEXT,
    result     TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- NEW CHAT TABLES (ADDED BY SOHAIB)
-- ============================================

-- Chat Sessions Table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id  TEXT    UNIQUE NOT NULL,
    title       TEXT    DEFAULT 'New Chat',
    is_active   BOOLEAN DEFAULT true,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat Messages Table
CREATE TABLE IF NOT EXISTS chat_messages (
    id           SERIAL PRIMARY KEY,
    user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id   TEXT    NOT NULL REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    message_type TEXT    NOT NULL CHECK (message_type IN ('user', 'assistant', 'system')),
    content      TEXT    NOT NULL,
    metadata     JSONB   DEFAULT '{}',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_session ON chat_messages(user_id, session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_active ON chat_sessions(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_updated ON chat_sessions(user_id, updated_at DESC);