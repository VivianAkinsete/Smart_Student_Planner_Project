"""
SignupScreen — View layer for the Sign Up screen.
"""

from kivy.uix.screenmanager import Screen
from kivy.animation import Animation
from kivy.metrics import dp


class SignupScreen(Screen):
    """Renders the signup form and handles UI events."""

    def on_enter(self, *args):
        """Clear fields and errors whenever this screen opens."""
        self.ids.username_input.text = ""
        self.ids.display_name_input.text = ""
        self.ids.password_input.text = ""
        self.ids.confirm_input.text = ""
        self._hide_error()

    def on_signup(self) -> None:
        """Create a new account and navigate to the dashboard on success."""
        app = self._get_app()
        ctrl = app.auth_controller

        username = self.ids.username_input.text
        display_name = self.ids.display_name_input.text
        password = self.ids.password_input.text
        confirm = self.ids.confirm_input.text

        success, error_msg = ctrl.signup(username, password, confirm, display_name)
        if success:
            self._hide_error()
            self.manager.current = "dashboard"
        else:
            self._show_error(error_msg)

    def go_to_login(self) -> None:
        """Return to login screen."""
        self._hide_error()
        self.manager.current = "login"

    # ------------------------------------------------------------------ #
    #  Error helpers                                                      #
    # ------------------------------------------------------------------ #

    def _show_error(self, message: str) -> None:
        error_box = self.ids.error_box
        error_label = self.ids.error_label
        error_label.text = message
        Animation(height=dp(52), opacity=1, duration=0.2).start(error_box)

    def _hide_error(self) -> None:
        error_box = self.ids.error_box
        Animation(height=dp(0), opacity=0, duration=0.15).start(error_box)

    # ------------------------------------------------------------------ #
    #  Utility                                                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _get_app():
        from kivy.app import App
        return App.get_running_app()
