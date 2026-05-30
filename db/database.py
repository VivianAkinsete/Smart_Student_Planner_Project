import sqlite3
import os

# Store DB alongside this file so path is always predictable
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "planner.db")


def get_connection() -> sqlite3.Connection:
    """Return a new SQLite connection with row_factory for dict-like access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows accessible by column name
    return conn


def init_db() -> None:
    """
    Create tables if they don't exist and seed a default user.
    Called once at app startup from main.py.
    """
    conn = get_connection()
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL,
            display_name TEXT DEFAULT ''
        )
    """)

    # Tasks table — stores all task fields from the brief
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            title       TEXT    NOT NULL,
            module      TEXT    DEFAULT '',
            due_date    TEXT    DEFAULT '',
            priority    TEXT    DEFAULT 'Medium',
            notes       TEXT    DEFAULT '',
            is_complete INTEGER DEFAULT 0,
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)

    # Ensure tasks table has user_id column (migration for older DBs)
    c.execute("PRAGMA table_info(tasks)")
    columns = [row[1] for row in c.fetchall()]
    if "user_id" not in columns:
        c.execute("ALTER TABLE tasks ADD COLUMN user_id INTEGER DEFAULT 0")

    # Seed default test user (INSERT OR IGNORE prevents duplicates on re-init)
    c.execute(
        "INSERT OR IGNORE INTO users (username, password, display_name) VALUES (?, ?, ?)",
        ("Vivian Akinsete", "password123", "Vivian Akinsete"),
    )
    c.execute("SELECT id FROM users WHERE username = ?", ("Vivian Akinsete",))
    default_user_id = c.fetchone()[0]

    # Backfill any existing tasks without user_id
    c.execute("UPDATE tasks SET user_id = ? WHERE user_id IS NULL OR user_id = 0", (default_user_id,))

    # Seed sample tasks for default user so dashboard isn't empty on first run
    c.execute("SELECT COUNT(*) FROM tasks WHERE user_id = ?", (default_user_id,))
    if c.fetchone()[0] == 0:
        sample_tasks = [
            (default_user_id, "History Essay Draft",  "World History",   "2024-10-24", "High",   "Draft intro and first two sections", 0),
            (default_user_id, "Math Problem Set 4",   "Calculus",        "2024-10-25", "Medium", "Problems 1–20 from Chapter 4",       0),
            (default_user_id, "Read Chapter 3",       "Biology",         "2024-10-26", "Low",    "Focus on cell division diagrams",    0),
        ]
        c.executemany(
            "INSERT INTO tasks (user_id, title, module, due_date, priority, notes, is_complete) VALUES (?,?,?,?,?,?,?)",
            sample_tasks,
        )

    conn.commit()
    conn.close()
