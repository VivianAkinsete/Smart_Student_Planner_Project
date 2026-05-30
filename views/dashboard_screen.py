"""
DashboardScreen — View layer for the Dashboard.

MVC role: This is the V.
DashboardScreen reads from TaskController (C) and renders task cards.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.metrics import dp
from views.task_card import TaskCard

class DashboardScreen(Screen):
    """Home screen. Shows important and upcoming tasks."""

    def on_enter(self, *args):
        """Refresh content every time the user navigates here."""
        self._update_greeting()
        self.refresh_tasks()

    # ------------------------------------------------------------------ #
    #  Greeting                                                           #
    # ------------------------------------------------------------------ #

    def _update_greeting(self) -> None:
        app  = _app()
        user = app.state.current_user
        name = user.display_name or (user.username if user else "Student")
        stats = app.task_controller.get_stats()

        self.ids.welcome_label.text = f"Welcome, {name}."
        due = stats["due_today"]
        if due == 0:
            msg = "No tasks due today. Great work!"
        elif due == 1:
            msg = "You have 1 task due today. Stay focused."
        else:
            msg = f"You have {due} tasks due today. Stay focused."
        self.ids.tasks_due_label.text = msg

    # ------------------------------------------------------------------ #
    #  Task list                                                          #
    # ------------------------------------------------------------------ #

    def refresh_tasks(self) -> None:
        """Clear and repopulate important and upcoming task sections."""
        important_list = self.ids.important_list
        upcoming_list = self.ids.upcoming_list
        important_list.clear_widgets()
        upcoming_list.clear_widgets()

        ctrl = _app().task_controller
        important = ctrl.get_important_tasks()
        upcoming = ctrl.get_upcoming_tasks()

        self.ids.important_count_label.text = f"{len(important)} task(s)"
        self.ids.upcoming_count_label.text = f"{len(upcoming)} task(s)"

        if not important:
            important_list.add_widget(self._empty_label("No high-priority tasks."))
        else:
            for task in important:
                important_list.add_widget(self._make_card(task))

        if not upcoming:
            upcoming_list.add_widget(self._empty_label("No upcoming tasks."))
        else:
            for task in upcoming:
                upcoming_list.add_widget(self._make_card(task))

    def _empty_label(self, text: str) -> Label:
        return Label(
            text=text,
            font_size=dp(13),
            color=_app().theme_text_muted,
            halign="left",
            size_hint_y=None,
            height=dp(40),
        )

    def _make_card(self, task) -> TaskCard:
        return TaskCard(
            task_id=task.id,
            task_title=task.title,
            module_name=task.module,
            due_date=task.due_date,
            priority=task.priority,
            is_complete=task.is_complete,
        )

    # ------------------------------------------------------------------ #
    #  Navigation                                                         #
    # ------------------------------------------------------------------ #

    def go_to_add_task(self) -> None:
        """FAB pressed — open Add Task in 'new' mode."""
        app = _app()
        app.task_controller.set_edit_mode(False)
        app.state.selected_task_id = None
        app.root.current = "add_task"
        app.root.get_screen("add_task").reset_form()

    def go_to_tasks(self) -> None:
        _app().root.current = "tasks"

    def go_to_profile(self) -> None:
        _app().root.current = "profile"


# ─────────────────────────────────────────────────────────────────────────────
#  Helper
# ─────────────────────────────────────────────────────────────────────────────

def _app():
    from kivy.app import App
    return App.get_running_app()
