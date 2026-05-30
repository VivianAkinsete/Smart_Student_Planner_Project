"""
Model layer — User dataclass and UserManager.

MVC role: This is the M for user/auth data.
"""

from dataclasses import dataclass
from typing import Optional, Tuple
import sqlite3
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.database import get_connection


@dataclass
class User:
    id:           int = 0
    username:     str = ""
    display_name: str = ""


class UserManager:
    """Handles user lookup and credential verification."""

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Verify credentials. Returns a User on success, None on failure.
        In a real app, passwords would be hashed (e.g. bcrypt).
        Plain text is used here for simplicity as per academic scope.
        """
        if not username.strip() or not password.strip():
            return None
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username.strip(), password.strip()),
        ).fetchone()
        conn.close()
        if row:
            return User(id=row["id"], username=row["username"],
                        display_name=row["display_name"])
        return None

    def create_user(self, username: str, password: str, display_name: str) -> Tuple[Optional[User], str]:
        """
        Create a new user account.
        Returns (User, "") on success, (None, error_msg) on failure.
        """
        username = username.strip()
        password = password.strip()
        display_name = display_name.strip()

        if not username:
            return None, "Please enter a username."
        if not password:
            return None, "Please enter a password."
        if not display_name:
            display_name = username

        conn = get_connection()
        try:
            cursor = conn.execute(
                "INSERT INTO users (username, password, display_name) VALUES (?, ?, ?)",
                (username, password, display_name),
            )
            conn.commit()
            user_id = cursor.lastrowid
            return User(id=user_id, username=username, display_name=display_name), ""
        except sqlite3.IntegrityError:
            return None, "That username is already taken."
        finally:
            conn.close()

    def update_display_name(self, user_id: int, name: str) -> bool:
        """Update user's display name. Returns True on success."""
        conn = get_connection()
        cursor = conn.execute(
            "UPDATE users SET display_name = ? WHERE id = ?", (name.strip(), user_id)
        )
        conn.commit()
        ok = cursor.rowcount > 0
        conn.close()
        return ok
