"""
Model layer — Task dataclass and TaskManager repository.

MVC role: This is the M. It knows nothing about the UI.
All database access for tasks goes through TaskManager.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.database import get_connection

VALID_PRIORITIES = ("High", "Medium", "Low")


@dataclass
class Task:
    """Represents a single student task."""
    id:          int  = 0
    user_id:     int  = 0
    title:       str  = ""
    module:      str  = ""
    due_date:    str  = ""          # ISO format YYYY-MM-DD
    priority:    str  = "Medium"
    notes:       str  = ""
    is_complete: bool = False
    created_at:  str  = ""

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "user_id":     self.user_id,
            "title":       self.title,
            "module":      self.module,
            "due_date":    self.due_date,
            "priority":    self.priority,
            "notes":       self.notes,
            "is_complete": int(self.is_complete),
        }

    @staticmethod
    def from_row(row) -> "Task":
        """Construct a Task from a sqlite3.Row."""
        return Task(
            id          = row["id"],
            user_id     = row["user_id"],
            title       = row["title"],
            module      = row["module"]      or "",
            due_date    = row["due_date"]    or "",
            priority    = row["priority"]    or "Medium",
            notes       = row["notes"]       or "",
            is_complete = bool(row["is_complete"]),
            created_at  = row["created_at"]  or "",
        )


class TaskManager:
    """
    Repository for Task CRUD operations.
    All methods return Task objects or lists — never raw DB rows.
    """

    # ------------------------------------------------------------------ #
    #  Read operations                                                     #
    # ------------------------------------------------------------------ #

    def get_all(self, user_id: int) -> List[Task]:
        """Return all tasks ordered by priority then due date."""
        priority_order = "CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END"
        conn = get_connection()
        rows = conn.execute(
            f"SELECT * FROM tasks WHERE user_id = ? ORDER BY {priority_order}, due_date ASC",
            (user_id,),
        ).fetchall()
        conn.close()
        return [Task.from_row(r) for r in rows]

    def get_by_id(self, user_id: int, task_id: int) -> Optional[Task]:
        """Return a single task or None if not found."""
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id),
        ).fetchone()
        conn.close()
        return Task.from_row(row) if row else None

    def search(self, user_id: int, keyword: str) -> List[Task]:
        """Case-insensitive search across title, module, and notes."""
        kw = f"%{keyword.strip()}%"
        conn = get_connection()
        rows = conn.execute(
            """SELECT * FROM tasks
               WHERE user_id = ?
                 AND (LOWER(title) LIKE LOWER(?)
                   OR LOWER(module) LIKE LOWER(?)
                   OR LOWER(notes) LIKE LOWER(?))
                ORDER BY due_date ASC""",
            (user_id, kw, kw, kw),
        ).fetchall()
        conn.close()
        return [Task.from_row(r) for r in rows]

    def filter_by_priority(self, user_id: int, priority: str) -> List[Task]:
        """Return tasks filtered by a specific priority label."""
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM tasks WHERE user_id = ? AND priority = ? ORDER BY due_date ASC",
            (user_id, priority),
        ).fetchall()
        conn.close()
        return [Task.from_row(r) for r in rows]

    # ------------------------------------------------------------------ #
    #  Write operations                                                    #
    # ------------------------------------------------------------------ #

    def add(self, user_id: int, title: str, module: str, due_date: str,
            priority: str, notes: str) -> Task:
        """
        Insert a new task and return the created Task with its new id.
        Raises ValueError if validation fails.
        """
        errors = self._validate(title, due_date, priority)
        if errors:
            raise ValueError("; ".join(errors))

        conn = get_connection()
        cursor = conn.execute(
            """INSERT INTO tasks (user_id, title, module, due_date, priority, notes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, title.strip(), module.strip(), due_date.strip(), priority, notes.strip()),
        )
        conn.commit()
        task_id = cursor.lastrowid
        conn.close()
        return self.get_by_id(user_id, task_id)

    def update(self, user_id: int, task_id: int, title: str, module: str, due_date: str,
               priority: str, notes: str) -> Task:
        """
        Update an existing task. Raises ValueError on validation failure
        or KeyError if task_id doesn't exist.
        """
        if not self.get_by_id(user_id, task_id):
            raise KeyError(f"Task {task_id} not found.")
        errors = self._validate(title, due_date, priority)
        if errors:
            raise ValueError("; ".join(errors))

        conn = get_connection()
        conn.execute(
            """UPDATE tasks
               SET title=?, module=?, due_date=?, priority=?, notes=?
               WHERE id=? AND user_id=?""",
            (title.strip(), module.strip(), due_date.strip(), priority, notes.strip(), task_id, user_id),
        )
        conn.commit()
        conn.close()
        return self.get_by_id(user_id, task_id)

    def delete(self, user_id: int, task_id: int) -> bool:
        """Delete a task by id. Returns True if a row was deleted."""
        conn = get_connection()
        cursor = conn.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted

    def set_complete(self, user_id: int, task_id: int, complete: bool) -> bool:
        """Toggle the is_complete flag. Returns True on success."""
        conn = get_connection()
        cursor = conn.execute(
            "UPDATE tasks SET is_complete = ? WHERE id = ? AND user_id = ?",
            (int(complete), task_id, user_id),
        )
        conn.commit()
        ok = cursor.rowcount > 0
        conn.close()
        return ok

    # ------------------------------------------------------------------ #
    #  Validation                                                          #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _validate(title: str, due_date: str, priority: str) -> List[str]:
        """Return a list of error strings (empty = valid)."""
        errors = []
        if not title or not title.strip():
            errors.append("Title is required.")
        if due_date and due_date.strip():
            import re
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", due_date.strip()):
                errors.append("Due date must be in YYYY-MM-DD format.")
        if priority not in VALID_PRIORITIES:
            errors.append(f"Priority must be one of: {', '.join(VALID_PRIORITIES)}.")
        return errors
