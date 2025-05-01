# 🧩 Plugin System (tkinter)

This file explains how the plugin system for the Budget Planner works. The plugin system is designed to be flexible and allows for easy integration of new features without modifying the core codebase. This is particularly useful for maintaining a clean architecture and enabling third-party developers to contribute plugins.

---

## 📁 Project Structure

```plaintext
src/gui/plugins/
├── __init__.py      ← Plugin-Loader
└── menu_extension/
    ├── plugin_all_menu_help.py
    └── plugin_homepage_menu_account.py
```

---

## File Naming

```plaintext
plugin_<scope>_<type>_<name>.py
```

| Part       | Description                                  |
|------------|----------------------------------------------|
| `plugin`   | fixed prefix for all plugins                 |
| `<scope>`  | `all` for global, otherwise e.g. `homepage`  |
| `<type>`   | `menu`                                       |
| `<name>`   | brief description of the function            |

Example: `plugin_homepage_menu_account.py` extends the homepage menu.

---

## 📂 Loading Plugins

All plugins are loaded during application and during the start of windows startup via `gui.plugins.__init__.load_plugins()`.

The function `load_plugins(plugin_type: str, plugin_scope: str) -> list[module]` returns a list of plugin modules, which you can then process:

```python
for plugin in load_plugins("menu", self.plugin_scope):
    if hasattr(plugin, "add_to_menu"):
        plugin.add_to_menu(self, menu_bar)
```

### 🔢 Menu Order via `menu_id`

Each plugin can optionally define a `menu_id` attribute. Plugins are **loaded sorted by `menu_id`**.

Tips for `menu_id`:
- Go up in increments of 10 (e.g. 10, 20, 30) to leave space for future plugins.

```python
menu_id = 10  # e.g. for menu sorting order
```

### Example Plugin

```python
# plugins/menu_extension/plugin_all_menu_help.py
import tkinter as tk

# If no id is specified, the default id of 9999 is assigned
menu_id = 5

def add_to_menu(window, menu_bar):
    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(
        label="Hilfe",
        command=lambda: window.show_message("Dies ist die globale Hilfe."))
    menu_bar.add_cascade(label="Hilfe", menu=help_menu)

```

---

## 🛠 Plugin Loader API

### `load_plugins(plugin_type: str, plugin_scope: str) -> list[module]`

- Loads matching plugins based on the filename schema
- Sorts by `menu_id`
- Dynamically imports modules

---

## 🛠 Defining Custom Scopes per Window

You can define custom scopes for each window in the code. To do this, change the `plugin_scope: str = None` parameter in the window class initialization to the desired scope:

```python
class MyWindow(BaseWindow):
    def __init__(self, ..., plugin_scope: str = "mywindow"):
        super().__init__(..., plugin_scope=plugin_scope)
        # window-specific initialization
```

This way, only plugins with this scope and the global `all` scope will be loaded.