"""
AddTaskScreen — View layer for the Add / Edit Task screen.

MVC role: This is the V.
Handles both "add new" and "edit existing" modes.
All business logic delegated to TaskController (C).
Inline validation errors displayed without alert popups.
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.animation import Animation


PRIORITY_OPTIONS = ["High", "Medium", "Low"]

PRIORITY_ACTIVE = {
    "High":   (0.961, 0.502, 0.090, 1),   # amber
    "Medium": (0.098, 0.463, 0.824, 1),   # blue
    "Low":    (0.220, 0.557, 0.235, 1),   # green
}


class AddTaskScreen(Screen):
    """
    Dual-mode screen:
      - edit_mode = False  → creates a new task
      - edit_mode = True   → edits the task in AppState.selected_task_id
    """

    _selected_priority: str = "Medium"
    _edit_task_id: int | None = None

    # ------------------------------------------------------------------ #
    #  Lifecycle                                                          #
    # ------------------------------------------------------------------ #

    def on_enter(self, *args):
        """
        Called every time the screen becomes active.
        reset_form() or load_task_for_edit() should be called before
        navigation so the correct mode is set up.
        """
        self._build_priority_buttons()

    def reset_form(self) -> None:
        """Clear all fields for 'Add New Task' mode."""
        self._edit_task_id = None
        self._selected_priority = "Medium"
        self.ids.screen_title_label.text = "New Task"
        self.ids.title_input.text    = ""
        self.ids.module_input.text   = ""
        self.ids.due_date_input.text = ""
        self.ids.notes_input.text    = ""
        self._hide_errors()
        self._build_priority_buttons()

    def load_task_for_edit(self, task_id: int) -> None:
        """Populate fields for 'Edit Task' mode."""
        task = _app().task_controller.get_task(task_id)
        if not task:
            return
        self._edit_task_id = task_id
        self._selected_priority = task.priority
        self.ids.screen_title_label.text = "Edit Task"
        self.ids.title_input.text    = task.title
        self.ids.module_input.text   = task.module
        self.ids.due_date_input.text = task.due_date
        self.ids.notes_input.text    = task.notes
        self._hide_errors()
        self._build_priority_buttons()

    # ------------------------------------------------------------------ #
    #  Priority segmented control                                         #
    # ------------------------------------------------------------------ #

    def _build_priority_buttons(self) -> None:
        selector = self.ids.priority_selector
        selector.clear_widgets()

        for p in PRIORITY_OPTIONS:
            is_active = (p == self._selected_priority)
            active_color = PRIORITY_ACTIVE[p]
            btn = Button(
                text             = p,
                font_size        = dp(13),
                bold             = is_active,
                background_normal  = "",
                background_color   = active_color if is_active else _app().theme_surface,
                color            = (1, 1, 1, 1) if is_active else _app().theme_text_muted,
            )
            btn.bind(on_press=lambda b, pri=p: self._select_priority(pri))
            from kivy.graphics import Color, RoundedRectangle, Line
            with btn.canvas.before:
                c = Color(rgba=active_color if is_active else _app().theme_border)
                Line(rounded_rectangle=[btn.x, btn.y, btn.width, btn.height, dp(8)],
                     width=dp(1 if is_active else 0.8))
            btn.bind(pos=lambda b, *a: self._redraw_pri_btn(b),
                     size=lambda b, *a: self._redraw_pri_btn(b))
            selector.add_widget(btn)

    @staticmethod
    def _redraw_pri_btn(btn):
        from kivy.graphics import Color, Line
        btn.canvas.before.clear()
        with btn.canvas.before:
            Color(rgba=_app().theme_border)
            Line(rounded_rectangle=[btn.x, btn.y, btn.width, btn.height, dp(8)],
                 width=dp(0.8))

    def _select_priority(self, priority: str) -> None:
        self._selected_priority = priority
        self._build_priority_buttons()

    # ------------------------------------------------------------------ #
    #  Save                                                               #
    # ------------------------------------------------------------------ #

    def on_save(self) -> None:
        """
        Validate and save (add or update).
        Shows inline errors on failure; navigates back on success.
        """
        self._hide_errors()

        title    = self.ids.title_input.text.strip()
        module   = self.ids.module_input.text.strip()
        due_date = self.ids.due_date_input.text.strip()
        priority = self._selected_priority
        notes    = self.ids.notes_input.text.strip()

        # Client-side pre-validation for instant feedback
        has_error = False
        if not title:
            self._show_field_error("title_error", "Title is required.")
            has_error = True

        if due_date:
            import re
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", due_date):
                self._show_field_error("date_error", "Use YYYY-MM-DD format (e.g. 2024-12-25).")
                has_error = True

        if has_error:
            return

        ctrl = _app().task_controller

        if self._edit_task_id:
            task, error = ctrl.update_task(
                self._edit_task_id, title, module, due_date, priority, notes
            )
        else:
            task, error = ctrl.add_task(title, module, due_date, priority, notes)

        if error:
            self._show_field_error("title_error", error)
            return

        # Success — go back to tasks list and refresh
        self.manager.current = "tasks"
        self.manager.get_screen("tasks").refresh_tasks()
        self.manager.get_screen("dashboard").refresh_tasks()

    # ------------------------------------------------------------------ #
    #  Cancel                                                             #
    # ------------------------------------------------------------------ #

    def on_cancel(self) -> None:
        """Close button pressed — discard changes and go back."""
        self.manager.current = "tasks"
        self.manager.get_screen("tasks").refresh_tasks()

    # ------------------------------------------------------------------ #
    #  Delete (called from edit mode only)                                #
    # ------------------------------------------------------------------ #

    def on_delete(self) -> None:
        """
        Show a confirmation popup before deleting.
        Only available in edit mode.
        """
        if not self._edit_task_id:
            return
        self._show_delete_confirm()

    def _show_delete_confirm(self) -> None:
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        content.add_widget(Label(
            text="Delete this task?\nThis cannot be undone.",
            font_size=dp(14),
            color=_app().theme_text,
            halign="center",
        ))
        buttons = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(12))

        popup = Popup(title="Confirm Delete", content=content,
                      size_hint=(0.8, 0.35), auto_dismiss=True)

        cancel_btn = Button(text="Cancel", background_normal="",
                            background_color=_app().theme_bg,
                            color=_app().theme_text)
        cancel_btn.bind(on_press=popup.dismiss)

        delete_btn = Button(text="Delete", background_normal="",
                            background_color=(0.729, 0.102, 0.102, 1),
                            color=(1, 1, 1, 1))
        delete_btn.bind(on_press=lambda *a: self._confirm_delete(popup))

        buttons.add_widget(cancel_btn)
        buttons.add_widget(delete_btn)
        content.add_widget(buttons)
        popup.open()

    def _confirm_delete(self, popup: Popup) -> None:
        popup.dismiss()
        _app().task_controller.delete_task(self._edit_task_id)
        self.manager.current = "tasks"
        self.manager.get_screen("tasks").refresh_tasks()
        self.manager.get_screen("dashboard").refresh_tasks()

    # ------------------------------------------------------------------ #
    #  Error helpers                                                      #
    # ------------------------------------------------------------------ #

    def _show_field_error(self, field_id: str, message: str) -> None:
        lbl = self.ids[field_id]
        lbl.text = message
        Animation(height=dp(18), opacity=1, duration=0.2).start(lbl)

    def _hide_errors(self) -> None:
        for field_id in ("title_error", "date_error"):
            lbl = self.ids[field_id]
            lbl.text = ""
            Animation(height=dp(0), opacity=0, duration=0.1).start(lbl)


# ─────────────────────────────────────────────────────────────────────────────
#  Helper
# ─────────────────────────────────────────────────────────────────────────────

def _app():
    from kivy.app import App
    return App.get_running_app()
