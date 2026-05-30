"""
LoginScreen — View layer for the Login screen.

MVC role: This is the V. It renders the KV layout and
delegates all logic to AuthController (C).
"""

from kivy.uix.screenmanager import Screen
from kivy.animation import Animation
from kivy.metrics import dp


class LoginScreen(Screen):
    """
    Renders the login form and handles UI events.
    On successful auth it transitions to the Dashboard.
    """

    def on_enter(self, *args):
        """Called every time this screen becomes visible."""
        # Clear fields so back-button doesn't show stale input
        self.ids.username_input.text = ""
        self.ids.password_input.text = ""
        self._hide_error()

    def on_login(self):
        """
        Called by the Login button and keyboard Enter key.
        Delegates to AuthController and navigates on success.
        """
        app  = self._get_app()
        ctrl = app.auth_controller

        username = self.ids.username_input.text
        password = self.ids.password_input.text

        success, error_msg = ctrl.login(username, password)

        if success:
            self._hide_error()
            self.manager.current = "dashboard"
        else:
            self._show_error(error_msg)

    def go_to_signup(self) -> None:
        """Navigate to the signup screen."""
        self._hide_error()
        self.manager.current = "signup"

    # ------------------------------------------------------------------ #
    #  Error helpers                                                      #
    # ------------------------------------------------------------------ #

    def _show_error(self, message: str) -> None:
        error_box   = self.ids.error_box
        error_label = self.ids.error_label
        error_label.text = message
        # Animate the box open
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
