import os
import importlib


def load_plugins(plugin_type: str, plugin_scope: str):
    base_path = os.path.dirname(__file__)
    base_package = "gui.plugins"
    plugins = []

    for root, _, files in os.walk(base_path):
        for filename in files:
            if not filename.endswith(".py") or filename.startswith("__"):
                continue

            parts = filename[:-3].split("_")
            if len(parts) < 4:
                continue

            prefix, scope, p_type, _ = parts[:4]
            if prefix != "plugin" or p_type != plugin_type:
                continue

            if scope == "all" or scope == plugin_scope:
                relative_path = os.path.relpath(root, base_path)
                module_path = (
                    f"{base_package}.{relative_path.replace(os.sep, '.')}"
                    if relative_path != "." else base_package
                )
                module_name = f"{module_path}.{filename[:-3]}"
                try:
                    module = importlib.import_module(module_name)
                    # fallback falls keine id
                    menu_id = getattr(module, "menu_id", 9999)
                    plugins.append((scope, menu_id, module))
                except Exception as e:
                    print(f"Fehler beim Laden von Plugin {filename}: {e}")

    # Sortieren: zuerst "all", dann andere scopes, jeweils nach menu_id
    sorted_plugins = sorted(
        plugins, key=lambda item: (0 if item[0] == "all" else 1, item[1])
    )
    return [mod for _, _, mod in sorted_plugins]
