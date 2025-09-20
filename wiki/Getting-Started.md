# Getting Started

This guide helps new developers get up and running with the Budget Planner project quickly and efficiently.

## 🎯 Prerequisites

### Required Software
- **Python 3.8+** - Core language requirement
- **Git** - Version control
- **SQLite3** - Database (usually included with Python)

### Optional Tools
- **IDE/Editor** with Python support (VS Code, PyCharm, etc.)
- **DB Browser for SQLite** - For database inspection
- **Python virtual environment** - For dependency isolation

## 🚀 Quick Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Mika-Rsbg/Budget-Planner.git
cd Budget-Planner
```

### 2. Set Up Python Environment (Recommended)

```bash
# Create virtual environment
python -m venv budget-planner-env

# Activate it
# Windows:
budget-planner-env\Scripts\activate
# Linux/MacOS:
source budget-planner-env/bin/activate
```

### 3. Install Dependencies

Currently, the project uses only standard library modules, so no additional installations are needed. However, check `requirements.txt` for any future dependencies:

```bash
pip install -r requirements.txt
```

### 4. First Run

```bash
# Run the application
python src/main.py
```

On first run, the application will:
- Create the SQLite database at `data/database.db`
- Set up logging in the `log/` directory
- Launch the main Homepage window

### 5. Test Mode (Optional)

For development and testing:

```python
# In Python shell or modify main.py
from src.main import main_test
main_test()
```

## 📁 Project Structure Overview

Understanding the basic layout will help you navigate the codebase:

```
Budget-Planner/
├── src/                          # Main application code
│   ├── main.py                   # Application entry point
│   ├── config.py                 # Central configuration
│   ├── gui/                      # GUI components
│   │   ├── basewindow.py         # Base class for main windows
│   │   ├── basetoplevelwindow.py # Base class for dialogs
│   │   ├── homepage/             # Main application window
│   │   ├── plugins/              # Extensible plugin system
│   │   └── [other_pages]/        # Specialized UI pages
│   └── utils/                    # Utility modules
│       ├── data/                 # Database and data handling
│       ├── logging/              # Logging configuration
│       └── ai/                   # Budget suggestions (basic)
├── data/                         # Database files (created at runtime)
├── log/                          # Log files (created at runtime)
├── docs/                         # Project documentation
├── wiki/                         # Developer wiki pages
└── src_old/                      # Legacy code (reference)
```

## 🔍 Understanding the Architecture

### Core Components

1. **Entry Point** (`src/main.py`)
   - Creates database schema
   - Sets up logging
   - Launches Homepage window

2. **Base Classes** (`src/gui/`)
   - `BaseWindow`: Main application windows
   - `BaseToplevelWindow`: Modal dialogs and popups

3. **Plugin System** (`src/gui/plugins/`)
   - Extensible menu system
   - Follows naming convention: `plugin_{scope}_{type}_{name}.py`

4. **Database Layer** (`src/utils/data/`)
   - Singleton connection pattern
   - Domain-specific utility modules

### Key Patterns

- **Logging Decorator**: Use `@log_fn` for automatic function timing
- **Configuration**: All paths managed in `src/config.py`
- **Database Access**: Always use utility functions, never direct SQL
- **GUI Inheritance**: All windows inherit from base classes

## 🛠️ Development Workflow

### Making Your First Change

1. **Pick a Good First Issue**: Look for issues labeled `good first issue`

2. **Create a Branch**: Follow the [branch naming conventions](https://github.com/Mika-Rsbg/Budget-Planner/blob/main/docs/BRANCH_GUIDELINES.md)
   ```bash
   git checkout -b feat/your-feature-name
   ```

3. **Make Changes**: Follow existing patterns and coding style

4. **Test Your Changes**:
   ```bash
   python src/main.py  # Run the full app
   # Or use test mode for specific components
   ```

5. **Commit**: Follow [commit message guidelines](https://github.com/Mika-Rsbg/Budget-Planner/blob/main/docs/COMMIT_GUIDELINES.md)
   ```bash
   git commit -m "feat(gui): add new feature description"
   ```

6. **Submit PR**: Create pull request with clear description

### Common Development Tasks

#### Adding a New GUI Window

1. Create new class inheriting from `BaseWindow` or `BaseToplevelWindow`
2. Implement `init_ui()` method
3. Add navigation from existing windows
4. Test window lifecycle (open, close, reload)

```python
from gui.basewindow import BaseWindow

class MyWindow(BaseWindow):
    def __init__(self):
        super().__init__(plugin_scope="mywindow", title="My Window")
    
    def init_ui(self):
        # Implement UI components
        pass
```

#### Adding Database Functionality

1. Add utility functions in appropriate `src/utils/data/database/` module
2. Use `@log_fn` decorator for logging
3. Always use parameterized queries
4. Test with sample data

```python
from utils.data.database_connection import DatabaseConnection
from utils.logging.logging_tools import log_fn

@log_fn
def get_my_data():
    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM my_table WHERE condition = ?", (value,))
    return cursor.fetchall()
```

#### Creating a Plugin

1. Follow naming convention: `plugin_{scope}_{type}_{name}.py`
2. Implement required interface methods
3. Add `menu_id` for ordering (10, 20, 30, etc.)
4. Place in `src/gui/plugins/` directory

```python
# plugin_homepage_menu_myfeature.py
menu_id = 25

def add_to_menu(window, menu_bar):
    # Add menu items to the menu bar
    pass
```

## 🐛 Debugging Tips

### Logging
- Check `log/app.log` for detailed debug information
- Use `log/app_no_debug.log` for cleaner INFO-level logs
- Add `@log_fn` decorator to functions for automatic timing

### Database Issues
- Use DB Browser for SQLite to inspect `data/database.db`
- Check foreign key relationships
- Verify data types match schema

### GUI Issues
- Test window resizing and fullscreen mode
- Verify menu items load correctly
- Check plugin loading with different scopes

## 📚 Next Steps

Once you're comfortable with the basics:

1. **[Architecture Overview](Architecture-Overview)** - Understand the deeper design patterns
2. **[Core Modules & Structure](Core-Modules-Structure)** - Detailed component breakdown  
3. **[Plugin Development](Plugin-Development)** - Create extensible features
4. **[Development Workflows](Development-Workflows)** - Advanced development patterns

## 🤝 Getting Help

- **Issues**: Check existing GitHub issues or create new ones
- **Discussions**: Use GitHub Discussions for questions
- **Code Review**: Submit PRs for feedback on changes
- **Documentation**: Contribute to these wiki pages!

---

*Ready to start contributing? Pick an issue and dive in! The modular architecture makes it easy to work on isolated features without affecting the entire system.*