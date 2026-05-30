"""
DashboardScreen + TaskCard — View layer for the Dashboard.

MVC role: This is the V.
DashboardScreen reads from TaskController (C) and renders task cards.
TaskCard is a reusable widget for a single task row.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty
from kivy.metrics import dp
from kivy.clock import Clock


# ─────────────────────────────────────────────────────────────────────────────
#  TaskCard widget
# ─────────────────────────────────────────────────────────────────────────────

class TaskCard(BoxLayout):
    """
    A single task row rendered in the Dashboard list.
    Receives task data as Kivy properties so the KV rule can bind to them.
    """
    task_id            = NumericProperty(0)
    task_title         = StringProperty("")
    module_name        = StringProperty("")
    due_date           = StringProperty("")
    priority           = StringProperty("Medium")
    is_complete        = BooleanProperty(False)
    priority_text_color = ListProperty([0, 0, 0, 1])

    # Map priority → (bg_color, text_color) — mirroring the HTML badge colours
    PRIORITY_COLORS = {
        "High":   [0.961, 0.502, 0.090, 1],   # amber text
        "Medium": [0.098, 0.463, 0.824, 1],   # blue text
        "Low":    [0.220, 0.557, 0.235, 1],   # green text
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
        # Refresh the dashboard list
        app.root.get_screen("dashboard").refresh_tasks()

    def on_tap(self) -> None:
        """Chevron tapped — navigate to task detail."""
        app = _app()
        app.task_controller.select_task(self.task_id)
        app.root.current = "add_task"   # reuses Add/Edit screen in edit mode
        screen = app.root.get_screen("add_task")
        screen.load_task_for_edit(self.task_id)


# ─────────────────────────────────────────────────────────────────────────────
#  DashboardScreen
# ─────────────────────────────────────────────────────────────────────────────

class DashboardScreen(Screen):
    """
    Home screen. Shows task list filtered by search and priority.
    State (filter, query) lives in AppState; this screen reads from it.
    """

    FILTER_OPTIONS = ["All", "High", "Medium", "Low"]

    def on_enter(self, *args):
        """Refresh content every time the user navigates here."""
        self._update_greeting()
        self._build_filter_pills()
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
    #  Filter pills                                                       #
    # ------------------------------------------------------------------ #

    def _build_filter_pills(self) -> None:
        bar = self.ids.filter_bar
        bar.clear_widgets()
        active = _app().state.filter_priority or "All"

        for label in self.FILTER_OPTIONS:
            is_active = (label == active)
            btn = Button(
                text         = label,
                font_size    = dp(12),
                size_hint    = (None, 1),
                width        = dp(72),
                background_normal  = "",
                background_color   = (0.408, 0.659, 0.502, 1) if is_active else (1, 1, 1, 1),
                color        = (1, 1, 1, 1) if is_active else (0.267, 0.278, 0.298, 1),
                bold         = is_active,
            )
            btn.bind(on_press=lambda b, l=label: self._on_filter(l))
            # Draw rounded pill border
            from kivy.graphics import Color, RoundedRectangle, Line
            with btn.canvas.before:
                Color(rgba=(0.773, 0.780, 0.804, 1))
                Line(rounded_rectangle=[btn.x, btn.y, btn.width, btn.height, dp(20)],
                     width=dp(0.8))
            bar.add_widget(btn)
            # Trigger canvas update after layout
            btn.bind(pos=self._redraw_pill, size=self._redraw_pill)

    @staticmethod
    def _redraw_pill(btn, *args):
        from kivy.graphics import Color, Line
        btn.canvas.before.clear()
        with btn.canvas.before:
            Color(rgba=(0.773, 0.780, 0.804, 1))
            Line(rounded_rectangle=[btn.x, btn.y, btn.width, btn.height, dp(20)],
                 width=dp(0.8))

    def _on_filter(self, priority: str) -> None:
        _app().task_controller.set_filter(priority)
        _app().task_controller.set_search("")
        self.ids.search_input.text = ""
        self._build_filter_pills()
        self.refresh_tasks()

    # ------------------------------------------------------------------ #
    #  Search                                                             #
    # ------------------------------------------------------------------ #

    def on_search(self, text: str) -> None:
        """Called on every keystroke in the search box."""
        _app().task_controller.set_search(text)
        if text:
            _app().task_controller.set_filter("All")
        self.refresh_tasks()

    # ------------------------------------------------------------------ #
    #  Task list                                                          #
    # ------------------------------------------------------------------ #

    def refresh_tasks(self) -> None:
        """Clear and repopulate the task list from the controller."""
        task_list = self.ids.task_list
        task_list.clear_widgets()

        tasks = _app().task_controller.get_tasks()
        self.ids.task_count_label.text = f"{len(tasks)} task(s)"

        if not tasks:
            empty = Label(
                text       = "No tasks found.\nTap + to add one!",
                font_size  = dp(14),
                color      = (0.459, 0.459, 0.459, 1),
                halign     = "center",
                size_hint_y = None,
                height     = dp(80),
            )
            task_list.add_widget(empty)
            return

        for task in tasks:
            card = TaskCard(
                task_id     = task.id,
                task_title  = task.title,
                module_name = task.module,
                due_date    = task.due_date,
                priority    = task.priority,
                is_complete = task.is_complete,
            )
            task_list.add_widget(card)

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
        """Tasks nav item — stay on dashboard (same screen in this layout)."""
        self.refresh_tasks()

    def go_to_profile(self) -> None:
        _app().root.current = "profile"


# ─────────────────────────────────────────────────────────────────────────────
#  Helper
# ─────────────────────────────────────────────────────────────────────────────

def _app():
    from kivy.app import App
    return App.get_running_app()
