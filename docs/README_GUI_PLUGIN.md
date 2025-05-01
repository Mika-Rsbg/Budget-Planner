# 🧩 Plugin System for tkinter GUI

This project demonstrates how a modular plugin system can be integrated into a tkinter-based GUI application. Plugins can extend, for example, the menu without modifying the main application.

---

## 📁 Project Structure

```plaintext
budget-planner/
├── src/
│   └── gui/
│       ├── basewindow.py
│       └── plugins/
│           ├── __init__.py            ← Plugin Loader
│           └── menu_extension/
│               ├── plugin_all_menu_help.py
│               └── plugin_homepage_menu_account.py
```

---

## 🔌 Plugin Concept

### 🔧 File Naming Convention for Plugins:

```plaintext
plugin_<scope>_<type>_<name>.py
```

| Part       | Description                                  |
|------------|----------------------------------------------|
| `plugin`   | fixed prefix for all plugins                 |
| `<scope>`  | `all` for global, otherwise e.g. `homepage` |
| `<type>`   | `menu`                                       |
| `<name>`   | brief description of the function             |

Example: `plugin_homepage_menu_account.py` extends the homepage menu.

---

## 📂 Loading Plugins

All plugins are loaded at application startup via `gui.plugins.__init__.load_plugins()`.

### 🔢 Menu Order via `menu_id`
Each plugin can optionally define a `menu_id` attribute. Plugins are **loaded sorted by `menu_id`**.

```python
menu_id = 10  # e.g. for menu sorting order
```

### Example Plugin:
```python
# plugins/menu_extension/plugin_all_menu_help.py
import tkinter as tk

# No id specified, so it will get the default id of 9999

def add_to_menu(window, menu_bar):
    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="Hilfe", command=lambda:
                          window.show_message("Dies ist die globale Hilfe."))
    menu_bar.add_cascade(label="Hilfe", menu=help_menu)

```

---

## 🛠 Plugin Loader API

### `load_plugins(plugin_type: str, plugin_scope: str) -> list[module]`

- Loads matching plugins based on the filename schema
- Sorts by `menu_id`
- Dynamically imports modules