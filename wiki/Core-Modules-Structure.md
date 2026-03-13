# Core Modules & Structure

This document provides a detailed breakdown of the Budget Planner's core modules, their responsibilities, and interactions.

## 📁 Project Structure

```
src/
├── main.py                    # Application entry point
├── config.py                  # Configuration management
├── gui/                       # User interface components
│   ├── basewindow.py          # Base class for main windows
│   ├── basetoplevelwindow.py  # Base class for modal dialogs
│   ├── homepage/              # Main application window
│   ├── accountpage/           # Account management windows
│   ├── transactionpage/       # Transaction management windows
│   ├── cashpage/              # Cash flow analysis
│   ├── overview/              # Data overview and reports
│   ├── budget_suggestion/     # AI budget suggestions
│   └── plugins/               # Plugin system
└── utils/                     # Utility modules
    ├── data/                  # Data handling and database
    ├── logging/               # Logging configuration
    └── ai/                    # AI/ML features (basic)
```

## 🏗️ Core Module Breakdown

### 1. Application Entry (`src/main.py`)

**Purpose**: Bootstrap and lifecycle management

```python
@log_fn
def main() -> None:
    """Main application entry point"""
    from gui.homepage.homepage import Homepage
    from utils.data.createdatabase_utils import create_database
    
    logger.info("APPLICATION STARTED")
    create_database()           # Initialize database schema
    app = Homepage(fullscreen=True)
    app.run()                  # Start GUI event loop
```

**Functions:**
- `main()`: Production mode application launch
- `main_test()`: Test mode with specific window testing  
- `main_fn_test()`: Function-level testing mode

**Dependencies**: 
- `gui.homepage.homepage.Homepage`
- `utils.data.createdatabase_utils.create_database`
- `config` (via logging setup)

### 2. Configuration (`src/config.py`)

**Purpose**: Centralized configuration management

```python
class Database:
    PATH = Path(__file__).resolve().parent.parent / 'data' / 'database.db'

class Logging:
    LOG_DIR = Path(__file__).resolve().parent.parent / 'log'
    log_file_name = 'app.log'
    log_file_name_no_debug = 'app_no_debug.log'
    
    @staticmethod
    def ensure_log_directory_exists():
        Logging.LOG_DIR.mkdir(parents=True, exist_ok=True)
```

**Key Features:**
- Cross-platform path handling with `pathlib`
- Runtime log directory creation
- Centralized path management
- Easy configuration modification

## 🖥️ GUI Module (`src/gui/`)

### Base Classes

#### BaseWindow (`src/gui/basewindow.py`)

**Purpose**: Foundation for all main application windows

```python
class BaseWindow(tk.Tk):
    def __init__(self, plugin_scope: str, title: str = "Fenster",
                 geometry: str = "800x600", bg_color: str = "white",
                 fullscreen: bool = False):
        super().__init__()
        self.plugin_scope = plugin_scope
        # Automatic setup sequence
        self._apply_styles()      # TTK theme configuration
        self._setup_main_frame()  # Main content area
        self._setup_status_bar()  # Bottom status bar
        self._setup_menu()        # Menu bar with plugins
        self.init_ui()           # Custom UI (must implement)
```

**Key Methods:**
- `init_ui()`: **Abstract method** - Must be implemented by subclasses
- `show_message(message: str)`: Standard message popup
- `ask_permission(message: str, focus_on: List[bool])`: Permission dialog
- `reload()`: Refresh UI by destroying and recreating components
- `run()`: Start the main event loop

**Plugin Integration:**
```python
def _setup_menu(self):
    menu_bar = tk.Menu(self)
    for plugin in load_plugins("menu", self.plugin_scope):
        if hasattr(plugin, "add_to_menu"):
            plugin.add_to_menu(self, menu_bar)
```

#### BaseToplevelWindow (`src/gui/basetoplevelwindow.py`)

**Purpose**: Foundation for modal dialogs and popup windows

```python
class BaseToplevelWindow(tk.Toplevel):
    def __init__(self, master: BaseWindow, plugin_scope: str = "",
                 title: str = "Fenster", geometry: str = "600x400",
                 bg_color: str = "white"):
        super().__init__(master)
        # Similar setup to BaseWindow but as modal dialog
```

**Key Differences from BaseWindow:**
- Inherits from `tk.Toplevel` instead of `tk.Tk`
- Requires `master` window parameter
- Modal dialog behavior
- Smaller default geometry

### Specialized Windows

#### Homepage (`src/gui/homepage/homepage.py`)

**Purpose**: Main application interface showing account widgets

```python
class Homepage(BaseWindow):
    def __init__(self, fullscreen: bool = False):
        self.account_widgets = {}  # Store widget references
        super().__init__(plugin_scope="homepage", 
                        title="Budget Planner - Homepage",
                        fullscreen=fullscreen)
    
    def init_ui(self):
        # Create account widgets from database
        account_data = get_account_data(selected_columns=[...])
        for account in account_data:
            self._create_account_widget(account)
```

**Key Features:**
- Dynamic account widget creation from database
- Plugin scope "homepage" for specialized menu items
- Fullscreen support
- Account data visualization

#### TransactionPage (`src/gui/transactionpage/transactionpage.py`)

**Purpose**: Transaction entry and editing interface

```python
class TransactionPage(BaseToplevelWindow):
    def __init__(self, parent: BaseWindow, plugin_scope: str):
        # Load data for dropdowns
        self.account_data = get_account_data(selected_columns=[...])
        self.counterparty_data = get_counterparty_data()
        self.category_data = get_category_data(selected_columns=[...])
        super().__init__(parent, plugin_scope, title="Transaction Page")
    
    def save_transaction(self):
        # Validate and save transaction data
        pass
```

**Key Features:**
- Form-based transaction entry
- Dropdown population from database
- Input validation and placeholder text
- Integration with account, counterparty, and category data

### Plugin System (`src/gui/plugins/`)

#### Plugin Loader (`src/gui/plugins/__init__.py`)

**Purpose**: Dynamic plugin loading and management

```python
@log_fn
def load_plugins(plugin_type: str, plugin_scope: str):
    """Load plugins based on naming convention and scope"""
    plugins = []
    
    # Scan directory for plugin files
    for filename in files:
        parts = filename[:-3].split("_")  # Remove .py extension
        prefix, scope, p_type, name = parts[:4]
        
        if prefix == "plugin" and p_type == plugin_type:
            if scope == "all" or scope == plugin_scope:
                # Dynamic import
                module = importlib.import_module(module_name)
                menu_id = getattr(module, "menu_id", 9999)
                plugins.append((scope, menu_id, module))
    
    # Sort by menu_id for consistent ordering
    return sorted(plugins, key=lambda item: item[1])
```

**Plugin Naming Convention:**
```
plugin_{scope}_{type}_{name}.py
```

**Example Plugin Structure:**
```python
# plugin_homepage_menu_account.py
menu_id = 10  # Controls menu ordering

def add_to_menu(window, menu_bar):
    """Add menu items to the menu bar"""
    account_menu = tk.Menu(menu_bar, tearoff=0)
    account_menu.add_command(label="Add Account", 
                           command=lambda: open_account_page(window))
    menu_bar.add_cascade(label="Account", menu=account_menu)
```

## 🗃️ Data Module (`src/utils/data/`)

### Database Connection (`src/utils/data/database_connection.py`)

**Purpose**: Singleton database connection management

```python
class DatabaseConnection:
    _instance: Optional[sqlite3.Connection] = None
    _cursor: Optional[sqlite3.Cursor] = None
    
    @staticmethod
    def get_connection(db_path: Path = config.Database.PATH) -> sqlite3.Connection:
        """Returns singleton database connection"""
        if DatabaseConnection._instance is None:
            DatabaseConnection._instance = sqlite3.connect(db_path)
            logger.info(f"Database connection created: {db_path}")
        return DatabaseConnection._instance
```

**Key Methods:**
- `get_connection()`: Get/create singleton connection
- `get_cursor()`: Get/create singleton cursor
- `close_cursor()`: Close cursor safely
- `close_connection()`: Close connection and cursor safely

**Benefits:**
- Prevents SQLite locking issues
- Consistent database access
- Automatic connection reuse
- Proper cleanup methods

### Database Schema (`src/utils/data/createdatabase_utils.py`)

**Purpose**: Database schema creation and management

**Core Tables:**
```sql
-- Accounts
CREATE TABLE tbl_Account (
    i8_AccountID INTEGER PRIMARY KEY AUTOINCREMENT,
    i8_WidgetPosition INTEGER UNIQUE,
    str_AccountName TEXT UNIQUE NOT NULL,
    str_AccountNumber TEXT,
    real_AccountBalance REAL NOT NULL DEFAULT 0.0,
    -- Foreign keys and constraints
);

-- Transactions  
CREATE TABLE tbl_Transaction (
    i8_TransactionID INTEGER PRIMARY KEY AUTOINCREMENT,
    i8_AccountID INTEGER NOT NULL,
    str_Date TEXT NOT NULL,
    real_Amount REAL NOT NULL,
    str_Purpose TEXT NOT NULL,
    -- Foreign key relationships
    FOREIGN KEY (i8_AccountID) REFERENCES tbl_Account(i8_AccountID) ON DELETE CASCADE
);

-- Categories, Counterparties, etc.
```

**Key Features:**
- Foreign key constraints with proper cascading
- Default values and data types
- Unique constraints for data integrity
- Automatic ID generation

### Database Utilities (`src/utils/data/database/`)

**Organization by Domain:**

#### Account Utilities (`account_utils.py`)

```python
@log_fn
def get_account_data(selected_columns: List[bool] = None) -> List[Tuple]:
    """Get account data with column selection"""
    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor()
    
    # Build dynamic query based on selected columns
    columns = ["i8_AccountID", "str_AccountName", "real_AccountBalance", ...]
    selected = [col for i, col in enumerate(columns) if selected_columns[i]]
    
    cursor.execute(f"SELECT {', '.join(selected)} FROM tbl_Account")
    return cursor.fetchall()

@log_fn
def add_account(account_name: str, account_number: str = "") -> bool:
    """Add new account with validation"""
    # Implementation with parameterized queries
```

**Common Patterns:**
- `@log_fn` decorator for timing
- Parameterized queries only
- Column selection with boolean lists
- Consistent return types (List[Tuple])
- Exception handling with custom exception classes

#### Transaction Utilities (`transaction_utils.py`)
#### Category Utilities (`category_utils.py`)
#### Counterparty Utilities (`counterparty_utils.py`)

**Similar structure for each domain with CRUD operations**

### Date & Value Utilities

#### Date Utils (`src/utils/data/date_utils.py`)
```python
def get_iso_date(day: str = "", month: str = "", year: str = "") -> str:
    """Convert date components to ISO format YYYY-MM-DD"""

def get_month_literal(month_number: int) -> str:
    """Convert month number to German literal"""
```

#### Value Utils (`src/utils/data/value_utils.py`)
```python
def format_currency(amount: float, currency: str = "EUR") -> str:
    """Format currency with locale-specific formatting"""
```

## 📝 Logging Module (`src/utils/logging/`)

### Logger Configuration (`src/utils/logging/logger_config.py`)

**Purpose**: Multi-level logging setup

```python
def setup_logging():
    """Configure logging with multiple handlers"""
    # Console handler (INFO+)
    console_handler = logging.StreamHandler()
    
    # File handler all levels (DEBUG+)  
    file_handler = logging.FileHandler(config.Logging.LOG_FILE)
    
    # File handler no debug (INFO+)
    file_handler_no_debug = logging.FileHandler(config.Logging.LOG_FILE_NO_DEBUG)
    
    # Apply formatters and configure root logger
```

**Output Targets:**
- **Console**: INFO+ with color formatting
- **`app.log`**: All levels including DEBUG
- **`app_no_debug.log`**: INFO+ only for production monitoring

### Logging Tools (`src/utils/logging/logging_tools.py`)

**Purpose**: Decorator-based function timing

```python
def log_fn(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to log function start/end with timing"""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.debug(f'Start: {func.__name__}')
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug(f'End: {func.__name__} (Duration: {end - start:.2f}s)')
        return result
    return wrapper
```

**Usage Pattern:**
```python
@log_fn
def my_database_function():
    # Function automatically timed and logged
    pass
```

## 🤖 AI Module (`src/utils/ai/`)

**Purpose**: Basic budget suggestions and analysis

```python
# budget_suggestions.py
def generate_budget_suggestions(account_data, transaction_history):
    """Basic rule-based budget suggestions"""
    # Simple analysis and recommendations
```

**Current Features:**
- Rule-based budget analysis
- Basic spending pattern recognition
- Simple recommendations

**Future Extension Points:**
- Machine learning integration
- Advanced analytics
- Predictive modeling

## 🔗 Module Dependencies

### Dependency Flow
```
main.py
├── config
├── gui.homepage.homepage
│   ├── gui.basewindow
│   │   └── gui.plugins
│   └── utils.data.database.account_utils
└── utils.data.createdatabase_utils
    └── utils.data.database_connection
```

### Import Patterns

**Standard Pattern:**
```python
import logging
from pathlib import Path
from typing import List, Tuple, Optional

from utils.logging.logging_tools import log_fn
from utils.data.database_connection import DatabaseConnection
import config

logger = logging.getLogger(__name__)
```

**GUI Imports:**
```python
import tkinter as tk
from tkinter import ttk

from gui.basewindow import BaseWindow
from gui.basetoplevelwindow import BaseToplevelWindow
```

## 📊 Module Interaction Patterns

### 1. GUI → Database Flow
```
GUI Component → Domain Utility → DatabaseConnection → SQLite
```

### 2. Plugin → Window Flow  
```
Plugin Load → Menu Creation → User Action → Window Creation
```

### 3. Data → UI Flow
```
Database Query → Data Processing → Widget Update → User Display
```

## 🔧 Extension Points

### Adding New Modules

1. **New GUI Window**: Inherit from base classes, implement `init_ui()`
2. **New Database Table**: Add to `createdatabase_utils.py`, create utilities module
3. **New Plugin Type**: Extend plugin loader, define interface methods
4. **New Utility Domain**: Create module in appropriate subdirectory
5. **New Configuration**: Add classes to `config.py`

### Module Guidelines

- **Single Responsibility**: Each module has one clear purpose
- **Consistent Patterns**: Follow existing import, naming, and structure patterns
- **Logging Integration**: Use `@log_fn` for significant functions
- **Type Hints**: Required for all function parameters and returns
- **Documentation**: Docstrings with Args/Returns sections

---

*This modular structure makes the codebase easy to navigate, understand, and extend while maintaining consistency and reliability.*