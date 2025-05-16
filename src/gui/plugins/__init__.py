import os
import importlib
import logging
from utils.logging.logging_tools import logg


logger = logging.getLogger(__name__)


@logg
def load_plugins(plugin_type: str, plugin_scope: str):
    """
    Load plugins from the specified directory based on their type and scope.

    Args:
        plugin_type (str): Typ des Plugins (z.B. "data", "gui").
        plugin_scope (str): Typ des Scopes (z.B. "all", "local", "global").
    Returns:
        list: List of loaded plugin modules.
    """
    error_during_import: bool = False
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
                    logger.exception(
                        f"Fehler beim Laden des Plugins {filename}: {e}"
                    )
                    error_during_import = True

    # Sortieren: zuerst "all", dann andere scopes, jeweils nach menu_id
    sorted_plugins = sorted(plugins, key=lambda item: item[1])

    if error_during_import:
        logger.warning(
            "There were errors during the import of some plugins. "
        )
    else:
        logger.info(
            "All plugins were imported successfully."
        )
    return [mod for _, _, mod in sorted_plugins]
