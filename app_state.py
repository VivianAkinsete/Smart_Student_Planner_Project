"""
Application State — shared singleton accessed via App.get_running_app().state.

MVC role: Bridges Controller and View.
Holds runtime state that multiple screens need to read/write.
No UI code lives here; no DB code lives here.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from models.user import User
from models.task import Task


@dataclass
class AppState:
    """
    Single source of truth for runtime state.

    Attributes
    ----------
    current_user      : The authenticated User, or None if logged out.
    selected_task_id  : The task the user tapped — passed to TaskDetailScreen.
    filter_priority   : Active priority filter on Dashboard ('All', 'High', etc.).
    search_query      : Live search text on Dashboard.
    task_edit_mode    : True when AddTaskScreen is editing an existing task.
    """
    current_user:     Optional[User] = None
    selected_task_id: Optional[int]  = None
    filter_priority:  str            = "All"
    search_query:     str            = ""
    task_edit_mode:   bool           = False

    # Notification toggle stored in memory (could be persisted to prefs table)
    notifications_enabled: bool = True
    dark_mode_enabled: bool = False

    def reset(self) -> None:
        """Clear session state on logout."""
        self.current_user     = None
        self.selected_task_id = None
        self.filter_priority  = "All"
        self.search_query     = ""
        self.task_edit_mode   = False
