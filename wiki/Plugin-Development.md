# Plugin Development

This guide covers how to develop plugins for the Budget Planner application, including the plugin architecture, development process, and best practices.

## 🧩 Plugin System Overview

The Budget Planner uses a **dynamic plugin system** that allows extending functionality without modifying core code. Plugins are automatically discovered and loaded based on naming conventions and scope.

### Core Benefits
- **Extensibility**: Add features without touching core code
- **Modularity**: Each plugin is self-contained
- **Maintainability**: Easy to enable/disable features
- **Third-party development**: External developers can create plugins

## 📁 Plugin Architecture

### Directory Structure
```
src/gui/plugins/
├── __init__.py                    # Plugin loader
├── menu_extension/                # Menu plugins
│   ├── plugin_all_menu_help.py              # Global help menu
│   ├── plugin_homepage_menu_account.py      # Homepage account menu
│   ├── plugin_homepage_menu_transaction.py  # Homepage transaction menu
│   ├── plugin_homepage_menu_overview.py     # Homepage overview menu
│   └── plugin_homepage_menu_data.py         # Homepage data menu
└── [future_plugin_types]/         # Other plugin types (widgets, toolbars, etc.)
```

### Naming Convention

**Critical**: Plugin files must follow this exact naming pattern:

```
plugin_{scope}_{type}_{name}.py
```

| Component | Description | Examples |
|-----------|-------------|----------|
| `plugin` | Fixed prefix for all plugins | `plugin` |
| `{scope}` | Where the plugin applies | `all`, `homepage`, `transactionpage` |
| `{type}` | Plugin functionality type | `menu`, `widget`, `toolbar` |
| `{name}` | Brief functionality description | `account`, `help`, `data` |

**Examples:**
- `plugin_all_menu_help.py` - Global help menu for all windows
- `plugin_homepage_menu_account.py` - Account menu for homepage
- `plugin_transactionpage_widget_calculator.py` - Calculator widget for transaction page

## 🔄 Plugin Loading Process

### Automatic Discovery

The plugin system automatically scans for and loads plugins:

```python
# In BaseWindow.__init__()
def _setup_menu(self):
    menu_bar = tk.Menu(self)
    self.config(menu=menu_bar)
    
    # Load plugins matching this window's scope
    for plugin in load_plugins("menu", self.plugin_scope):
        if hasattr(plugin, "add_to_menu"):
            plugin.add_to_menu(self, menu_bar)
```

### Loading Algorithm

```python
@log_fn
def load_plugins(plugin_type: str, plugin_scope: str):
    """Load and sort plugins by naming convention"""
    plugins = []
    
    for filename in scan_plugin_directory():
        # Parse filename: plugin_scope_type_name.py
        parts = filename[:-3].split("_")
        if len(parts) < 4:
            continue
            
        prefix, scope, p_type, name = parts[:4]
        
        # Filter by type and scope
        if prefix == "plugin" and p_type == plugin_type:
            if scope == "all" or scope == plugin_scope:
                # Dynamic import
                module = importlib.import_module(module_name)
                menu_id = getattr(module, "menu_id", 9999)
                plugins.append((scope, menu_id, module))
    
    # Sort by menu_id for consistent ordering
    return sorted(plugins, key=lambda item: item[1])
```

**Key Points:**
- Plugins matching `scope = "all"` load in every window
- Plugins matching the window's specific scope load only there
- `menu_id` controls display order (10, 20, 30, etc.)
- Invalid plugins are logged but don't break the system

## 🛠️ Creating Menu Plugins

### Basic Menu Plugin Template

```python
# plugin_homepage_menu_myfeature.py
import tkinter as tk
from gui.basewindow import BaseWindow

# Controls menu ordering (10, 20, 30, etc.)
menu_id = 25

def add_to_menu(window: BaseWindow, menu_bar: tk.Menu):
    """Add menu items to the menu bar
    
    Args:
        window: The parent window instance
        menu_bar: The menu bar to add items to
    """
    # Create submenu
    my_menu = tk.Menu(menu_bar, tearoff=0)
    
    # Add menu items
    my_menu.add_command(
        label="My Feature", 
        command=lambda: handle_my_feature(window)
    )
    my_menu.add_separator()
    my_menu.add_command(
        label="Configure", 
        command=lambda: configure_feature(window)
    )
    
    # Add to menu bar
    menu_bar.add_cascade(label="My Feature", menu=my_menu)

def handle_my_feature(window: BaseWindow):
    """Handle menu item action"""
    # Your feature implementation
    window.show_message("My feature activated!")

def configure_feature(window: BaseWindow):
    """Handle configuration"""
    # Configuration dialog or action
    pass
```

### Menu ID Guidelines

Use consistent menu_id values to control menu ordering:

```python
# Standard menu ordering
menu_id = 10   # Primary features (Account, Transaction)
menu_id = 20   # Secondary features (Reports, Analysis)  
menu_id = 30   # Data operations (Import, Export)
menu_id = 40   # Tools and utilities
menu_id = 50   # Configuration and settings
menu_id = 90   # Help and about (use 'all' scope)
```

**Spacing**: Use increments of 10 to allow future plugins to fit between

## 📋 Plugin Development Process

### 1. Planning Your Plugin

Before coding, consider:

**Scope Decision:**
- `all` - Should this feature be available everywhere?
- `homepage` - Only on the main window?
- `transactionpage` - Only when editing transactions?
- Custom scope - For specialized windows?

**Type Decision:**
- `menu` - Menu items and commands
- `widget` - UI components (future)
- `toolbar` - Toolbar buttons (future)

**Name Decision:**
- Keep it short and descriptive
- Use existing names as reference
- Avoid special characters or spaces

### 2. Setting Up Development Environment

1. **Create Plugin File**: Follow naming convention exactly
2. **Choose Menu ID**: Pick appropriate ordering value
3. **Import Required Modules**: GUI libraries, utilities, etc.
4. **Test Plugin Loading**: Verify plugin is discovered

```bash
# Test plugin loading by running the application
python src/main.py

# Check logs for plugin loading messages
tail -f log/app.log | grep plugin
```

### 3. Implementing Plugin Interface

#### Required Interface Methods

**For Menu Plugins:**
```python
def add_to_menu(window: BaseWindow, menu_bar: tk.Menu):
    """Required method for menu plugins"""
    # Must be implemented
```

**For Future Plugin Types:**
```python
def add_to_toolbar(window: BaseWindow, toolbar: tk.Frame):
    """For toolbar plugins"""
    
def create_widget(parent: tk.Widget) -> tk.Widget:
    """For widget plugins"""
```

#### Plugin Metadata

```python
# Required for ordering
menu_id = 30

# Optional metadata
plugin_name = "My Feature Plugin"
plugin_version = "1.0.0"
plugin_author = "Your Name"
plugin_description = "Brief description of functionality"
```

### 4. Testing Your Plugin

#### Basic Testing
```python
# Add debug output to your plugin
def add_to_menu(window, menu_bar):
    print(f"Loading {__name__} plugin")
    # ... rest of implementation
```

#### Integration Testing
1. **Menu Loading**: Verify menu items appear in correct order
2. **Functionality**: Test all menu commands work properly
3. **Error Handling**: Test with invalid inputs or edge cases
4. **Window Scope**: Verify plugin loads only in intended windows

#### Plugin-Specific Testing
```python
# Test in main.py or create dedicated test
def test_my_plugin():
    from gui.plugins.menu_extension.plugin_homepage_menu_myfeature import add_to_menu
    # Test plugin functions
```

## 🎨 Advanced Plugin Patterns

### Dialog Creation Pattern

```python
def open_my_dialog(parent_window: BaseWindow):
    """Create and show a custom dialog"""
    from gui.basetoplevelwindow import BaseToplevelWindow
    
    class MyDialog(BaseToplevelWindow):
        def __init__(self, master):
            super().__init__(master, plugin_scope="mydialog", 
                           title="My Dialog", geometry="400x300")
        
        def init_ui(self):
            # Implement dialog UI
            tk.Label(self.main_frame, text="My Dialog Content").pack()
            tk.Button(self.main_frame, text="OK", 
                     command=self.destroy).pack(pady=10)
    
    dialog = MyDialog(parent_window)
    parent_window.wait_window(dialog)  # Modal behavior
```

### Database Integration Pattern

```python
from utils.data.database_connection import DatabaseConnection
from utils.logging.logging_tools import log_fn

@log_fn
def my_database_operation():
    """Plugin database operations"""
    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM tbl_Account WHERE condition = ?", (value,))
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"Database error in plugin: {e}")
        return []
```

### Configuration Storage Pattern

```python
import json
from pathlib import Path
import config

def save_plugin_config(config_data: dict):
    """Save plugin configuration"""
    config_path = config.Database.PATH.parent / "plugin_configs" / "myfeature.json"
    config_path.parent.mkdir(exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=2)

def load_plugin_config() -> dict:
    """Load plugin configuration"""
    config_path = config.Database.PATH.parent / "plugin_configs" / "myfeature.json"
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}  # Default configuration
```

## 📝 Plugin Examples

### Example 1: Simple Information Plugin

```python
# plugin_all_menu_about.py
import tkinter as tk
from tkinter import messagebox

menu_id = 90

def add_to_menu(window, menu_bar):
    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="About", command=show_about)
    menu_bar.add_cascade(label="Help", menu=help_menu)

def show_about():
    messagebox.showinfo(
        "About Budget Planner",
        "Budget Planner v1.0\nPersonal Finance Management\n\nDeveloped with Python & Tkinter"
    )
```

### Example 2: Feature Plugin with Dialog

```python
# plugin_homepage_menu_backup.py
import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import config

menu_id = 35

def add_to_menu(window, menu_bar):
    tools_menu = tk.Menu(menu_bar, tearoff=0)
    tools_menu.add_command(label="Backup Database", command=lambda: backup_database(window))
    tools_menu.add_command(label="Restore Database", command=lambda: restore_database(window))
    menu_bar.add_cascade(label="Tools", menu=tools_menu)

def backup_database(parent_window):
    """Backup database to user-selected location"""
    backup_path = filedialog.asksaveasfilename(
        title="Save Database Backup",
        defaultextension=".db",
        filetypes=[("Database files", "*.db"), ("All files", "*.*")]
    )
    
    if backup_path:
        try:
            shutil.copy2(config.Database.PATH, backup_path)
            messagebox.showinfo("Success", f"Database backed up to:\n{backup_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed:\n{e}")

def restore_database(parent_window):
    """Restore database from user-selected backup"""
    parent_window.ask_permission(
        "This will replace your current database. Continue?", 
        [True, False]
    )
    
    if not getattr(parent_window, 'permission', False):
        return
        
    restore_path = filedialog.askopenfilename(
        title="Select Database Backup",
        filetypes=[("Database files", "*.db"), ("All files", "*.*")]
    )
    
    if restore_path:
        try:
            shutil.copy2(restore_path, config.Database.PATH)
            messagebox.showinfo("Success", "Database restored successfully.\nRestart the application.")
        except Exception as e:
            messagebox.showerror("Error", f"Restore failed:\n{e}")
```

### Example 3: Data Analysis Plugin

```python
# plugin_homepage_menu_analytics.py
import tkinter as tk
from gui.basetoplevelwindow import BaseToplevelWindow
from utils.data.database.transaction_utils import get_all_transactions
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

menu_id = 25

def add_to_menu(window, menu_bar):
    analytics_menu = tk.Menu(menu_bar, tearoff=0)
    analytics_menu.add_command(label="Spending Chart", 
                              command=lambda: show_spending_chart(window))
    menu_bar.add_cascade(label="Analytics", menu=analytics_menu)

def show_spending_chart(parent_window):
    """Show spending analysis chart"""
    
    class AnalyticsWindow(BaseToplevelWindow):
        def __init__(self, master):
            super().__init__(master, plugin_scope="analytics",
                           title="Spending Analytics", geometry="800x600")
        
        def init_ui(self):
            # Get transaction data
            transactions = get_all_transactions()
            
            # Create matplotlib figure
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Process data and create chart
            # ... chart creation logic ...
            
            # Embed in tkinter
            canvas = FigureCanvasTkAgg(fig, self.main_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    analytics_window = AnalyticsWindow(parent_window)
```

## 🔍 Debugging Plugins

### Common Issues

#### Plugin Not Loading
**Symptoms**: Plugin doesn't appear in menus
**Causes**:
- Incorrect naming convention
- File not in correct directory
- Import errors in plugin code

**Debug Steps**:
```bash
# Check plugin discovery logs
grep "Loading plugin" log/app.log

# Check for import errors  
grep "Error loading plugin" log/app.log

# Verify file naming
ls -la src/gui/plugins/menu_extension/plugin_*
```

#### Menu Items Not Appearing
**Symptoms**: Plugin loads but menu items missing
**Causes**:
- Missing `add_to_menu` method
- Errors in menu creation code
- Incorrect scope matching

**Debug Steps**:
```python
# Add debug prints to your plugin
def add_to_menu(window, menu_bar):
    print(f"Adding menu for {window.__class__.__name__}")
    print(f"Menu bar has {menu_bar.index(tk.END) + 1} items")
    # ... rest of code
```

#### Runtime Errors
**Symptoms**: Plugin loads but crashes when used
**Causes**:
- Missing imports
- Incorrect function signatures
- Database connection issues

**Debug Strategy**:
```python
def safe_plugin_function(window):
    """Wrapper with error handling"""
    try:
        # Your plugin code here
        actual_plugin_function(window)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception(f"Plugin error: {e}")
        window.show_message(f"Plugin error: {e}")
```

### Testing Strategies

#### Unit Testing
```python
# test_my_plugin.py
import unittest
from unittest.mock import MagicMock
from gui.plugins.menu_extension.plugin_homepage_menu_myfeature import add_to_menu

class TestMyPlugin(unittest.TestCase):
    def test_menu_creation(self):
        """Test menu is created properly"""
        window_mock = MagicMock()
        menu_bar_mock = MagicMock()
        
        add_to_menu(window_mock, menu_bar_mock)
        
        # Verify menu was added
        menu_bar_mock.add_cascade.assert_called_once()
```

#### Integration Testing
```python
# Manual integration test
if __name__ == "__main__":
    # Test plugin in isolation
    import tkinter as tk
    from gui.basewindow import BaseWindow
    
    class TestWindow(BaseWindow):
        def init_ui(self):
            tk.Label(self.main_frame, text="Test Window").pack()
    
    app = TestWindow(plugin_scope="homepage", title="Plugin Test")
    app.run()
```

## 📚 Plugin Best Practices

### Code Quality
- **Follow PEP 8** style guidelines
- **Use type hints** for function parameters
- **Add docstrings** for all public functions
- **Handle exceptions** gracefully

### User Experience  
- **Consistent naming** with existing menus
- **Logical menu placement** using appropriate menu_id
- **Clear error messages** for user actions
- **Confirmation dialogs** for destructive actions

### Performance
- **Lazy loading** for expensive operations
- **Efficient database queries** using utilities
- **Memory management** for large datasets
- **Progress indicators** for long operations

### Maintainability
- **Minimal dependencies** on core code
- **Clear separation** between plugin and core
- **Configuration externalization** when possible
- **Documentation** for complex plugins

## 🔮 Future Plugin Types

The plugin system is designed for expansion beyond menu plugins:

### Widget Plugins
```python
# plugin_homepage_widget_calculator.py
def create_widget(parent) -> tk.Widget:
    """Return a widget to be embedded in the parent"""
    return CalculatorWidget(parent)
```

### Toolbar Plugins
```python
# plugin_all_toolbar_quickactions.py  
def add_to_toolbar(window, toolbar):
    """Add buttons to application toolbar"""
    tk.Button(toolbar, text="Quick Add", command=quick_add).pack(side=tk.LEFT)
```

### Data Plugins
```python
# plugin_all_data_csvexport.py
def register_export_format():
    """Register new export format"""
    return {
        'name': 'CSV Export',
        'extension': '.csv', 
        'handler': export_to_csv
    }
```

---

*The plugin system makes Budget Planner highly extensible while maintaining code organization and stability. Follow these patterns to create powerful, maintainable plugins that enhance the user experience.*