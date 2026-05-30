"""
ProfileScreen — View layer for the Profile / Settings screen.

MVC role: This is the V.
Displays user info from AppState, handles logout via AuthController.
"""

from kivy.uix.screenmanager import Screen


class ProfileScreen(Screen):
    """Shows user profile, preferences toggles, and logout button."""

    def on_enter(self, *args):
        """Refresh user info from AppState each time screen opens."""
        app  = _app()
        user = app.state.current_user

        if user:
            name = user.display_name or user.username
            initials = "".join(p[0].upper() for p in name.split()[:2])
            self.ids.display_name_label.text = name
            self.ids.username_label.text     = user.username
            self.ids.avatar_label.text       = initials or "??"
        else:
            self.ids.display_name_label.text = "Guest"
            self.ids.username_label.text     = ""
            self.ids.avatar_label.text       = "G"

        # Sync notification switch to AppState
        self.ids.notif_switch.active = app.state.notifications_enabled
        self.ids.dark_switch.active = app.state.dark_mode_enabled
        app.apply_theme(app.state.dark_mode_enabled)

    def on_toggle_notifications(self, active: bool) -> None:
        """Persist notification preference to AppState."""
        _app().state.notifications_enabled = active

    def on_toggle_theme(self, active: bool) -> None:
        """Toggle light/dark mode for the app."""
        app = _app()
        app.state.dark_mode_enabled = active
        app.apply_theme(active)
        if "tasks" in app.root.screen_names:
            app.root.get_screen("tasks")._build_filter_pills()
            app.root.get_screen("tasks").refresh_tasks()
        if "add_task" in app.root.screen_names:
            app.root.get_screen("add_task")._build_priority_buttons()

    def on_logout(self) -> None:
        """Clear session and navigate back to login."""
        app = _app()
        app.auth_controller.logout()
        # Clear inputs on the login screen
        login = app.root.get_screen("login")
        app.root.current = "login"

    def go_to_dashboard(self) -> None:
        _app().root.current = "dashboard"

    def go_to_tasks(self) -> None:
        app = _app()
        app.root.current = "tasks"
        app.root.get_screen("tasks").refresh_tasks()


def _app():
    from kivy.app import App
    return App.get_running_app()
