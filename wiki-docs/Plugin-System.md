# Plugin System

The Budget Planner features a sophisticated plugin architecture that allows for easy extension of functionality without modifying core code. This document explains how the plugin system works and how to create custom plugins.

## 🔌 Plugin System Overview

The plugin system is designed around **convention-based discovery** and **scope-based loading**. It enables:

- **Menu Extensions**: Add custom menu items to any window
- **Feature Extensions**: Integrate new functionality seamlessly
- **Scope-Based Loading**: Load plugins only where they're needed
- **Dynamic Discovery**: Automatic plugin detection based on file naming
- **Error Isolation**: Plugin failures don't crash the main application

## 📁 Plugin Structure

### Directory Layout

```
src/gui/plugins/
├── __init__.py                    # Plugin loader module
└── menu_extension/               # Plugin category folder
    ├── plugin_all_menu_help.py  # Global help menu
    └── plugin_homepage_menu_account.py  # Homepage account menu
```

### File Naming Convention

All plugin files must follow this strict naming pattern:

```
plugin_<scope>_<type>_<name>.py
```

**Components**:
- **plugin**: Required prefix for all plugin files
- **scope**: Where the plugin applies (`all`, `homepage`, `transaction`, etc.)
- **type**: Plugin category (`menu`, `widget`, `tool`, etc.)
- **name**: Descriptive name of the plugin's function

### Examples

| Filename | Scope | Type | Name | Purpose |
|----------|-------|------|------|---------|
| `plugin_all_menu_help.py` | all | menu | help | Global help menu |
| `plugin_homepage_menu_account.py` | homepage | menu | account | Homepage account menu |
| `plugin_transaction_widget_calculator.py` | transaction | widget | calculator | Transaction calculator widget |
| `plugin_all_tool_export.py` | all | tool | export | Global data export tool |

## 🔍 Plugin Discovery Process

The plugin system uses a sophisticated discovery mechanism implemented in `src/gui/plugins/__init__.py`:

### 1. File System Scanning

```python
@log_fn
def load_plugins(plugin_type: str, plugin_scope: str):
    """Load plugins based on naming convention and scope"""
    
    base_path = os.path.dirname(__file__)
    plugins = []
    
    # Walk through all subdirectories
    for root, _, files in os.walk(base_path):
        for filename in files:
            if not filename.endswith(".py") or filename.startswith("__"):
                continue
                
            # Parse filename components
            parts = filename[:-3].split("_")
            if len(parts) < 4:
                continue
                
            prefix, scope, p_type, _ = parts[:4]
```

### 2. Plugin Filtering

Plugins are filtered based on:

- **Prefix Match**: Must start with "plugin"
- **Type Match**: Must match requested plugin type (`menu`, `widget`, etc.)
- **Scope Match**: Must match current scope or be universal (`all`)

```python
if prefix != "plugin" or p_type != plugin_type:
    continue

if scope == "all" or scope == plugin_scope:
    # Plugin matches criteria - load it
```

### 3. Dynamic Loading

```python
# Construct module path
module_path = f"{base_package}.{relative_path.replace(os.sep, '.')}"
module_name = f"{module_path}.{filename[:-3]}"

try:
    module = importlib.import_module(module_name)
    menu_id = getattr(module, "menu_id", 9999)  # Default priority
    plugins.append((scope, menu_id, module))
except Exception as e:
    logger.exception(f"Error loading plugin {filename}: {e}")
```

### 4. Plugin Sorting

Plugins are sorted by their `menu_id` attribute for consistent ordering:

```python
# Sort by menu_id for consistent ordering
sorted_plugins = sorted(plugins, key=lambda item: item[1])
return [mod for _, _, mod in sorted_plugins]
```

## 🎯 Plugin Scopes

### Predefined Scopes

| Scope | Description | When Loaded |
|-------|-------------|-------------|
| `all` | Global plugins | Every window |
| `homepage` | Homepage-specific | Main application window |
| `transaction` | Transaction-related | Transaction management windows |
| `account` | Account-specific | Account management windows |
| `overview` | Overview features | Financial overview windows |
| `test` | Development/testing | Test mode only |

### Custom Scopes

You can define custom scopes for new windows:

```python
class MyCustomWindow(BaseWindow):
    def __init__(self):
        super().__init__(
            plugin_scope="custom_scope",  # Your custom scope
            title="My Custom Window"
        )
```

Plugins targeting this scope would be named:
```
plugin_custom_scope_menu_feature.py
```

## ✍️ Creating Plugins

### Basic Menu Plugin Structure

```python
# plugin_homepage_menu_example.py

import tkinter as tk
import logging

# Plugin metadata
menu_id = 100  # Determines menu order (lower = earlier)

logger = logging.getLogger(__name__)

def add_to_menu(parent_window, menu_bar):
    """
    Called by BaseWindow to integrate plugin into menu system.
    
    Args:
        parent_window: The window instance requesting plugins
        menu_bar: The tkinter Menu object to add items to
    """
    
    # Create a new menu
    example_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Example", menu=example_menu)
    
    # Add menu items
    example_menu.add_command(
        label="Do Something",
        command=lambda: do_something(parent_window)
    )
    
    example_menu.add_separator()
    
    example_menu.add_command(
        label="Settings",
        command=lambda: open_settings(parent_window)
    )
    
    logger.info("Example menu plugin loaded successfully")

def do_something(parent_window):
    """Example plugin functionality"""
    parent_window.show_message("Plugin action executed!")

def open_settings(parent_window):
    """Example settings dialog"""
    # Implementation details...
    pass
```

### Advanced Plugin Example

```python
# plugin_all_menu_data_export.py

import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import json
import logging
from utils.data.database.transaction_utils import get_all_transactions

menu_id = 200  # Later in menu order

logger = logging.getLogger(__name__)

def add_to_menu(parent_window, menu_bar):
    """Add data export menu to any window"""
    
    # Find existing File menu or create it
    file_menu = None
    for i in range(menu_bar.index("end") + 1):
        try:
            if menu_bar.entrycget(i, "label") == "File":
                file_menu = menu_bar.nametowidget(menu_bar.entrycget(i, "menu"))
                break
        except tk.TclError:
            continue
    
    if not file_menu:
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
    
    # Add export submenu
    export_menu = tk.Menu(file_menu, tearoff=0)
    file_menu.add_cascade(label="Export", menu=export_menu)
    
    export_menu.add_command(
        label="Export to CSV",
        command=lambda: export_data(parent_window, "csv")
    )
    
    export_menu.add_command(
        label="Export to JSON", 
        command=lambda: export_data(parent_window, "json")
    )

def export_data(parent_window, format_type):
    """Export transaction data to specified format"""
    
    try:
        # Get data
        transactions = get_all_transactions()
        
        if not transactions:
            messagebox.showwarning("Export", "No data to export")
            return
        
        # Choose file location
        if format_type == "csv":
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            if filename:
                export_csv(transactions, filename)
        
        elif format_type == "json":
            filename = filedialog.asksaveasfilename(
                defaultextension=".json", 
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                export_json(transactions, filename)
        
        if filename:
            messagebox.showinfo("Export", f"Data exported successfully to {filename}")
            logger.info(f"Data exported to {filename}")
            
    except Exception as e:
        error_msg = f"Export failed: {str(e)}"
        messagebox.showerror("Export Error", error_msg)
        logger.error(error_msg)

def export_csv(transactions, filename):
    """Export transactions to CSV format"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(['Date', 'Account', 'Amount', 'Purpose', 'Category'])
        # Write data
        for transaction in transactions:
            writer.writerow([
                transaction.date,
                transaction.account_name, 
                transaction.amount,
                transaction.purpose,
                transaction.category_name
            ])

def export_json(transactions, filename):
    """Export transactions to JSON format"""
    data = []
    for transaction in transactions:
        data.append({
            'date': transaction.date,
            'account': transaction.account_name,
            'amount': transaction.amount,
            'purpose': transaction.purpose,
            'category': transaction.category_name
        })
    
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=2, ensure_ascii=False)
```

## 🔧 Plugin Integration Points

### BaseWindow Integration

The `BaseWindow` class automatically loads and integrates plugins:

```python
def _setup_menu(self) -> None:
    menu_bar = tk.Menu(self)
    self.config(menu=menu_bar)

    # Load plugins for current scope
    for plugin in load_plugins("menu", self.plugin_scope):
        if hasattr(plugin, "add_to_menu"):
            plugin.add_to_menu(self, menu_bar)
```

### Plugin Interface Contract

All plugins must implement the expected interface:

#### Menu Plugins
```python
def add_to_menu(parent_window, menu_bar):
    """
    Required function for menu plugins
    
    Args:
        parent_window: BaseWindow instance
        menu_bar: tkinter.Menu instance
    """
    pass
```

#### Widget Plugins (Future)
```python
def create_widget(parent_frame):
    """
    Required function for widget plugins
    
    Args:
        parent_frame: tkinter.Frame instance
        
    Returns:
        Widget instance
    """
    pass
```

## 🎨 Plugin Best Practices

### 1. Error Handling

Always wrap plugin code in try-catch blocks:

```python
def add_to_menu(parent_window, menu_bar):
    try:
        # Plugin implementation
        pass
    except Exception as e:
        logger.error(f"Plugin error: {e}")
        # Graceful fallback or notification
```

### 2. Resource Management

Clean up resources properly:

```python
def cleanup():
    """Called when plugin is being unloaded"""
    # Close files, database connections, etc.
    pass
```

### 3. User Feedback

Provide appropriate user feedback:

```python
def long_running_operation(parent_window):
    parent_window.status_var.set("Processing...")
    try:
        # Long operation
        parent_window.status_var.set("Operation completed")
    except Exception as e:
        parent_window.status_var.set("Operation failed")
        parent_window.show_message(f"Error: {str(e)}")
```

### 4. Plugin Dependencies

Check for required modules/features:

```python
try:
    import required_module
    HAS_FEATURE = True
except ImportError:
    HAS_FEATURE = False

def add_to_menu(parent_window, menu_bar):
    if not HAS_FEATURE:
        logger.warning("Required module not available")
        return
    
    # Plugin implementation
```

### 5. Configuration

Use configuration for customizable behavior:

```python
# Plugin configuration
PLUGIN_CONFIG = {
    'enable_feature_x': True,
    'default_format': 'csv',
    'max_items': 1000
}

def add_to_menu(parent_window, menu_bar):
    if not PLUGIN_CONFIG['enable_feature_x']:
        return
    
    # Plugin implementation using config
```

## 🐛 Plugin Debugging

### Logging

Use the standard logging framework:

```python
import logging
logger = logging.getLogger(__name__)

def add_to_menu(parent_window, menu_bar):
    logger.debug("Plugin initializing")
    # Implementation
    logger.info("Plugin loaded successfully")
```

### Error Reporting

Report plugin errors appropriately:

```python
def add_to_menu(parent_window, menu_bar):
    try:
        # Plugin code
        pass
    except Exception as e:
        logger.exception(f"Plugin {__name__} failed to load")
        # Don't re-raise - allow application to continue
```

## 🚀 Future Plugin Types

The plugin system is designed to support additional plugin types:

### Widget Plugins
```python
# plugin_homepage_widget_quick_add.py
def create_widget(parent_frame):
    """Create a quick transaction entry widget"""
    pass
```

### Data Plugins
```python
# plugin_all_data_backup.py
def schedule_backup():
    """Implement automatic data backup"""
    pass
```

### Report Plugins
```python
# plugin_all_report_monthly.py
def generate_report(start_date, end_date):
    """Generate monthly financial report"""
    pass
```

## 📝 Plugin Development Workflow

1. **Plan Plugin**: Define scope, type, and functionality
2. **Create File**: Follow naming convention exactly
3. **Implement Interface**: Add required functions (e.g., `add_to_menu`)
4. **Add Metadata**: Set `menu_id` and other plugin attributes
5. **Test Plugin**: Verify loading and functionality
6. **Error Handling**: Add robust error handling
7. **Documentation**: Document plugin functionality
8. **Integration**: Test with target windows/scopes

## 🔒 Plugin Security

### Sandboxing Considerations

- **Import Restrictions**: Plugins can import any available module
- **File System Access**: Plugins have full file system access
- **Database Access**: Plugins can access the application database
- **Network Access**: Plugins can make network requests

### Best Practices

- **Code Review**: Review plugin code before deployment
- **Testing**: Thoroughly test plugins in isolated environments
- **User Permissions**: Consider user confirmation for sensitive operations
- **Resource Limits**: Implement timeouts for long-running operations

---

The plugin system provides a powerful way to extend Budget Planner functionality while maintaining clean separation between core application code and custom features. By following the conventions and best practices outlined here, you can create robust, maintainable plugins that enhance the application's capabilities.