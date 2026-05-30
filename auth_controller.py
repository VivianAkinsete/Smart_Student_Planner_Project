"""
Auth Controller — handles login and logout logic.

MVC role: This is the C for authentication.
Calls UserManager (Model) and updates AppState.
Never touches Kivy widgets directly.
"""

from models.user import UserManager
from controllers.app_state import AppState
from typing import Tuple


class AuthController:
    """Mediates between the Login/Settings views and the User model."""

    def __init__(self, state: AppState):
        self._state        = state
        self._user_manager = UserManager()

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Attempt authentication.

        Returns
        -------
        (True, "")          on success — AppState.current_user is set.
        (False, error_msg)  on failure.
        """
        if not username.strip():
            return False, "Please enter your username."
        if not password.strip():
            return False, "Please enter your password."

        user = self._user_manager.authenticate(username, password)
        if user:
            self._state.current_user = user
            return True, ""
        return False, "Incorrect username or password. Please try again."

    def logout(self) -> None:
        """Clear all session state."""
        self._state.reset()

    def signup(self, username: str, password: str, confirm_password: str,
               display_name: str) -> Tuple[bool, str]:
        """
        Create a new user and log them in.
        Returns (True, "") on success or (False, error_msg) on failure.
        """
        if password.strip() != confirm_password.strip():
            return False, "Passwords do not match."

        user, error = self._user_manager.create_user(username, password, display_name)
        if user:
            self._state.current_user = user
            return True, ""
        return False, error
