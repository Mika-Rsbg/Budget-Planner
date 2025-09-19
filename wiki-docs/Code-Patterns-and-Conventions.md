# Code Patterns & Conventions

This document outlines the coding patterns, conventions, and design decisions used throughout the Budget Planner codebase. Following these patterns ensures consistency, maintainability, and easier collaboration.

## 🏗️ Architectural Patterns

### 1. Layered Architecture

The application follows a strict layered architecture with clear separation of concerns:

```
┌─────────────────────┐
│    Presentation     │  ← GUI components, user interaction
│     (gui/)          │
├─────────────────────┤
│     Business        │  ← Application logic, data processing
│     (utils/)        │
├─────────────────────┤
│      Data           │  ← Database access, file I/O
│  (utils/data/)      │
└─────────────────────┘
```

**Rules**:
- **No upward dependencies**: Lower layers never import from higher layers
- **Clear interfaces**: Well-defined boundaries between layers
- **Single responsibility**: Each layer has a specific purpose

### 2. Template Method Pattern

Used extensively in the GUI framework:

```python
class BaseWindow(tk.Tk):
    def __init__(self, plugin_scope: str, **kwargs):
        super().__init__()
        self._setup_main_frame()    # Template method
        self._setup_status_bar()    # Template method
        self._setup_menu()          # Template method
        self.init_ui()             # Abstract method - implemented by subclasses

    @log_fn
    def init_ui(self) -> None:
        """Abstract method - must be implemented by subclasses"""
        raise NotImplementedError("init_ui() needs to be implemented in subclasses")
```

**Benefits**:
- **Consistent initialization**: All windows follow same setup pattern
- **Customization points**: Subclasses only implement what's unique
- **Framework control**: Base class controls the overall process

### 3. Decorator Pattern

Used for cross-cutting concerns like logging:

```python
@log_fn
def critical_function():
    """Function with automatic logging"""
    # Business logic here
```

**Implementation**:
```python
def log_fn(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.debug(f'Start: {func.__name__}')
        start: float = time.time()
        result: Any = func(*args, **kwargs)
        end: float = time.time()
        logger.debug(f'End: {func.__name__} (Duration: {end - start:.2f}s)')
        return result
    return wrapper
```

### 4. Plugin Architecture

Convention-based plugin discovery and loading:

```python
# File naming convention: plugin_<scope>_<type>_<name>.py
# Example: plugin_homepage_menu_account.py

menu_id = 100  # Controls ordering

def add_to_menu(parent_window, menu_bar):
    """Standard plugin interface"""
    pass
```

## 🎨 Coding Conventions

### Python Style Guidelines

#### Naming Conventions

**Variables and Functions**:
```python
# Use snake_case for variables and functions
account_balance = 1000.0
transaction_count = 0

def get_account_data():
    return []

def calculate_total_balance():
    return 0.0
```

**Classes**:
```python
# Use PascalCase for class names
class BaseWindow:
    pass

class TransactionManager:
    pass

class DatabaseConnection:
    pass
```

**Constants**:
```python
# Use UPPER_SNAKE_CASE for constants
MAX_RETRY_ATTEMPTS = 3
DEFAULT_CURRENCY = "EUR"
DATABASE_VERSION = 1
```

**Private Members**:
```python
class ExampleClass:
    def __init__(self):
        self._private_var = "internal use"  # Single underscore for internal use
        self.__very_private = "name mangled"  # Double underscore for name mangling
```

#### Database Naming Conventions

**Table Names**:
```sql
-- Prefix with tbl_ and use PascalCase
CREATE TABLE tbl_Transaction (...);
CREATE TABLE tbl_Account (...);
CREATE TABLE tbl_Category (...);
```

**Column Names**:
```sql
-- Use type prefix and descriptive names
i8_TransactionID        -- Integer (8-bit conceptually)
str_AccountName         -- String/Text field
real_AccountBalance     -- Real/Float field
```

**Index Names**:
```sql
-- Descriptive names with idx_ prefix
CREATE INDEX idx_transaction_account_date ON tbl_Transaction(i8_AccountID, str_Date);
CREATE INDEX idx_account_widget_position ON tbl_Account(i8_WidgetPosition);
```

### Import Organization

Organize imports in three groups with blank lines between:

```python
# Standard library imports
import os
import sys
import logging
import sqlite3
from typing import List, Tuple, Optional
from pathlib import Path

# Third-party imports
import tkinter as tk
from tkinter import ttk, messagebox

# Local application imports
from utils.logging.logging_tools import log_fn
from utils.data.database_connection import DatabaseConnection
from gui.basewindow import BaseWindow
import config
```

### Function Documentation

Use consistent docstring format:

```python
@log_fn
def get_transactions_by_category(category_id: int, 
                                start_date: str = None, 
                                end_date: str = None) -> List[Tuple]:
    """
    Retrieve transactions for a specific category within date range.
    
    This function queries the database for transactions belonging to the specified
    category, optionally filtered by date range. Results are ordered by date.
    
    Args:
        category_id (int): The unique identifier for the category
        start_date (str, optional): Start date in YYYY-MM-DD format. 
                                   If None, no start date filter is applied.
        end_date (str, optional): End date in YYYY-MM-DD format.
                                 If None, no end date filter is applied.
    
    Returns:
        List[Tuple]: List of transaction tuples containing:
                    (transaction_id, date, amount, purpose, account_name)
    
    Raises:
        sqlite3.Error: If database query fails
        ValueError: If category_id is invalid or dates are malformed
    
    Example:
        >>> transactions = get_transactions_by_category(1, "2024-01-01", "2024-01-31")
        >>> print(f"Found {len(transactions)} transactions")
    """
    # Implementation here
```

## 🗄️ Database Patterns

### Connection Management

Always use the centralized connection manager:

```python
# Good: Use the connection manager
from utils.data.database_connection import DatabaseConnection

def database_operation():
    conn = DatabaseConnection.get_connection()
    cursor = DatabaseConnection.get_cursor()
    
    try:
        cursor.execute("SELECT * FROM tbl_Account")
        return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        DatabaseConnection.close_cursor()
```

```python
# Avoid: Direct connection management
import sqlite3

def bad_database_operation():
    conn = sqlite3.connect("database.db")  # Don't do this
    # ... operations
    conn.close()
```

### Query Patterns

#### Parameterized Queries
Always use parameterized queries to prevent SQL injection:

```python
# Good: Parameterized query
def get_account_by_id(account_id: int):
    cursor.execute(
        "SELECT * FROM tbl_Account WHERE i8_AccountID = ?", 
        (account_id,)
    )
    
# Bad: String interpolation
def bad_get_account_by_id(account_id: int):
    cursor.execute(
        f"SELECT * FROM tbl_Account WHERE i8_AccountID = {account_id}"  # SQL injection risk
    )
```

#### Dynamic Query Building
For complex queries with optional parameters:

```python
def get_transactions_filtered(account_id: int = None, 
                             start_date: str = None, 
                             end_date: str = None,
                             category_id: int = None) -> List[Tuple]:
    """Build query dynamically based on provided filters"""
    
    query = "SELECT * FROM tbl_Transaction t WHERE 1=1"
    params = []
    
    if account_id is not None:
        query += " AND t.i8_AccountID = ?"
        params.append(account_id)
        
    if start_date is not None:
        query += " AND t.str_Date >= ?"
        params.append(start_date)
        
    if end_date is not None:
        query += " AND t.str_Date <= ?"
        params.append(end_date)
        
    if category_id is not None:
        query += " AND t.i8_CategoryID = ?"
        params.append(category_id)
    
    query += " ORDER BY t.str_Date DESC"
    
    cursor.execute(query, params)
    return cursor.fetchall()
```

### Transaction Handling

For operations that modify multiple tables:

```python
@log_fn
def create_account_with_initial_balance(name: str, number: str, 
                                      initial_balance: float) -> int:
    """Create account and record initial balance in history"""
    
    conn = DatabaseConnection.get_connection()
    cursor = DatabaseConnection.get_cursor()
    
    try:
        # Start transaction
        cursor.execute("BEGIN")
        
        # Create account
        cursor.execute("""
            INSERT INTO tbl_Account (str_AccountName, str_AccountNumber, 
                                   real_AccountBalance, i8_WidgetPosition)
            VALUES (?, ?, ?, ?)
        """, (name, number, initial_balance, get_next_widget_position()))
        
        account_id = cursor.lastrowid
        
        # Record initial balance in history
        cursor.execute("""
            INSERT INTO tbl_AccountHistory (i8_AccountID, real_Balance, 
                                          str_RecordDate, str_ChangeDate)
            VALUES (?, ?, datetime('now'), datetime('now'))
        """, (account_id, initial_balance))
        
        # Commit transaction
        cursor.execute("COMMIT")
        logger.info(f"Created account {name} with ID {account_id}")
        return account_id
        
    except sqlite3.Error as e:
        cursor.execute("ROLLBACK")
        logger.error(f"Failed to create account {name}: {e}")
        raise
    finally:
        DatabaseConnection.close_cursor()
```

## 🖥️ GUI Patterns

### Window Inheritance Hierarchy

All windows must inherit from `BaseWindow`:

```python
class YourCustomWindow(BaseWindow):
    def __init__(self, specific_param: str):
        # Call parent constructor with plugin scope
        super().__init__(
            plugin_scope="your_scope",
            title="Your Window Title",
            geometry="800x600"
        )
        
        # Store specific parameters
        self.specific_param = specific_param
        
    def init_ui(self):
        """Required: Implement the abstract method"""
        # Create your specific UI here
        self.create_main_content()
        self.setup_event_handlers()
    
    def create_main_content(self):
        """Separate UI creation for better organization"""
        # UI creation code
        pass
    
    def setup_event_handlers(self):
        """Separate event handler setup"""
        # Event binding code
        pass
```

### Widget Organization

Use descriptive names and consistent patterns:

```python
class TransactionEntryWindow(BaseWindow):
    def init_ui(self):
        # Create main sections
        self.create_input_section()
        self.create_button_section()
        self.create_status_section()
    
    def create_input_section(self):
        """Create the input form section"""
        input_frame = ttk.Frame(self.main_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Amount input
        ttk.Label(input_frame, text="Amount:").grid(row=0, column=0, sticky=tk.W)
        self.amount_entry = ttk.Entry(input_frame)
        self.amount_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Purpose input  
        ttk.Label(input_frame, text="Purpose:").grid(row=1, column=0, sticky=tk.W)
        self.purpose_entry = ttk.Entry(input_frame)
        self.purpose_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        # Configure column weights
        input_frame.columnconfigure(1, weight=1)
    
    def create_button_section(self):
        """Create the button section"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.save_button = ttk.Button(
            button_frame, 
            text="Save Transaction",
            command=self.on_save_clicked
        )
        self.save_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.cancel_button = ttk.Button(
            button_frame,
            text="Cancel", 
            command=self.on_cancel_clicked
        )
        self.cancel_button.pack(side=tk.RIGHT)
```

### Event Handler Patterns

Use consistent naming and error handling:

```python
@log_fn
def on_save_clicked(self):
    """Handle save button click with validation and error handling"""
    
    try:
        # Validate input
        amount_str = self.amount_entry.get().strip()
        purpose = self.purpose_entry.get().strip()
        
        if not amount_str or not purpose:
            self.show_message("Please fill in all required fields")
            return
            
        # Parse and validate amount
        try:
            amount = float(amount_str)
        except ValueError:
            self.show_message("Please enter a valid amount")
            return
            
        # Update status
        self.status_var.set("Saving transaction...")
        
        # Perform the operation
        transaction_id = self.save_transaction(amount, purpose)
        
        # Success feedback
        self.status_var.set("Transaction saved successfully")
        logger.info(f"Transaction {transaction_id} saved successfully")
        
        # Close window or reset form
        self.on_transaction_saved(transaction_id)
        
    except Exception as e:
        error_msg = f"Failed to save transaction: {str(e)}"
        self.status_var.set("Save failed")
        self.show_message(error_msg)
        logger.error(error_msg)

@log_fn 
def on_cancel_clicked(self):
    """Handle cancel button click"""
    # Ask for confirmation if there are unsaved changes
    if self.has_unsaved_changes():
        # Implementation depends on specific requirements
        pass
    
    self.destroy()
```

### Color and Style Patterns

Use consistent color coding throughout the application:

```python
class StyleConstants:
    """Centralized style definitions"""
    
    # Colors for financial amounts
    POSITIVE_BG = "#ccffcc"  # Light green background
    POSITIVE_FG = "#006600"  # Dark green text
    NEGATIVE_BG = "#ffcccc"  # Light red background  
    NEGATIVE_FG = "#990000"  # Dark red text
    NEUTRAL_BG = "#f0f0f0"   # Light gray background
    
    # Standard fonts
    HEADING_FONT = ("Helvetica", 16, "bold")
    SUBHEADING_FONT = ("Helvetica", 12, "bold")
    BODY_FONT = ("Helvetica", 10)
    MONEY_FONT = ("Helvetica", 14, "bold")

def apply_money_styling(widget, amount: float):
    """Apply consistent styling to money displays"""
    if amount >= 0:
        widget.config(
            bg=StyleConstants.POSITIVE_BG,
            fg=StyleConstants.POSITIVE_FG
        )
    else:
        widget.config(
            bg=StyleConstants.NEGATIVE_BG,
            fg=StyleConstants.NEGATIVE_FG
        )
```

## 🔧 Error Handling Patterns

### Exception Hierarchy

Use custom exceptions for domain-specific errors:

```python
class BudgetPlannerError(Exception):
    """Base exception for Budget Planner specific errors"""
    pass

class DatabaseError(BudgetPlannerError):
    """Database-related errors"""
    pass

class ValidationError(BudgetPlannerError):
    """Input validation errors"""
    pass

class AccountNotFoundError(DatabaseError):
    """Specific account lookup error"""
    pass
```

### Layered Error Handling

Different error handling strategies for different layers:

```python
# Data layer: Specific error information
def get_account_by_id(account_id: int) -> dict:
    try:
        # Database operations
        pass
    except sqlite3.Error as e:
        logger.error(f"Database error retrieving account {account_id}: {e}")
        raise DatabaseError(f"Failed to retrieve account {account_id}") from e

# Business layer: Context-aware error handling  
def calculate_account_balance(account_id: int) -> float:
    try:
        account = get_account_by_id(account_id)
        # Business logic
        return balance
    except DatabaseError:
        logger.warning(f"Cannot calculate balance for missing account {account_id}")
        return 0.0  # Reasonable default

# GUI layer: User-friendly error messages
@log_fn
def on_account_selected(self, account_id: int):
    try:
        balance = calculate_account_balance(account_id)
        self.update_balance_display(balance)
    except Exception as e:
        self.show_message("Unable to load account information")
        logger.exception(f"Error loading account {account_id}")
```

### Graceful Degradation

Design features to fail gracefully:

```python
@log_fn
def load_account_widgets(self):
    """Load account widgets with graceful error handling"""
    
    try:
        accounts = get_account_data()
        logger.info(f"Loading {len(accounts)} account widgets")
        
        for account in accounts:
            try:
                self.create_account_widget(account)
            except Exception as e:
                logger.warning(f"Failed to create widget for account {account.name}: {e}")
                # Continue with other accounts
                continue
                
    except DatabaseError as e:
        logger.error(f"Failed to load account data: {e}")
        # Show placeholder or error message
        self.show_account_error_message()
    
    # Always ensure UI is in consistent state
    self.finalize_account_layout()
```

## 📝 Logging Patterns

### Consistent Log Messages

Use structured log messages with context:

```python
@log_fn
def process_transaction(transaction_data: dict):
    """Process a transaction with comprehensive logging"""
    
    transaction_id = transaction_data.get('id', 'unknown')
    account_id = transaction_data.get('account_id', 'unknown')
    amount = transaction_data.get('amount', 0)
    
    logger.info(f"Processing transaction {transaction_id} for account {account_id}, amount: {amount}")
    
    try:
        # Validation
        validate_transaction_data(transaction_data)
        logger.debug(f"Transaction {transaction_id} validation passed")
        
        # Processing
        result = save_transaction(transaction_data)
        logger.info(f"Transaction {transaction_id} processed successfully, result: {result}")
        
        return result
        
    except ValidationError as e:
        logger.warning(f"Transaction {transaction_id} validation failed: {e}")
        raise
    except DatabaseError as e:
        logger.error(f"Database error processing transaction {transaction_id}: {e}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error processing transaction {transaction_id}")
        raise
```

### Performance Logging

The `@log_fn` decorator automatically logs performance:

```python
@log_fn  # Automatically logs entry/exit and duration
def expensive_calculation():
    """This function's performance is automatically tracked"""
    # Long-running operation
    pass

# Logs will show:
# DEBUG - Start: expensive_calculation
# DEBUG - End: expensive_calculation (Duration: 2.34s)
```

For manual performance tracking:

```python
def manual_performance_tracking():
    """Manual performance logging for complex operations"""
    
    start_time = time.time()
    logger.debug("Starting complex operation")
    
    # Phase 1
    phase1_start = time.time()
    perform_phase1()
    logger.debug(f"Phase 1 completed in {time.time() - phase1_start:.2f}s")
    
    # Phase 2  
    phase2_start = time.time()
    perform_phase2()
    logger.debug(f"Phase 2 completed in {time.time() - phase2_start:.2f}s")
    
    total_time = time.time() - start_time
    logger.info(f"Complex operation completed in {total_time:.2f}s")
```

## 🔌 Plugin Development Patterns

### Standard Plugin Structure

```python
# plugin_scope_type_name.py

import logging
from typing import Optional

# Plugin metadata
menu_id = 100  # Controls menu ordering
version = "1.0.0"
author = "Your Name"
description = "Brief description of plugin functionality"

logger = logging.getLogger(__name__)

def add_to_menu(parent_window, menu_bar):
    """
    Standard plugin entry point for menu plugins.
    
    Args:
        parent_window: BaseWindow instance that loaded the plugin
        menu_bar: tkinter.Menu instance to add items to
    """
    
    try:
        # Plugin initialization
        logger.debug(f"Loading plugin: {__name__}")
        
        # Create menu structure
        create_plugin_menu(parent_window, menu_bar)
        
        logger.info(f"Plugin {__name__} loaded successfully")
        
    except Exception as e:
        logger.error(f"Failed to load plugin {__name__}: {e}")
        # Don't raise - allow application to continue

def create_plugin_menu(parent_window, menu_bar):
    """Create the plugin's menu structure"""
    # Implementation specific to your plugin
    pass

def plugin_cleanup():
    """Optional cleanup function called when plugin is unloaded"""
    logger.debug(f"Cleaning up plugin: {__name__}")
    # Cleanup code here
```

### Plugin Error Handling

Plugins should never crash the main application:

```python
def add_to_menu(parent_window, menu_bar):
    """Error-resistant plugin loading"""
    
    try:
        # Check dependencies
        check_plugin_dependencies()
        
        # Initialize plugin
        initialize_plugin(parent_window)
        
        # Create UI elements
        create_menu_items(parent_window, menu_bar)
        
    except ImportError as e:
        logger.warning(f"Plugin {__name__} missing dependencies: {e}")
        # Could show a disabled menu item or skip entirely
        
    except Exception as e:
        logger.error(f"Plugin {__name__} failed to load: {e}")
        # Log error but don't crash application

def check_plugin_dependencies():
    """Verify required dependencies are available"""
    try:
        import required_module
    except ImportError:
        raise ImportError("Required module 'required_module' not available")
```

## 🧪 Testing Patterns

### Manual Testing Structure

The application includes several test modes:

```python
# In main.py - different test configurations

def main_test() -> None:
    """GUI component testing"""
    app = BaseWindow(plugin_scope="test")
    transaction_page = TransactionPage(parent=app, plugin_scope="test")
    app.mainloop()

def main_fn_test() -> None:
    """Database function testing"""  
    create_database()
    result = get_total_cash_history("2024-12-01", "")
    print(f"Test result: {result}")
```

### Test Data Patterns

For development and testing:

```python
def create_test_data():
    """Create sample data for testing"""
    
    logger.info("Creating test data")
    
    # Create test accounts
    test_accounts = [
        ("Checking Account", "DE89 3704 0044 0532 0130 00", 1500.00),
        ("Savings Account", "DE89 3704 0044 0532 0130 01", 5000.00),
        ("Cash", "CASH001", 200.00)
    ]
    
    for name, number, balance in test_accounts:
        account_id = create_account(name, number, get_next_position())
        update_account_balance(account_id, balance)
        logger.debug(f"Created test account: {name}")
    
    # Create test transactions
    create_test_transactions()
    
    logger.info("Test data creation completed")
```

---

Following these patterns and conventions ensures that your code integrates seamlessly with the existing Budget Planner codebase and maintains the project's quality standards.