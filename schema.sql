-- ============================================================
--  PyBridge Pro — SQLite Database Schema
--  File: schema.sql
--  Database: pybridge.db
--  Created: 2024
-- ============================================================


-- ============================================================
--  TABLE 1: notes
--  Stores user-created notes with title, content, category
-- ============================================================

CREATE TABLE IF NOT EXISTS notes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,   -- Unique note ID
    title       TEXT    NOT NULL,                    -- Note title
    content     TEXT    NOT NULL,                    -- Note body/content
    category    TEXT    DEFAULT 'General',           -- General | Work | Personal
    created_at  TEXT    DEFAULT (datetime('now')),   -- Auto timestamp on insert
    updated_at  TEXT    DEFAULT (datetime('now'))    -- Auto timestamp on update
);


-- ============================================================
--  TABLE 2: todos
--  Stores tasks with priority and completion status
-- ============================================================

CREATE TABLE IF NOT EXISTS todos (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,   -- Unique todo ID
    task        TEXT    NOT NULL,                    -- Task description
    completed   INTEGER DEFAULT 0,                  -- 0 = pending, 1 = done
    priority    TEXT    DEFAULT 'Medium',            -- Low | Medium | High
    created_at  TEXT    DEFAULT (datetime('now'))    -- Auto timestamp on insert
);


-- ============================================================
--  TABLE 3: short_urls
--  Stores original URLs and their generated short codes
-- ============================================================

CREATE TABLE IF NOT EXISTS short_urls (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique URL ID
    original_url TEXT    NOT NULL,                   -- Full original URL
    short_code   TEXT    UNIQUE NOT NULL,            -- 6-char unique code
    clicks       INTEGER DEFAULT 0,                 -- Click counter
    created_at   TEXT    DEFAULT (datetime('now'))   -- Auto timestamp on insert
);


-- ============================================================
--  TABLE 4: api_logs
--  Auto-logs every API request (endpoint + method)
-- ============================================================

CREATE TABLE IF NOT EXISTS api_logs (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,    -- Unique log ID
    endpoint   TEXT    NOT NULL,                     -- e.g. /notes, /todos
    method     TEXT    NOT NULL,                     -- GET | POST | PUT | DELETE
    called_at  TEXT    DEFAULT (datetime('now'))     -- Auto timestamp
);


-- ============================================================
--  INDEXES — Speed up common queries
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_notes_category   ON notes     (category);
CREATE INDEX IF NOT EXISTS idx_notes_created    ON notes     (created_at);
CREATE INDEX IF NOT EXISTS idx_todos_completed  ON todos     (completed);
CREATE INDEX IF NOT EXISTS idx_todos_priority   ON todos     (priority);
CREATE INDEX IF NOT EXISTS idx_urls_short_code  ON short_urls(short_code);
CREATE INDEX IF NOT EXISTS idx_urls_original    ON short_urls(original_url);
CREATE INDEX IF NOT EXISTS idx_logs_endpoint    ON api_logs  (endpoint);
CREATE INDEX IF NOT EXISTS idx_logs_called_at   ON api_logs  (called_at);


-- ============================================================
--  SAMPLE DATA — Optional test records
-- ============================================================

-- Sample Notes
INSERT INTO notes (title, content, category) VALUES
    ('Welcome to PyBridge', 'This is your first note. You can create, edit, and delete notes.', 'General'),
    ('AWS Deployment', 'Deploy using EC2 t2.micro + Nginx + PM2 + Certbot for HTTPS.', 'Work'),
    ('Shopping List', 'Milk, Eggs, Bread, Coffee', 'Personal');

-- Sample Todos
INSERT INTO todos (task, priority, completed) VALUES
    ('Set up EC2 instance on AWS', 'High', 0),
    ('Configure Nginx reverse proxy', 'High', 0),
    ('Enable HTTPS with Certbot', 'Medium', 0),
    ('Test all API endpoints', 'Medium', 1),
    ('Read the README.md', 'Low', 1);

-- Sample Short URLs
INSERT INTO short_urls (original_url, short_code, clicks) VALUES
    ('https://www.google.com', 'ggl001', 5),
    ('https://fastapi.tiangolo.com', 'fapi01', 12),
    ('https://aws.amazon.com/ec2', 'ec2aws', 3);


-- ============================================================
--  USEFUL QUERIES
-- ============================================================

-- View all notes:
-- SELECT * FROM notes ORDER BY created_at DESC;

-- View pending todos:
-- SELECT * FROM todos WHERE completed = 0 ORDER BY priority;

-- View completed todos:
-- SELECT * FROM todos WHERE completed = 1;

-- View all short URLs with click count:
-- SELECT short_code, original_url, clicks FROM short_urls ORDER BY clicks DESC;

-- View top 5 most called endpoints:
-- SELECT endpoint, COUNT(*) as hits FROM api_logs
-- GROUP BY endpoint ORDER BY hits DESC LIMIT 5;

-- View API calls today:
-- SELECT * FROM api_logs WHERE DATE(called_at) = DATE('now');

-- Count records in each table:
-- SELECT 'notes' as tbl, COUNT(*) as total FROM notes
-- UNION ALL SELECT 'todos', COUNT(*) FROM todos
-- UNION ALL SELECT 'short_urls', COUNT(*) FROM short_urls
-- UNION ALL SELECT 'api_logs', COUNT(*) FROM api_logs;
