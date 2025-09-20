# Testing & Debugging

This guide covers testing strategies, debugging techniques, and troubleshooting common issues in the Budget Planner application.

## 🧪 Testing Strategies

### Manual Testing

#### Application Testing
```python
# Test full application
python src/main.py

# Test specific component
def test_transaction_page():
    from src.main import main_test
    main_test()

# Test specific function  
def test_account_utils():
    from src.main import main_fn_test
    main_fn_test()
```

#### Window Testing
```python
# Test individual windows
from gui.basewindow import BaseWindow
from gui.transactionpage.transactionpage import TransactionPage

def test_window():
    """Test window in isolation"""
    app = BaseWindow(plugin_scope="test", title="Test Window")
    
    # Hide root window for modal testing
    app.withdraw()  
    
    # Create test window
    test_page = TransactionPage(parent=app, plugin_scope="test")
    
    app.mainloop()

if __name__ == "__main__":
    test_window()
```

#### Database Testing
```python
def test_database_operations():
    """Test database CRUD operations"""
    from utils.data.createdatabase_utils import create_database
    from utils.data.database.account_utils import add_account, get_account_data
    
    # Create test database
    create_database()
    
    # Test create
    print("Testing account creation...")
    success = add_account("Test Account", "TEST123")
    print(f"Add result: {success}")
    
    # Test read
    print("Testing account retrieval...")
    accounts = get_account_data()
    print(f"Accounts: {len(accounts)} found")
    for account in accounts:
        print(f"  {account}")
    
    # Test update/delete operations
    # ...

if __name__ == "__main__":
    test_database_operations()
```

### Plugin Testing

#### Plugin Loading Test
```python
def test_plugin_loading():
    """Test plugin discovery and loading"""
    from gui.plugins import load_plugins
    
    # Test menu plugins
    plugins = load_plugins("menu", "homepage")
    print(f"Loaded {len(plugins)} homepage menu plugins:")
    
    for plugin in plugins:
        print(f"  - {plugin.__name__}")
        if hasattr(plugin, 'menu_id'):
            print(f"    Menu ID: {plugin.menu_id}")

if __name__ == "__main__":
    test_plugin_loading()
```

#### Individual Plugin Test
```python
def test_specific_plugin():
    """Test a specific plugin in isolation"""
    import tkinter as tk
    from gui.basewindow import BaseWindow
    
    # Import plugin directly
    from gui.plugins.menu_extension.plugin_homepage_menu_account import add_to_menu
    
    class TestWindow(BaseWindow):
        def init_ui(self):
            tk.Label(self.main_frame, text="Plugin Test").pack()
    
    app = TestWindow(plugin_scope="homepage", title="Plugin Test")
    
    # Test menu creation
    menu_bar = tk.Menu(app)
    add_to_menu(app, menu_bar)
    app.config(menu=menu_bar)
    
    app.run()

if __name__ == "__main__":
    test_specific_plugin()
```

## 🔍 Debugging Techniques

### Logging Analysis

#### Real-time Log Monitoring
```bash
# Monitor all logs
tail -f log/app.log

# Monitor specific components
tail -f log/app.log | grep -i "transaction"
tail -f log/app.log | grep -i "database"
tail -f log/app.log | grep -i "error"

# Monitor without debug messages
tail -f log/app_no_debug.log
```

#### Log Level Filtering
```bash
# Show only errors and warnings
grep -E "(ERROR|WARNING)" log/app.log

# Show timing information
grep "Duration:" log/app.log | tail -10

# Show plugin loading
grep "plugin" log/app.log
```

#### Custom Debug Logging
```python
import logging

# Create custom logger for debugging
debug_logger = logging.getLogger("debug")
debug_logger.setLevel(logging.DEBUG)

def debug_function():
    """Function with detailed debug logging"""
    debug_logger.debug("Function entry")
    debug_logger.debug(f"Parameter values: {locals()}")
    
    # ... function code ...
    
    debug_logger.debug("Function exit")
```

### Database Debugging

#### SQLite Command Line
```bash
# Open database
sqlite3 data/database.db

# Useful commands
.tables                          # List all tables
.schema tbl_Transaction         # Show table structure
.headers on                     # Show column headers
.mode column                    # Columnar output

# Query data
SELECT * FROM tbl_Account LIMIT 5;
SELECT COUNT(*) FROM tbl_Transaction;

# Check foreign keys
PRAGMA foreign_key_check;

# Query with joins
SELECT 
    t.str_Purpose,
    a.str_AccountName,
    c.str_CategoryName
FROM tbl_Transaction t
LEFT JOIN tbl_Account a ON t.i8_AccountID = a.i8_AccountID
LEFT JOIN tbl_Category c ON t.i8_CategoryID = c.i8_CategoryID
LIMIT 10;

.quit
```

#### Database Browser Tool
```bash
# Install DB Browser for SQLite (GUI tool)
# Ubuntu/Debian
sudo apt install sqlitebrowser

# Windows/Mac - download from https://sqlitebrowser.org/

# Open database file
sqlitebrowser data/database.db
```

#### Database Connection Debugging
```python
def debug_database_connection():
    """Debug database connection issues"""
    from utils.data.database_connection import DatabaseConnection
    import config
    
    print(f"Database path: {config.Database.PATH}")
    print(f"Path exists: {config.Database.PATH.exists()}")
    
    try:
        conn = DatabaseConnection.get_connection()
        print(f"Connection: {conn}")
        print(f"Connection type: {type(conn)}")
        
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()
        print(f"SQLite version: {version}")
        
        # Test table access
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables: {[table[0] for table in tables]}")
        
    except Exception as e:
        print(f"Database error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_database_connection()
```

### GUI Debugging

#### Widget Inspection
```python
def debug_widget_tree(widget, indent=0):
    """Print widget hierarchy for debugging layout issues"""
    print("  " * indent + f"{widget.__class__.__name__}: {widget}")
    
    # Print widget properties
    if hasattr(widget, 'winfo_geometry'):
        print("  " * indent + f"  Geometry: {widget.winfo_geometry()}")
    
    if hasattr(widget, 'cget'):
        try:
            bg = widget.cget('bg')
            print("  " * indent + f"  Background: {bg}")
        except:
            pass
    
    # Recurse through children
    for child in widget.winfo_children():
        debug_widget_tree(child, indent + 1)

# Usage in window
def init_ui(self):
    # ... create UI ...
    
    # Debug widget tree
    self.after(1000, lambda: debug_widget_tree(self.main_frame))
```

#### Event Debugging
```python
def debug_events(widget):
    """Add event debugging to a widget"""
    def log_event(event):
        print(f"Event: {event.type} on {event.widget}")
    
    # Bind to common events
    widget.bind('<Button-1>', log_event)
    widget.bind('<KeyPress>', log_event)
    widget.bind('<FocusIn>', log_event)
    widget.bind('<FocusOut>', log_event)

# Usage
entry_widget = tk.Entry(parent)
debug_events(entry_widget)
```

#### Layout Debugging
```python
def debug_layout_issues():
    """Debug common layout issues"""
    def show_widget_info(event):
        widget = event.widget
        print(f"Widget: {widget}")
        print(f"  Requested size: {widget.winfo_reqwidth()}x{widget.winfo_reqheight()}")
        print(f"  Actual size: {widget.winfo_width()}x{widget.winfo_height()}")
        print(f"  Position: {widget.winfo_x()}, {widget.winfo_y()}")
        print(f"  Geometry: {widget.winfo_geometry()}")
    
    # Bind to main frame
    self.main_frame.bind('<Configure>', show_widget_info)
```

## 🐛 Common Issues and Solutions

### Database Issues

#### Issue: "Database is locked" 
**Symptoms**: `sqlite3.OperationalError: database is locked`

**Causes:**
- Multiple connections to database
- Unfinished transaction
- Application crashed without closing connection

**Solutions:**
```python
# Check for other processes using database
lsof data/database.db  # Linux/Mac

# Restart application to clear connections
python src/main.py

# Manual connection cleanup
from utils.data.database_connection import DatabaseConnection
DatabaseConnection.close_connection()
```

#### Issue: Foreign Key Constraint Failed
**Symptoms**: `FOREIGN KEY constraint failed`

**Debug Steps:**
```sql
-- Check foreign key constraints
PRAGMA foreign_key_check;

-- Verify referenced records exist
SELECT * FROM tbl_Account WHERE i8_AccountID = 999;  -- Check if ID exists

-- Check constraint definitions
.schema tbl_Transaction
```

**Solutions:**
- Ensure referenced records exist before insertion
- Use proper cascade options in schema
- Validate data before database operations

#### Issue: Column Does Not Exist
**Symptoms**: `no such column: new_column`

**Causes:**
- Database schema out of sync
- Migration not applied
- Wrong database file

**Solutions:**
```python
# Recreate database schema
import os
import config

# Backup existing data first
os.rename(str(config.Database.PATH), str(config.Database.PATH) + ".backup")

# Recreate database
from utils.data.createdatabase_utils import create_database
create_database()
```

### GUI Issues

#### Issue: Window Not Showing
**Symptoms**: Window created but not visible

**Debug Steps:**
```python
def debug_window_visibility():
    print(f"Window state: {self.state()}")
    print(f"Window geometry: {self.geometry()}")
    print(f"Window position: {self.winfo_x()}, {self.winfo_y()}")
    print(f"Window size: {self.winfo_width()}x{self.winfo_height()}")

# Call after window creation
self.after(100, debug_window_visibility)
```

**Solutions:**
- Check if window is minimized: `self.deiconify()`
- Verify geometry is reasonable: `self.geometry("800x600")`
- Bring to front: `self.lift()` and `self.focus_force()`

#### Issue: Plugin Menus Not Loading
**Symptoms**: Expected menu items don't appear

**Debug Steps:**
```python
# Check plugin loading
from gui.plugins import load_plugins

plugins = load_plugins("menu", "homepage")
print(f"Loaded plugins: {[p.__name__ for p in plugins]}")

# Check plugin file names
import os
plugin_dir = "src/gui/plugins/menu_extension"
files = os.listdir(plugin_dir)
print(f"Plugin files: {[f for f in files if f.startswith('plugin_')]}")

# Check specific plugin
try:
    from gui.plugins.menu_extension.plugin_homepage_menu_account import add_to_menu
    print("Plugin import successful")
except Exception as e:
    print(f"Plugin import failed: {e}")
```

**Solutions:**
- Verify plugin file naming convention
- Check for import errors in plugin files
- Ensure plugin directory is in Python path
- Check plugin scope matches window scope

#### Issue: Layout Problems
**Symptoms**: Widgets overlapping, wrong sizes, or positions

**Debug Tools:**
```python
def highlight_frames():
    """Add colored borders to frames for layout debugging"""
    colors = ['red', 'blue', 'green', 'yellow', 'purple']
    
    def color_widget(widget, color_index=0):
        if isinstance(widget, (tk.Frame, ttk.Frame)):
            widget.config(relief='solid', borderwidth=2)
            # Cycle through colors
            color = colors[color_index % len(colors)]
            if hasattr(widget, 'configure'):
                widget.configure(highlightbackground=color, highlightthickness=2)
        
        for child in widget.winfo_children():
            color_widget(child, color_index + 1)
    
    color_widget(self.main_frame)

# Call after UI creation
self.after(500, highlight_frames)
```

**Solutions:**
- Use `pack_propagate(False)` or `grid_propagate(False)` for fixed sizes
- Check sticky options in grid layout
- Verify fill and expand options in pack layout
- Use `pady` and `padx` for spacing

### Plugin Issues

#### Issue: Plugin Not Discovered
**Symptoms**: Plugin file exists but doesn't load

**Checklist:**
- [ ] File name follows `plugin_{scope}_{type}_{name}.py` pattern
- [ ] File is in correct directory (`src/gui/plugins/menu_extension/`)
- [ ] Plugin has required `menu_id` variable
- [ ] Plugin has required interface methods (`add_to_menu`)
- [ ] No Python syntax errors in plugin file

**Debug Script:**
```python
def debug_plugin_discovery():
    """Debug plugin discovery process"""
    import os
    import importlib.util
    
    plugin_dir = "src/gui/plugins/menu_extension"
    
    for filename in os.listdir(plugin_dir):
        if filename.startswith("plugin_") and filename.endswith(".py"):
            print(f"Found plugin file: {filename}")
            
            # Parse name components
            parts = filename[:-3].split("_")
            if len(parts) >= 4:
                prefix, scope, ptype, name = parts[:4]
                print(f"  Parsed: prefix={prefix}, scope={scope}, type={ptype}, name={name}")
            else:
                print(f"  Invalid name format: {parts}")
            
            # Try to import
            file_path = os.path.join(plugin_dir, filename)
            spec = importlib.util.spec_from_file_location(filename[:-3], file_path)
            
            try:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                print(f"  Import: SUCCESS")
                
                if hasattr(module, 'menu_id'):
                    print(f"  Menu ID: {module.menu_id}")
                else:
                    print(f"  Menu ID: MISSING")
                    
                if hasattr(module, 'add_to_menu'):
                    print(f"  Interface: add_to_menu exists")
                else:
                    print(f"  Interface: add_to_menu MISSING")
                    
            except Exception as e:
                print(f"  Import: FAILED - {e}")

if __name__ == "__main__":
    debug_plugin_discovery()
```

## 🔧 Performance Debugging

### Database Performance

#### Query Performance
```python
import time
import sqlite3

def benchmark_query(query, params=None):
    """Benchmark database query performance"""
    from utils.data.database_connection import DatabaseConnection
    
    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor()
    
    start_time = time.time()
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    
    results = cursor.fetchall()
    end_time = time.time()
    
    print(f"Query: {query[:50]}...")
    print(f"Results: {len(results)} rows")
    print(f"Time: {end_time - start_time:.4f} seconds")
    
    return results

# Test common queries
benchmark_query("SELECT * FROM tbl_Account")
benchmark_query("SELECT * FROM tbl_Transaction WHERE i8_AccountID = ?", (1,))
```

#### Connection Performance
```python
def benchmark_connection():
    """Benchmark connection creation vs singleton"""
    import time
    from utils.data.database_connection import DatabaseConnection
    
    # Test singleton connection
    start = time.time()
    for i in range(100):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
    singleton_time = time.time() - start
    
    # Test new connections (don't do this in real code!)
    start = time.time() 
    for i in range(100):
        conn = sqlite3.connect("data/database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
    new_conn_time = time.time() - start
    
    print(f"Singleton connections: {singleton_time:.4f}s")
    print(f"New connections: {new_conn_time:.4f}s")
    print(f"Improvement: {new_conn_time/singleton_time:.1f}x faster")

if __name__ == "__main__":
    benchmark_connection()
```

### GUI Performance

#### Widget Creation Performance
```python
def benchmark_widget_creation():
    """Benchmark widget creation performance"""
    import time
    import tkinter as tk
    from tkinter import ttk
    
    root = tk.Tk()
    root.withdraw()  # Don't show window
    
    # Test tk widgets
    start = time.time()
    widgets = []
    for i in range(1000):
        widget = tk.Label(root, text=f"Label {i}")
        widgets.append(widget)
    tk_time = time.time() - start
    
    # Clean up
    for widget in widgets:
        widget.destroy()
    
    # Test ttk widgets
    start = time.time()
    widgets = []
    for i in range(1000):
        widget = ttk.Label(root, text=f"Label {i}")
        widgets.append(widget)
    ttk_time = time.time() - start
    
    print(f"tk widgets: {tk_time:.4f}s")
    print(f"ttk widgets: {ttk_time:.4f}s")
    
    root.destroy()

if __name__ == "__main__":
    benchmark_widget_creation()
```

## 📊 Testing Tools and Scripts

### Test Runner Script
```python
#!/usr/bin/env python3
"""Test runner for Budget Planner components"""

import sys
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def run_test(test_name, test_function):
    """Run a single test with error handling"""
    print(f"\n{'='*50}")
    print(f"Running test: {test_name}")
    print('='*50)
    
    try:
        test_function()
        print(f"✓ {test_name} PASSED")
    except Exception as e:
        print(f"✗ {test_name} FAILED: {e}")
        traceback.print_exc()

def test_database():
    """Test database operations"""
    from utils.data.createdatabase_utils import create_database
    from utils.data.database.account_utils import add_account, get_account_data
    
    create_database()
    
    # Test account creation
    success = add_account("Test Account", "TEST001")
    assert success, "Account creation failed"
    
    # Test account retrieval
    accounts = get_account_data()
    assert len(accounts) > 0, "No accounts found"
    
    print(f"Found {len(accounts)} accounts")

def test_plugins():
    """Test plugin loading"""
    from gui.plugins import load_plugins
    
    plugins = load_plugins("menu", "homepage")
    assert len(plugins) > 0, "No homepage menu plugins found"
    
    print(f"Loaded {len(plugins)} plugins")
    
    for plugin in plugins:
        assert hasattr(plugin, 'add_to_menu'), f"Plugin {plugin.__name__} missing add_to_menu"
        print(f"  ✓ {plugin.__name__}")

def test_logging():
    """Test logging configuration"""
    import logging
    from utils.logging.logger_config import setup_logging
    from utils.logging.logging_tools import log_fn
    
    setup_logging()
    
    logger = logging.getLogger("test")
    logger.info("Test log message")
    
    @log_fn
    def test_function():
        return "test"
    
    result = test_function()
    assert result == "test", "Logged function failed"
    
    print("Logging system working correctly")

def main():
    """Run all tests"""
    tests = [
        ("Database Operations", test_database),
        ("Plugin Loading", test_plugins), 
        ("Logging System", test_logging),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            run_test(test_name, test_func)
            passed += 1
        except:
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed} passed, {failed} failed")
    print('='*50)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
```

### Interactive Debugging Shell
```python
#!/usr/bin/env python3
"""Interactive debugging shell for Budget Planner"""

import sys
import code
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import commonly used modules
import config
from utils.data.database_connection import DatabaseConnection
from utils.data.createdatabase_utils import create_database
from utils.logging.logger_config import setup_logging

# Import utilities
from utils.data.database.account_utils import *
from utils.data.database.transaction_utils import *
from utils.data.database.category_utils import *

def setup_environment():
    """Setup debugging environment"""
    print("Setting up Budget Planner debugging environment...")
    
    # Setup logging
    setup_logging()
    
    # Create database
    create_database()
    
    # Get database connection
    conn = DatabaseConnection.get_connection()
    print(f"Database connected: {config.Database.PATH}")
    
    # Show available functions
    print("\nAvailable functions:")
    print("  Database: get_account_data(), add_account(), get_all_transactions()")
    print("  Connection: conn (database connection)")
    print("  Config: config.Database.PATH, config.Logging.LOG_FILE")
    
    return {
        'conn': conn,
        'config': config,
    }

if __name__ == "__main__":
    # Setup environment
    env = setup_environment()
    
    # Start interactive shell
    print("\nStarting interactive shell...")
    print("Type 'help()' for Python help, 'exit()' to quit")
    
    code.interact(local=dict(globals(), **env))
```

---

*These testing and debugging techniques will help you identify and resolve issues quickly, ensuring the Budget Planner application remains stable and reliable as it grows.*