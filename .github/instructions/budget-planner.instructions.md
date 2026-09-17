---
name: Budget-Planner Python Development
description: "Use when modifying the Budget-Planner Python application, especially Tkinter GUI, SQLite database, repositories, services, plugins, logging, or project workflows."
applyTo: "src/**/*.py"
---
# Budget-Planner Development Instructions

## Architecture

- This is a Python Tkinter budget-tracking application backed by SQLite.
- The application entry point is `src/main.py`. The normal command is `python src/main.py`.
- Keep responsibilities separated between GUI code in `src/gui/`, domain features in `src/features/`, persistence in `src/core/database/`, models in `src/models/`, and shared helpers in `src/shared/`.
- Treat the current source tree as authoritative. The project contains stale references to older `src/utils` and old GUI paths; do not create new code in those paths.

## GUI

- Main windows inherit from `src/gui/app/basewindow.py::BaseWindow`.
- Dialogs inherit from `src/gui/app/basetoplevelwindow.py::BaseToplevelWindow` and receive a `BaseWindow` master.
- Pages are organized below `src/gui/pages/`, including `src/gui/pages/home/homepage.py`.
- Follow the existing initialization flow and implement the window methods expected by neighboring classes, such as `init_ui()`, `show_message()`, and `reload()` where applicable.
- Use the existing ttk `clam` theme, grid-based layout, frame ownership, and established widget styling. Do not introduce a second GUI framework or an unrelated styling system.

## Database And Domain Code

- Access SQLite through `src/core/database/connection.py::DatabaseConnection`; preserve its singleton connection and cursor behavior unless a deliberate refactor is required.
- Put schema creation and changes in `src/core/database/schema.py` and preserve foreign-key behavior, indexes, and existing table naming conventions.
- Put domain persistence and behavior in the appropriate `src/features/<domain>/` repository or service rather than embedding SQL in GUI pages.
- Use the existing model entities in `src/models/` and shared conversion helpers in `src/shared/` where applicable.
- Keep database resources and transactions explicit. Do not silently create a second connection or bypass the repository/service boundary.

## Plugins

- Plugins live in `src/gui/plugins/`, primarily `menu_extension/`, and are loaded dynamically by `src/gui/plugins/__init__.py`.
- Name menu plugins `plugin_{scope}_{type}_{name}.py`, for example `plugin_homepage_menu_account.py`.
- Expose the existing `add_to_menu(window, menu_bar)` interface.
- Use a `menu_id` for ordering when a plugin needs a defined position; use the established increments of 10 where practical. Plugins without an ID sort last.
- Prefer a plugin for menu-only extensions instead of modifying core window code.

## Logging And Errors

- Use `logging.getLogger(__name__)` in modules.
- Use the existing `@log_fn` decorator from `src/core/logging/logging_tools.py` for significant functions when neighboring code does so, especially service, repository, and lifecycle operations.
- Preserve the configured log levels and destinations managed by `src/core/logging/logger_config.py`.
- Catch specific exceptions, log useful context at an appropriate level, and surface user-facing errors through the existing GUI messaging conventions.
- Do not catch broad `Exception` unless the boundary genuinely needs a last-resort handler and re-raises or reports the failure appropriately.

## Code Quality

- Add type hints for all function parameters and return values.
- Follow the surrounding module's naming, import, and formatting style; keep changes focused and avoid unrelated refactors.
- Add concise docstrings with `Args` and `Returns` sections for public functions whose behavior is not obvious.
- Do not add dependencies without updating `requirements.txt`; verify whether a dependency is already available first.
- Preserve public APIs and existing data compatibility unless the task explicitly requires a breaking change.

## Verification

- Run `python src/main.py` for a normal application smoke test when a display is available.
- Use the available `main_test()` or `main_fn_test()` entry points in `src/main.py` for targeted manual checks; they are not command-line switches.
- No automated test suite is currently configured. When changing database or domain behavior, add or run the narrowest practical manual check and inspect the relevant log output.
- Remember that `requirements.txt` is currently empty and that `Budget-Planner.pyproj` contains stale file entries; do not treat either as a complete inventory of the live source tree.

## Git And Pull Requests

- Use branch names `feat/<description>`, `fix/<description>`, `hotfix/<description>`, or `release/<version>`.
- Use imperative commit subjects in the form `<type>(<scope>): <short summary>`, such as `fix(database): close stale cursors`.
- Pull requests should state what changed, why, how it was implemented, and how it was tested; target the correct base branch and link related issues with `Closes #X` when applicable.