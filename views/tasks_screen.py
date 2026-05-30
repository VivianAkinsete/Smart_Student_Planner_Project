"""
TasksScreen — View layer for the Tasks list screen.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.metrics import dp
from views.task_card import TaskCard


class TasksScreen(Screen):
    """Shows the full task list with search and priority filters."""

    FILTER_OPTIONS = ["All", "High", "Medium", "Low"]

    def on_enter(self, *args):
        self._build_filter_pills()
        self.refresh_tasks()

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
                text=label,
                font_size=dp(12),
                size_hint=(None, 1),
                width=dp(72),
                background_normal="",
                background_color=_app().theme_accent if is_active else _app().theme_surface,
                color=(1, 1, 1, 1) if is_active else _app().theme_text_muted,
                bold=is_active,
            )
            btn.bind(on_press=lambda b, l=label: self._on_filter(l))
            from kivy.graphics import Color, Line
            with btn.canvas.before:
                Color(rgba=_app().theme_border)
                Line(rounded_rectangle=[btn.x, btn.y, btn.width, btn.height, dp(20)],
                     width=dp(0.8))
            bar.add_widget(btn)
            btn.bind(pos=self._redraw_pill, size=self._redraw_pill)

    @staticmethod
    def _redraw_pill(btn, *args):
        from kivy.graphics import Color, Line
        btn.canvas.before.clear()
        with btn.canvas.before:
            Color(rgba=_app().theme_border)
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
        _app().task_controller.set_search(text)
        if text:
            _app().task_controller.set_filter("All")
        self.refresh_tasks()

    # ------------------------------------------------------------------ #
    #  Task list                                                          #
    # ------------------------------------------------------------------ #

    def refresh_tasks(self) -> None:
        task_list = self.ids.task_list
        task_list.clear_widgets()

        tasks = _app().task_controller.get_tasks()
        self.ids.task_count_label.text = f"{len(tasks)} task(s)"

        if not tasks:
            empty = Label(
                text="No tasks found.\nTap + to add one!",
                font_size=dp(14),
                color=_app().theme_text_muted,
                halign="center",
                size_hint_y=None,
                height=dp(80),
            )
            task_list.add_widget(empty)
            return

        for task in tasks:
            card = TaskCard(
                task_id=task.id,
                task_title=task.title,
                module_name=task.module,
                due_date=task.due_date,
                priority=task.priority,
                is_complete=task.is_complete,
            )
            task_list.add_widget(card)

    # ------------------------------------------------------------------ #
    #  Navigation                                                         #
    # ------------------------------------------------------------------ #

    def go_to_add_task(self) -> None:
        app = _app()
        app.task_controller.set_edit_mode(False)
        app.state.selected_task_id = None
        app.root.current = "add_task"
        app.root.get_screen("add_task").reset_form()

    def go_to_dashboard(self) -> None:
        _app().root.current = "dashboard"

    def go_to_profile(self) -> None:
        _app().root.current = "profile"


def _app():
    from kivy.app import App
    return App.get_running_app()
