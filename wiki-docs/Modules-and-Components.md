# Modules & Components

This document provides detailed information about all modules, classes, and functions in the Budget Planner codebase, organized by functional area.

## 📁 Project Structure

```
src/
├── main.py                 # Application entry point
├── config.py              # Configuration settings
├── gui/                   # User interface components
│   ├── basewindow.py      # Base window class
│   ├── basetoplevelwindow.py  # Base top-level window
│   ├── homepage/          # Main application window
│   ├── transactionpage/   # Transaction management
│   ├── accountpage/       # Account management
│   ├── cashpage/          # Cash flow management
│   ├── overview/          # Financial overview
│   ├── budget_suggestion/ # AI budget suggestions
│   └── plugins/           # Plugin system
└── utils/                 # Utility modules
    ├── data/              # Data handling and database
    ├── logging/           # Logging system
    └── ai/                # AI-powered features
```

## 🚀 Application Entry Point

### `main.py`

**Purpose**: Application bootstrap and entry point management.

#### Key Functions:

```python
@log_fn
def main() -> None:
    """Main application entry point - launches the homepage GUI"""
```

```python
def main_test() -> None:
    """Test mode for GUI component testing"""
```

```python
def main_fn_test() -> None:
    """Test mode for database function testing"""
```

**Design Pattern**: The main module uses a clean bootstrap pattern with separate test modes for development.

**Key Features**:
- **Logging Setup**: Configures comprehensive logging before application start
- **Database Initialization**: Ensures database exists and is properly configured
- **Test Modes**: Multiple test configurations for different development needs
- **Configuration Management**: Handles test vs. production configuration switching

## ⚙️ Configuration Module

### `config.py`

**Purpose**: Centralized configuration management for paths and settings.

#### Classes:

```python
class Database:
    PATH = Path(__file__).resolve().parent.parent / 'data' / 'database.db'
```

```python
class Logging:
    LOG_DIR = Path(__file__).resolve().parent.parent / 'log'
    LOG_FILE = LOG_DIR / 'app.log'
    LOG_FILE_NO_DEBUG = LOG_DIR / 'app_no_debug.log'
    
    @staticmethod
    def ensure_log_directory_exists():
        """Creates log directory if it doesn't exist"""
```

**Design Decisions**:
- **Path Resolution**: Uses `Path(__file__).resolve()` for reliable path calculation
- **Static Methods**: Utility methods for directory management
- **Centralized Settings**: Single source of truth for all application paths

## 🖥️ GUI Framework

### Base Window System

#### `basewindow.py` - Core GUI Foundation

**Purpose**: Provides the foundational window class that all GUI components inherit from.

```python
class BaseWindow(tk.Tk):
    def __init__(self, plugin_scope: str, title: str = "Fenster",
                 geometry: str = "800x600", bg_color: str = "white",
                 fullscreen: bool = False) -> None:
```

**Key Methods**:

```python
def _setup_main_frame(self) -> None:
    """Creates the main content frame"""

def _setup_status_bar(self) -> None:
    """Creates status bar for user feedback"""

def _setup_menu(self) -> None:
    """Initializes menu bar and loads plugins"""

@log_fn
def init_ui(self) -> None:
    """Abstract method - must be implemented by subclasses"""

@log_fn
def show_message(self, message: str) -> None:
    """Displays popup message to user"""

@log_fn
def ask_permission(self, message: str, focus_on: List[bool]) -> None:
    """Shows permission dialog with yes/no options"""
```

**Design Patterns**:
- **Template Method**: `init_ui()` must be implemented by subclasses
- **Plugin Integration**: Automatic plugin loading based on scope
- **Style Management**: Consistent theming across all windows

#### `basetoplevelwindow.py` - Top-Level Window Base

**Purpose**: Base class for secondary windows and dialogs.

**Key Features**:
- **Modal Dialog Support**: Built-in modal dialog functionality
- **Parent-Child Relationships**: Proper window hierarchy management
- **Consistent Styling**: Inherits styling from main application

### Application Windows

#### `homepage/homepage.py` - Main Application Window

**Purpose**: Primary application interface showing financial dashboard.

```python
class Homepage(BaseWindow):
    def __init__(self, fullscreen: bool = False) -> None:
        super().__init__(plugin_scope="homepage", 
                        title="Budget Planner - Homepage")
```

**Key Methods**:

```python
def create_account_widget(self, row: int, column: int, 
                         account_name: str, current_value: float = 0.0,
                         difference_value: float = 0.0) -> None:
    """Creates visual widget for account display"""

def update_account_values(self, widget_position: int, 
                         current_value: float, difference_value: float) -> None:
    """Updates account widget with new values"""

def set_budget(self, amount: float) -> None:
    """Updates budget display with color coding"""

def open_budget_suggestions(self):
    """Launches AI budget suggestion dialog"""
```

**UI Components**:
- **Budget Display**: Large, color-coded budget amount
- **Account Widgets**: Dynamic grid of account balance widgets
- **AI Integration**: Budget suggestion button (future feature)
- **Navigation**: Plugin-based menu system

**Data Flow**:
1. **Initialization**: Loads account data from database
2. **Widget Creation**: Dynamically creates account widgets based on data
3. **Real-time Updates**: Updates widget values and colors based on balance changes
4. **User Interaction**: Handles menu clicks and button presses

## 🔌 Plugin System

### `plugins/__init__.py` - Plugin Loader

**Purpose**: Dynamic plugin discovery and loading system.

```python
@log_fn
def load_plugins(plugin_type: str, plugin_scope: str):
    """Loads plugins based on naming convention and scope"""
```

**Plugin Naming Convention**:
```
plugin_<scope>_<type>_<name>.py
```

**Examples**:
- `plugin_all_menu_help.py` - Global help menu
- `plugin_homepage_menu_account.py` - Homepage-specific account menu

**Loading Process**:
1. **File Discovery**: Scans plugin directories recursively
2. **Name Parsing**: Extracts scope, type, and name from filename
3. **Scope Matching**: Loads plugins matching current scope or "all"
4. **Dynamic Import**: Uses `importlib` for runtime loading
5. **Sorting**: Orders plugins by `menu_id` attribute
6. **Error Handling**: Gracefully handles plugin load failures

**Plugin Interface**:
```python
# Example plugin structure
menu_id = 100  # Ordering for menu items

def add_to_menu(parent_window, menu_bar):
    """Called by BaseWindow to integrate plugin into menu"""
    # Plugin implementation
```

## 💾 Data Layer

### Database Connection Management

#### `utils/data/database_connection.py`

**Purpose**: Centralized database connection and cursor management.

```python
class DatabaseConnection:
    _connection = None
    _cursor = None
    
    @staticmethod
    def get_connection(db_path: Path) -> sqlite3.Connection:
        """Returns singleton database connection"""
    
    @staticmethod
    def get_cursor(db_path: Path) -> sqlite3.Cursor:
        """Returns database cursor for the connection"""
    
    @staticmethod
    def close_connection():
        """Properly closes connection and cursor"""
```

**Design Benefits**:
- **Singleton Pattern**: Reuses database connections efficiently
- **Resource Management**: Proper cleanup of database resources
- **Thread Safety**: Safe for single-threaded GUI application

### Database Schema Management

#### `utils/data/createdatabase_utils.py`

**Purpose**: Database schema creation and initial data population.

**Key Functions**:

```python
@log_fn
def create_database(db_path: Path = config.Database.PATH) -> None:
    """Creates complete database schema with tables and indexes"""
```

**Table Creation Functions**:
- `create_transactions_table()` - Core transaction data
- `create_account_table()` - Account information
- `create_category_table()` - Transaction categories
- `create_counterparty_table()` - Transaction counterparties
- `create_account_history_table()` - Balance history tracking

**Initial Data Functions**:
- `insert_initial_categories()` - Default transaction categories
- `insert_initial_budget_periods()` - Budget time periods
- `insert_initial_transaction_types()` - Default transaction types

### Database Utility Modules

#### Account Management (`utils/data/database/account_utils.py`)

**Key Functions**:

```python
def get_account_data() -> List[Tuple]:
    """Retrieves all account data for homepage display"""

def get_total_cash() -> float:
    """Calculates total cash across all accounts"""

def create_account(name: str, number: str, position: int) -> int:
    """Creates new account and returns ID"""

def update_account_balance(account_id: int, new_balance: float):
    """Updates account balance and records history"""
```

#### Transaction Management (`utils/data/database/transaction_utils.py`)

**Key Functions**:

```python
def add_transaction(account_id: int, amount: float, 
                   purpose: str, date: str, **kwargs) -> int:
    """Adds new transaction and returns ID"""

def get_transactions_by_account(account_id: int, 
                              start_date: str = None, 
                              end_date: str = None) -> List[Tuple]:
    """Retrieves transactions for specified account and date range"""

def update_transaction_category(transaction_id: int, category_id: int):
    """Updates transaction category for budgeting"""
```

#### Category Management (`utils/data/database/category_utils.py`)

**Key Functions**:

```python
def get_all_categories() -> List[Tuple]:
    """Retrieves all available categories"""

def create_category(name: str, budget: float = 0.0, 
                   period_id: int = 3) -> int:
    """Creates new category with budget settings"""

def get_category_spending(category_id: int, period: str) -> float:
    """Calculates spending for category in specified period"""
```

## 📊 Data Processing Utilities

### Date Utilities (`utils/data/date_utils.py`)

**Purpose**: Date formatting and manipulation functions.

**Key Functions**:

```python
def get_month_literal() -> str:
    """Returns current month in German locale format"""

def format_date_for_db(date: datetime) -> str:
    """Formats date for database storage (YYYY-MM-DD)"""

def parse_date_from_user(date_str: str) -> datetime:
    """Parses user-entered date with flexible formats"""
```

### Value Utilities (`utils/data/value_utils.py`)

**Purpose**: Financial value formatting and calculation utilities.

**Key Functions**:

```python
def format_currency(amount: float, currency: str = "€") -> str:
    """Formats amount as currency string with locale"""

def parse_user_amount(amount_str: str) -> float:
    """Parses user-entered amount with error handling"""

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculates percentage change between two values"""
```

## 📝 Logging System

### Logging Configuration (`utils/logging/logger_config.py`)

**Purpose**: Centralized logging setup and configuration.

```python
def setup_logging():
    """Configures logging handlers, formatters, and output destinations"""
```

**Logging Outputs**:
- **Console Handler**: Real-time output during development
- **File Handler (app.log)**: Complete log with DEBUG level
- **File Handler (app_no_debug.log)**: Production log with INFO+ levels

**Log Format**:
```
%(asctime)s - %(name)s - [%(levelname)s] - %(message)s
```

### Logging Decorator (`utils/logging/logging_tools.py`)

**Purpose**: Function-level logging with automatic timing.

```python
def log_fn(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator for automatic function entry/exit logging with timing"""
```

**Features**:
- **Automatic Logging**: No manual logging code required in functions
- **Performance Timing**: Measures and logs function execution time
- **Exception Safety**: Continues logging even if function raises exceptions
- **Consistent Format**: Standardized log message format

## 🤖 AI Integration

### Budget Suggestions (`utils/ai/budget_suggestions.py`)

**Purpose**: AI-powered budget recommendation system (future implementation).

**Planned Features**:
- **Spending Analysis**: Pattern recognition in transaction history
- **Budget Recommendations**: AI-generated budget suggestions
- **Trend Analysis**: Identification of spending trends and anomalies
- **Personalization**: User-specific recommendation tuning

## 📋 Data Import/Export

### MT940 Import (`utils/data/mt940import_utils.py`)

**Purpose**: Import bank statements in MT940 format.

**Key Features**:
- **Format Parsing**: Handles standard MT940 bank statement format
- **Transaction Mapping**: Maps bank data to application transaction format
- **Duplicate Detection**: Prevents duplicate transaction imports
- **Error Handling**: Graceful handling of malformed MT940 files

## 🔧 Development Utilities

### Dependency Graph (`dependencygraph.py`)

**Purpose**: Visualizes module dependencies for code analysis.

**Features**:
- **Module Discovery**: Scans Python files for import relationships
- **Dependency Visualization**: Generates visual dependency graphs
- **Isolation Detection**: Identifies modules with no dependencies
- **Manual Relationship Addition**: Interactive dependency modification

**Usage**:
```python
def main():
    # Interactive file selection for source directory and main file
    # Generates networkx graph of module dependencies
    # Creates visual representation of code structure
```

## 🎯 Code Organization Patterns

### Common Patterns Used

#### 1. Decorator Pattern
- **@log_fn**: Automatic function logging
- **Error Handling**: Centralized exception management
- **Performance Monitoring**: Built-in timing measurements

#### 2. Template Method Pattern
- **BaseWindow.init_ui()**: Subclasses implement specific UI initialization
- **Plugin Interface**: Standardized plugin integration methods

#### 3. Singleton Pattern
- **DatabaseConnection**: Single connection instance
- **Configuration**: Centralized settings access

#### 4. Factory Pattern
- **Widget Creation**: Dynamic GUI component creation
- **Plugin Loading**: Runtime plugin instantiation

#### 5. Observer Pattern (Implicit)
- **GUI Updates**: Database changes trigger UI updates
- **Status Updates**: Operations update status bar

### Naming Conventions

#### Database Tables
- **Prefix**: `tbl_` for all table names
- **Primary Keys**: `i8_<TableName>ID`
- **Foreign Keys**: `i8_<ReferencedTable>ID`
- **String Fields**: `str_<FieldName>`
- **Numeric Fields**: `real_<FieldName>` or `i8_<FieldName>`

#### Python Modules
- **Snake Case**: All module and function names
- **Descriptive Names**: Clear purpose indication
- **Utility Suffix**: `_utils.py` for utility modules

#### GUI Components
- **Class Names**: PascalCase (e.g., `BaseWindow`, `Homepage`)
- **Widget Variables**: Descriptive names with component type
- **Event Handlers**: Verb-based names (e.g., `open_budget_suggestions`)

### Error Handling Strategy

#### Custom Exceptions
```python
class Error(Exception):
    """Base exception class for application-specific errors"""
    pass
```

#### Exception Propagation
- **GUI Layer**: User-friendly error messages with technical details in logs
- **Data Layer**: Detailed error information with context
- **Plugin Layer**: Isolated failures don't crash the main application

---

This comprehensive overview of modules and components provides the foundation for understanding and extending the Budget Planner codebase. Each module is designed with specific responsibilities and clear interfaces for maximum maintainability and extensibility.