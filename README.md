# Smart Student Planner

A Kivy-based student task planner with multi-user accounts, per-user data, and a clean tasks workflow.

## Features

- Multi-user signup and login (unique usernames)
- Per-user task isolation and stats
- Dashboard shows **Important** (High priority) and **Upcoming** (due today or later) tasks
- Separate Tasks screen with search and priority filters
- Add/Edit Task screen
- Global light/dark theme toggle
- Local persistence with SQLite

## Requirements

- Python 3.10+
- Kivy 2.3+

## Installation & Run

1. Install Python 3.10+ (if not already installed).

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install kivy
```

4. Run the app:

```bash
python main.py
```

## Default demo account

- **Username:** Vivian Akinsete
- **Password:** password123

## App structure (MVC)

```
main.py                 # App entry + ScreenManager wiring
db/
  __init__.py
  database.py           # SQLite init + connection helper
  dashboard_screen.py   # Legacy file (unused)
  planner.db            # Local SQLite database
models/
  __init__.py
  user.py               # User model + auth/signup logic
  task.py               # Task model + repository
controllers/
  __init__.py
  app_state.py          # Shared runtime state
  auth_controller.py    # Login/logout/signup orchestration
  task_controller.py    # Task CRUD, search/filter, dashboard slices
views/
  __init__.py
  login_screen.py/.kv
  signup_screen.py/.kv
  dashboard_screen.py/.kv
  tasks_screen.py/.kv
  add_task_screen.py/.kv
  profile_screen.py/.kv
  task_card.py/.kv
assets/
  fonts/
    materialdesignicons-webfont.ttf
    materialdesignicons.css
  icons/
fonts/
  NotoEmoji-Regular.ttf
Image/
  calender.png
  menu.png
  profile.jpg
```

## Notes

- Passwords are stored in plain text for demo purposes.
- Tasks are scoped by `user_id`, so each account has its own data.
