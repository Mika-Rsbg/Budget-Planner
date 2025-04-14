# 🧩 Plugin-System für tkinter GUI

Dieses Projekt zeigt, wie ein modulares Plugin-System in eine tkinter-basierte GUI-Anwendung integriert werden kann. Plugins erweitern z. B. das Menü, ohne die Hauptanwendung zu verändern.

---

## 📁 Projektstruktur

```plaintext
project_root/
├── src/
│   └── gui/
│       ├── base_window.py
│       └── plugins/
│           ├── __init__.py            ← Plugin-Loader
│           └── menu_extension/
│               ├── plugin_all_menu_help.py
│               └── plugin_homepage_menu_extra.py
```

---

## 🔌 Plugin-Konzept

### 🔧 Namenskonvention für Plugin-Dateien:

```plaintext
plugin_<scope>_<type>_<name>.py
```

| Teil         | Beschreibung                               |
|--------------|--------------------------------------------|
| `plugin`     | fixer Prefix für alle Plugins              |
| `<scope>`    | `all` für global, sonst z. B. `homepage`   |
| `<type>`     | z. B. `menu`, `toolbar`, `window`          |
| `<name>`     | Kurzbeschreibung der Funktion              |

Beispiel: `plugin_homepage_menu_extra.py` erweitert das Menü der Homepage.

---

## 📂 Plugins laden

Alle Plugins werden beim Start der App über `gui.plugins.__init__.load_plugins()` geladen.

### 🔢 Menü-Reihenfolge via `menu_id`
Jedes Plugin kann (optional) ein Attribut `menu_id` definieren. Plugins werden **sortiert nach Scope und `menu_id`** geladen.

```python
menu_id = 10  # z. B. für Sortierreihenfolge im Menü
```

### Beispielplugin:
```python
# src/gui/plugins/menu_extension/plugin_all_menu_help.py
import tkinter as tk

menu_id = 1

def add_to_menu(window, menu_bar):
    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(
        label="Hilfe", 
        command=lambda: window.show_message("Dies ist die globale Hilfe."))
    menu_bar.add_cascade(label="Hilfe", menu=help_menu)
```

---

## 🛠 Plugin-Loader API

### `load_plugins(plugin_type: str, plugin_scope: str) -> list[module]`

- Lädt passende Plugins anhand des Dateinamenschemas
- Sortiert nach Scope und `menu_id`
- Importiert Module dynamisch