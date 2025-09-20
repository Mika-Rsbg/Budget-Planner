# Architecture Overview

This document provides a comprehensive overview of the Budget Planner application's architecture, design patterns, and core organizational principles.

## 🏗️ High-Level Architecture

Budget Planner follows a **modular, plugin-based architecture** with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Presentation  │    │   Business      │    │     Data        │
│   Layer (GUI)   │◄──►│   Logic Layer   │◄──►│     Layer       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
       │                        │                       │
   ┌───▼───┐              ┌─────▼─────┐         ┌──────▼──────┐
   │Plugin │              │ Utilities │         │   SQLite    │
   │System │              │& AI Logic │         │  Database   │
   └───────┘              └───────────┘         └─────────────┘
```

### Core Architectural Principles

1. **Plugin-Based Extensibility**: Features can be added without modifying core code
2. **Singleton Database Pattern**: Single connection instance shared across the application
3. **Base Class Inheritance**: Consistent behavior through shared base classes
4. **Decorator-Based Logging**: Automatic timing and debug information
5. **Configuration Centralization**: All paths and settings managed centrally

## 📱 Application Flow

### Startup Sequence

```python
# 1. Bootstrap (main.py)
setup_logging()                    # Configure logging system
create_database()                  # Ensure database schema exists

# 2. Application Launch
app = Homepage(fullscreen=True)    # Create main window
app.run()                         # Start GUI main loop
```

### Window Lifecycle

```python
# 1. Window Creation
class MyWindow(BaseWindow):
    def __init__(self):
        super().__init__(plugin_scope="mywindow", title="My Window")
        # Base class handles: styles, main_frame, status_bar, menu, plugins
        # Then calls init_ui()

# 2. UI Initialization 
def init_ui(self):
    # Custom UI components are created here
    # This is called automatically by base class

# 3. Plugin Loading
# Automatically loads plugins matching scope and type
# Plugins add menu items, behaviors, etc.
```

## 🔧 Core Components

### 1. Entry Point (`src/main.py`)

The application entry point manages the bootstrap process:

```python
@log_fn
def main() -> None:
    """Main application entry point"""
    from gui.homepage.homepage import Homepage
    from utils.data.createdatabase_utils import create_database

    logger.info("APPLICATION STARTED")
    create_database()           # Ensure database schema
    app = Homepage(fullscreen=True)  # Launch main window
    app.run()                   # Start event loop
```

**Key Responsibilities:**
- Logging initialization
- Database schema creation
- Main window instantiation
- Application lifecycle management

### 2. Configuration Management (`src/config.py`)

Centralized configuration using `pathlib` for cross-platform compatibility:

```python
class Database:
    PATH = Path(__file__).resolve().parent.parent / 'data' / 'database.db'

class Logging:
    LOG_DIR = Path(__file__).resolve().parent.parent / 'log'
    LOG_FILE = LOG_DIR / 'app.log'
    LOG_FILE_NO_DEBUG = LOG_DIR / 'app_no_debug.log'
```

**Design Rationale:**
- Single source of truth for paths
- Environment-agnostic path handling
- Easy to modify without code changes

### 3. GUI Base Classes

#### BaseWindow (Main Windows)

```python
class BaseWindow(tk.Tk):
    def __init__(self, plugin_scope: str, title: str = "Fenster",
                 geometry: str = "800x600", bg_color: str = "white",
                 fullscreen: bool = False):
        super().__init__()
        self.plugin_scope = plugin_scope
        # Setup: styles, main_frame, status_bar, menu
        self._setup_menu()  # Loads plugins automatically
        self.init_ui()      # Must be implemented by subclasses
```

**Key Features:**
- Automatic plugin loading based on scope
- Consistent styling with ttk theme "clam"
- Standard menu, status bar, and main frame
- Required `init_ui()` method for customization

#### BaseToplevelWindow (Modal Dialogs)

```python
class BaseToplevelWindow(tk.Toplevel):
    def __init__(self, master: BaseWindow, plugin_scope: str = "",
                 title: str = "Fenster", geometry: str = "600x400",
                 bg_color: str = "white"):
        super().__init__(master)
        # Similar setup but as modal dialog
```

**Key Features:**
- Modal dialog behavior
- Inherits styling from BaseWindow
- Plugin support for specialized dialogs
- Automatic parent window relationship

### 4. Plugin System (`src/gui/plugins/`)

**Naming Convention:**
```
plugin_{scope}_{type}_{name}.py
```

- `scope`: `all` (global) or specific window name (e.g., `homepage`)
- `type`: Currently `menu` (extensible)  
- `name`: Brief feature description

**Plugin Structure:**
```python
# plugin_homepage_menu_account.py
menu_id = 10  # Controls menu ordering (10, 20, 30...)

def add_to_menu(window, menu_bar):
    """Add menu items to the menu bar"""
    account_menu = tk.Menu(menu_bar, tearoff=0)
    account_menu.add_command(label="Add Account", command=lambda: add_account())
    menu_bar.add_cascade(label="Account", menu=account_menu)
```

**Plugin Loading Process:**
```python
@log_fn
def load_plugins(plugin_type: str, plugin_scope: str):
    """Dynamically loads and sorts plugins by menu_id"""
    # 1. Scan plugin directory for matching files
    # 2. Filter by naming convention
    # 3. Import modules dynamically
    # 4. Sort by menu_id for consistent ordering
    # 5. Return loaded modules
```

### 5. Database Layer

#### Connection Management (Singleton Pattern)

```python
class DatabaseConnection:
    _instance: Optional[sqlite3.Connection] = None
    
    @staticmethod
    def get_connection(db_path: Path = config.Database.PATH) -> sqlite3.Connection:
        """Returns singleton database connection"""
        if DatabaseConnection._instance is None:
            DatabaseConnection._instance = sqlite3.connect(db_path)
        return DatabaseConnection._instance
```

**Benefits:**
- Single connection prevents SQLite locking issues
- Consistent database access across modules
- Automatic connection reuse

#### Data Access Pattern

Database operations are organized by domain in `src/utils/data/database/`:

```python
# src/utils/data/database/account_utils.py
@log_fn
def get_account_data(selected_columns: List[bool] = None) -> List[Tuple]:
    """Get account data with column selection"""
    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor()
    # Parameterized queries only
    cursor.execute("SELECT * FROM tbl_Account WHERE condition = ?", (value,))
    return cursor.fetchall()
```

**Key Principles:**
- Always use parameterized queries
- Organize utilities by domain (accounts, transactions, categories)
- Use `@log_fn` decorator for timing
- Return simple data structures (tuples, lists)

### 6. Logging System

#### Decorator Pattern

```python
@log_fn
def my_function():
    """Automatically logged with timing information"""
    # Function implementation
```

**Generated Output:**
```
2024-01-01 10:00:00 - module_name - [DEBUG] - Start: my_function
2024-01-01 10:00:01 - module_name - [DEBUG] - End: my_function (Duration: 1.23s)
```

#### Multi-Level Logging

- **`app.log`**: All levels including DEBUG
- **`app_no_debug.log`**: INFO and above only  
- **Console**: INFO and above with color coding

## 🔄 Data Flow Patterns

### 1. Application Startup Flow

```
main.py
├── setup_logging()
├── create_database() 
│   ├── Create tables if not exist
│   ├── Set up foreign key constraints
│   └── Insert default data
└── Homepage()
    ├── BaseWindow.__init__()
    ├── Load homepage plugins
    ├── init_ui() → Create account widgets
    └── mainloop()
```

### 2. User Interaction Flow

```
User Click → Plugin Menu Item → Window Creation → Database Query → UI Update
     ▲                                                                 │
     │                                                                 │
     └─────────────────── User sees updated data ◄───────────────────┘
```

### 3. Database Operations Flow

```
GUI Component → Domain Utility Function → DatabaseConnection → SQLite
     ▲               │                            │               │
     │               │ @log_fn decorator          │ Singleton     │
     │               │ Parameterized query       │ Pattern       │
     │               ▼                            ▼               │
User sees ← Data Processing ← Query Results ← Execute Query ←────┘
```

## 🧩 Design Patterns Used

### 1. **Singleton Pattern**
- **Where**: `DatabaseConnection` class
- **Why**: Prevents SQLite connection conflicts
- **Implementation**: Static methods with class-level instance storage

### 2. **Template Method Pattern**
- **Where**: `BaseWindow` and `BaseToplevelWindow`
- **Why**: Consistent window initialization while allowing customization
- **Implementation**: Base class calls `init_ui()` after setup

### 3. **Plugin Pattern** 
- **Where**: Menu extension system
- **Why**: Extensibility without core code modification
- **Implementation**: Dynamic module loading with naming conventions

### 4. **Decorator Pattern**
- **Where**: Logging with `@log_fn`
- **Why**: Automatic timing and debug information
- **Implementation**: Function wrapper with timing capture

### 5. **Factory Pattern** (Implicit)
- **Where**: Window creation in plugins
- **Why**: Consistent window instantiation
- **Implementation**: Standard constructors with base class initialization

## 🎯 Architectural Benefits

### For Developers
- **Modularity**: Changes isolated to specific components
- **Consistency**: Base classes ensure uniform behavior
- **Extensibility**: Plugin system allows new features
- **Debuggability**: Comprehensive logging with timing

### For Users  
- **Performance**: Singleton database connection
- **Reliability**: Consistent error handling and logging
- **Usability**: Standardized UI patterns and navigation
- **Maintainability**: Clear separation of concerns

## 🔮 Extension Points

The architecture provides several extension mechanisms:

1. **New Windows**: Inherit from base classes for consistency
2. **New Plugins**: Follow naming convention for automatic loading
3. **New Database Tables**: Add to `createdatabase_utils.py` with utilities
4. **New Utilities**: Organize by domain with `@log_fn` decorators
5. **New Configuration**: Add to `config.py` classes

## 📈 Future Architecture Considerations

As the application grows, consider:

- **Plugin Type Extension**: Beyond menu plugins (toolbars, widgets)
- **Configuration Externalization**: JSON/YAML config files
- **Database Migration System**: Schema versioning and updates  
- **Event System**: Decoupled communication between components
- **Theme System**: User-customizable UI themes

---

*This architecture balances simplicity with extensibility, making it easy for developers to understand and extend while maintaining consistency and reliability.*