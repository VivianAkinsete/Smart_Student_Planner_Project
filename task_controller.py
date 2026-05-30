"""
Task Controller — orchestrates task operations between Views and the Task Model.

MVC role: This is the C for task management.
All validation, filtering, and search logic lives here.
Views call controller methods; they never touch TaskManager directly.
"""

from models.task import TaskManager, Task, VALID_PRIORITIES
from controllers.app_state import AppState
from typing import List, Tuple, Optional
from datetime import date


class TaskController:
    """
    Provides high-level task operations to Views.
    Returns (data, error_string) tuples so Views can display
    errors without knowing anything about the model layer.
    """

    def __init__(self, state: AppState):
        self._state   = state
        self._manager = TaskManager()

    # ------------------------------------------------------------------ #
    #  Read                                                               #
    # ------------------------------------------------------------------ #

    def get_tasks(self) -> List[Task]:
        """
        Return tasks applying the current filter and search query
        stored in AppState. Used by DashboardScreen to refresh the list.
        """
        if not self._state.current_user:
            return []
        query    = self._state.search_query.strip()
        priority = self._state.filter_priority
        user_id  = self._state.current_user.id

        if query:
            tasks = self._manager.search(user_id, query)
        elif priority and priority != "All":
            tasks = self._manager.filter_by_priority(user_id, priority)
        else:
            tasks = self._manager.get_all(user_id)
        return tasks

    def get_task(self, task_id: int) -> Optional[Task]:
        """Return a single task by id for the detail screen."""
        if not self._state.current_user:
            return None
        return self._manager.get_by_id(self._state.current_user.id, task_id)

    def get_selected_task(self) -> Optional[Task]:
        """Convenience: fetch the task currently stored in AppState."""
        if self._state.selected_task_id is None:
            return None
        if not self._state.current_user:
            return None
        return self._manager.get_by_id(self._state.current_user.id, self._state.selected_task_id)

    def get_stats(self) -> dict:
        """Return summary stats shown on the Dashboard header."""
        if not self._state.current_user:
            return {"total": 0, "completed": 0, "due_today": 0}
        user_id = self._state.current_user.id
        all_tasks  = self._manager.get_all(user_id)
        total      = len(all_tasks)
        completed  = sum(1 for t in all_tasks if t.is_complete)
        due_today  = sum(
            1 for t in all_tasks
            if not t.is_complete and t.due_date == _today()
        )
        return {"total": total, "completed": completed, "due_today": due_today}

    def get_important_tasks(self) -> List[Task]:
        """High priority tasks (not complete)."""
        if not self._state.current_user:
            return []
        tasks = self._manager.filter_by_priority(self._state.current_user.id, "High")
        return [t for t in tasks if not t.is_complete]

    def get_upcoming_tasks(self) -> List[Task]:
        """Tasks with due dates today or later (not complete)."""
        if not self._state.current_user:
            return []
        all_tasks = self._manager.get_all(self._state.current_user.id)
        upcoming = []
        today = date.today().isoformat()
        for task in all_tasks:
            if task.is_complete or not task.due_date:
                continue
            if task.due_date >= today:
                upcoming.append(task)
        return sorted(upcoming, key=lambda t: t.due_date)

    # ------------------------------------------------------------------ #
    #  Write                                                              #
    # ------------------------------------------------------------------ #

    def add_task(self, title: str, module: str, due_date: str,
                 priority: str, notes: str) -> Tuple[Optional[Task], str]:
        """
        Create a new task.
        Returns (Task, "") on success or (None, error_message) on failure.
        """
        if not self._state.current_user:
            return None, "Please sign in to add tasks."
        try:
            task = self._manager.add(self._state.current_user.id, title, module, due_date, priority, notes)
            return task, ""
        except ValueError as exc:
            return None, str(exc)

    def update_task(self, task_id: int, title: str, module: str,
                    due_date: str, priority: str,
                    notes: str) -> Tuple[Optional[Task], str]:
        """
        Update an existing task.
        Returns (Task, "") on success or (None, error_message) on failure.
        """
        if not self._state.current_user:
            return None, "Please sign in to update tasks."
        try:
            task = self._manager.update(self._state.current_user.id, task_id, title, module, due_date, priority, notes)
            return task, ""
        except (ValueError, KeyError) as exc:
            return None, str(exc)

    def delete_task(self, task_id: int) -> Tuple[bool, str]:
        """Delete a task. Returns (True, "") or (False, error_message)."""
        if not self._state.current_user:
            return False, "Please sign in to delete tasks."
        ok = self._manager.delete(self._state.current_user.id, task_id)
        if ok:
            if self._state.selected_task_id == task_id:
                self._state.selected_task_id = None
            return True, ""
        return False, "Task not found."

    def toggle_complete(self, task_id: int) -> Tuple[bool, str]:
        """
        Flip is_complete on a task.
        Returns (new_complete_state, "") or (False, error_message).
        """
        if not self._state.current_user:
            return False, "Please sign in to update tasks."
        task = self._manager.get_by_id(self._state.current_user.id, task_id)
        if not task:
            return False, "Task not found."
        new_state = not task.is_complete
        self._manager.set_complete(self._state.current_user.id, task_id, new_state)
        return new_state, ""

    # ------------------------------------------------------------------ #
    #  State helpers for Views                                            #
    # ------------------------------------------------------------------ #

    def set_filter(self, priority: str) -> None:
        """Update the active priority filter in AppState."""
        self._state.filter_priority = priority

    def set_search(self, query: str) -> None:
        """Update the active search query in AppState."""
        self._state.search_query = query

    def select_task(self, task_id: int) -> None:
        """Mark a task as selected (for detail/edit navigation)."""
        self._state.selected_task_id = task_id

    def set_edit_mode(self, editing: bool) -> None:
        self._state.task_edit_mode = editing


def _today() -> str:
    from datetime import date
    return date.today().isoformat()
