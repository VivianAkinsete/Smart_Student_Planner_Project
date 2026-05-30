"""
TaskCard — Reusable task row widget.
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty


class TaskCard(BoxLayout):
    """
    A single task row rendered in task lists.
    Receives task data as Kivy properties so the KV rule can bind to them.
    """
    task_id             = NumericProperty(0)
    task_title          = StringProperty("")
    module_name         = StringProperty("")
    due_date            = StringProperty("")
    priority            = StringProperty("Medium")
    is_complete         = BooleanProperty(False)
    priority_text_color = ListProperty([0, 0, 0, 1])

    PRIORITY_COLORS = {
        "High":   [0.961, 0.502, 0.090, 1],   # amber
        "Medium": [0.098, 0.463, 0.824, 1],   # blue
        "Low":    [0.220, 0.557, 0.235, 1],   # green
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.priority_text_color = self.PRIORITY_COLORS.get(
            self.priority, [0, 0, 0, 1]
        )

    def on_priority(self, instance, value):
        self.priority_text_color = self.PRIORITY_COLORS.get(value, [0, 0, 0, 1])

    def on_toggle_complete(self, active: bool) -> None:
        """Checkbox toggled — call controller to persist."""
        app = _app()
        app.task_controller.toggle_complete(self.task_id)
        app.root.get_screen("dashboard").refresh_tasks()
        app.root.get_screen("tasks").refresh_tasks()

    def on_tap(self) -> None:
        """Chevron tapped — navigate to task detail."""
        app = _app()
        app.task_controller.select_task(self.task_id)
        app.root.current = "add_task"
        screen = app.root.get_screen("add_task")
        screen.load_task_for_edit(self.task_id)


def _app():
    from kivy.app import App
    return App.get_running_app()
