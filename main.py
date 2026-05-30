import os # This line brings in a built‑in Python tool that helps the program work with the computer’s file system, such as managing file paths.
import sys #This loads Python tool that the program interact with system settings, such as changing where Python looks for modules

ROOT = os.path.dirname(os.path.abspath(__file__)) # This line sets a variable called ROOT to the directory where the main.py file is located. It uses os.path functions to get the absolute path of the current file and then finds its directory.
for sub in ("", "models", "views", "controllers", "db"):
    p = os.path.join(ROOT, sub)
    if p not in sys.path:
        sys.path.insert(0, p)


os.environ.setdefault("KIVY_NO_ENV_CONFIG", "1")

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.properties import ListProperty, BooleanProperty


from db.database import init_db


from controllers.app_state import AppState
from controllers.auth_controller import AuthController
from controllers.task_controller import TaskController


from views.login_screen    import LoginScreen
from views.signup_screen   import SignupScreen
from views.dashboard_screen import DashboardScreen
from views.tasks_screen     import TasksScreen
from views.add_task_screen  import AddTaskScreen
from views.profile_screen   import ProfileScreen


Window.size = (400, 780)


def _load_kv(filename: str) -> None:
    """Load a .kv file relative to the views/ directory."""
    path = os.path.join(ROOT, "views", filename)
    Builder.load_file(path)


class PlannerApp(App):
    """
    Root application class.

    Public attributes (accessible via App.get_running_app()):
        state            : AppState singleton
        auth_controller  : AuthController
        task_controller  : TaskController
    """

    title = "Smart Student Planner"
    theme_bg = ListProperty([0.984, 0.976, 0.980, 1])
    theme_surface = ListProperty([1, 1, 1, 1])
    theme_input_bg = ListProperty([1, 1, 1, 1])
    theme_border = ListProperty([0.894, 0.886, 0.894, 1])
    theme_text = ListProperty([0.106, 0.106, 0.114, 1])
    theme_text_muted = ListProperty([0.220, 0.235, 0.255, 1])
    theme_header_text = ListProperty([0.114, 0.169, 0.243, 1])
    theme_nav_active_bg = ListProperty([0.820, 0.957, 0.918, 1])
    theme_nav_active_text = ListProperty([0.086, 0.639, 0.290, 1])
    theme_nav_inactive_text = ListProperty([0.459, 0.459, 0.459, 1])
    theme_accent = ListProperty([0.608, 0.733, 0.643, 1])
    dark_mode = BooleanProperty(False)

    def build(self):
        # 1. Initialise the database (creates tables + seeds default data)
        init_db()

        # 2. Initialise shared state and controllers
        self.state           = AppState()
        self.auth_controller = AuthController(self.state)
        self.task_controller = TaskController(self.state)
        self.apply_theme(self.state.dark_mode_enabled)

        LabelBase.register(
            name="mdi",
            fn_regular=os.path.join(ROOT, "assets", "fonts", "materialdesignicons-webfont.ttf"),
        )

        # 3. Load KV layout files
        _load_kv("login_screen.kv")
        _load_kv("signup_screen.kv")
        _load_kv("task_card.kv")
        _load_kv("dashboard_screen.kv")
        _load_kv("tasks_screen.kv")
        _load_kv("add_task_screen.kv")
        _load_kv("profile_screen.kv")

        # 4. Build the ScreenManager
        sm = ScreenManager(transition=SlideTransition(duration=0.25))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignupScreen(name="signup"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(TasksScreen(name="tasks"))
        sm.add_widget(AddTaskScreen(name="add_task"))
        sm.add_widget(ProfileScreen(name="profile"))

        # Start on the login screen
        sm.current = "login"
        return sm

    def apply_theme(self, enabled: bool) -> None:
        self.dark_mode = enabled
        if enabled:
            self.theme_bg = [0.090, 0.102, 0.114, 1]
            self.theme_surface = [0.149, 0.161, 0.173, 1]
            self.theme_input_bg = [0.180, 0.192, 0.208, 1]
            self.theme_border = [0.325, 0.341, 0.365, 1]
            self.theme_text = [0.925, 0.925, 0.937, 1]
            self.theme_text_muted = [0.780, 0.792, 0.808, 1]
            self.theme_header_text = [0.925, 0.925, 0.937, 1]
            self.theme_nav_active_bg = [0.180, 0.259, 0.224, 1]
            self.theme_nav_active_text = [0.553, 0.855, 0.635, 1]
            self.theme_nav_inactive_text = [0.659, 0.667, 0.678, 1]
            self.theme_accent = [0.553, 0.855, 0.635, 1]
            Window.clearcolor = self.theme_bg
        else:
            self.theme_bg = [0.984, 0.976, 0.980, 1]
            self.theme_surface = [1, 1, 1, 1]
            self.theme_input_bg = [1, 1, 1, 1]
            self.theme_border = [0.765, 0.773, 0.792, 1]
            self.theme_text = [0.106, 0.106, 0.114, 1]
            self.theme_text_muted = [0.200, 0.216, 0.239, 1]
            self.theme_header_text = [0.114, 0.169, 0.243, 1]
            self.theme_nav_active_bg = [0.820, 0.957, 0.918, 1]
            self.theme_nav_active_text = [0.086, 0.639, 0.290, 1]
            self.theme_nav_inactive_text = [0.459, 0.459, 0.459, 1]
            self.theme_accent = [0.608, 0.733, 0.643, 1]
            Window.clearcolor = self.theme_bg


if __name__ == "__main__":
    PlannerApp().run()
