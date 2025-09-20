# Budget-Planner AI Agent Instructions

## Project Architecture

This is a Python GUI budget tracking application using Tkinter with SQLite database storage. The project follows a modular architecture with clear separation between GUI, data handling, and utilities.

### Core Structure
- **Entry point**: `src/main.py` - Creates database and launches `Homepage` GUI
- **GUI hierarchy**: Two base classes - `BaseWindow` (tk.Tk) for main windows, `BaseToplevelWindow` (tk.Toplevel) for dialogs
- **Database**: SQLite with singleton connection pattern via `DatabaseConnection` class
- **Configuration**: Centralized in `src/config.py` with path management

### Key Components
- `src/gui/basewindow.py` - Base class for main application windows with plugin loading
- `src/gui/basetoplevelwindow.py` - Base class for modal dialogs and popup windows
- `src/gui/homepage/homepage.py` - Main application interface showing account widgets
- `src/utils/data/createdatabase_utils.py` - Database schema creation and management
- `src/utils/logging/` - Comprehensive logging system with decorators and file rotation

## Development Patterns

### Database Layer
- Uses singleton pattern (`DatabaseConnection.get_connection()`)
- Database utilities are organized by domain: `account_utils.py`, `transaction_utils.py`, etc.
- Schema creates tables: `tbl_Transaction`, `tbl_Account`, `tbl_Category`, `tbl_Counterparty`
- Foreign key relationships with cascade/set null behaviors

### GUI Architecture
- **Window Types**: Main windows inherit from `BaseWindow`, dialogs from `BaseToplevelWindow`
- **Plugin system**: Plugins named `plugin_{scope}_{type}_{name}.py` with auto-loading and `menu_id` ordering
- **Styling**: Both base classes use ttk.Style with "clam" theme and consistent background colors
- **Layout**: Grid-based with proper frame management and responsive design
- **Common Methods**: All windows have `init_ui()`, `show_message()`, and `reload()` methods

### Plugin System Details
- **Naming Convention**: `plugin_{scope}_{type}_{name}.py` (e.g., `plugin_homepage_menu_account.py`)
- **Scopes**: `all` for global plugins, specific window names for targeted functionality
- **Menu Ordering**: Use `menu_id` attribute (increment by 10s: 10, 20, 30) for consistent menu ordering
- **Auto-Loading**: Plugins loaded via `load_plugins(plugin_type, plugin_scope)` during window initialization
- **Location**: All plugins in `src/gui/plugins/` with subdirectories for organization

### Logging Strategy
- **Decorator pattern**: Use `@log_fn` decorator for automatic function timing and entry/exit logging
- **Multi-level logging**: DEBUG to `app.log`, INFO+ to `app_no_debug.log` and console
- **Format**: `%(asctime)s - %(name)s - [%(levelname)s] - %(message)s`
- **Location**: Centrally configured via `config.Logging` class with automatic directory creation

### Data Flow
1. Application starts in `main.py` → creates database → launches Homepage
2. Homepage loads account widgets from database via `get_account_data()`
3. User interactions trigger navigation to specialized pages (transactions, categories)
4. All database operations go through utility modules in `src/utils/data/database/`

## Development Workflows

### Running the Application
```bash
python src/main.py          # Production mode
python -c "from src.main import main_test; main_test()"  # Test mode
```

### Adding New Features
1. **Main Windows**: Inherit from `BaseWindow`, implement `init_ui()` method
2. **Modal Dialogs**: Inherit from `BaseToplevelWindow` with master window parameter
3. **Database Tables**: Add creation logic to `createdatabase_utils.py` with proper foreign keys
4. **Plugins**: Follow `plugin_{scope}_{type}_{name}.py` naming, implement required interface methods
5. **Utilities**: Organize by domain in appropriate `utils/` subdirectory with logging decorators

### Code Conventions
- **Type hints**: Required for all function parameters and returns
- **Logging**: Add `@log_fn` decorator to significant functions for automatic timing
- **Error handling**: Use specific exception classes, log errors with appropriate levels
- **Documentation**: Docstrings with Args/Returns sections, follow logging guidelines
- **GUI Methods**: Implement `init_ui()`, `show_message()`, and `reload()` in all window classes

## Development Guidelines

### Branch Management
- **Feature branches**: `feat/description` (e.g., `feat/add-transaction-filters`)
- **Bug fixes**: `fix/description` (e.g., `fix/database-connection-leak`)
- **Hotfixes**: `hotfix/description` for critical production issues
- **Releases**: `release/version` (e.g., `release/v1.2.0`)

### Commit Message Format
```
<type>(<scope>): <short imperative summary>

- feat(gui): add new transaction filtering dialog
- fix(database): resolve connection timeout issues  
- docs(readme): update installation instructions
- style(logging): reformat logging configuration
- refactor(plugins): simplify plugin loading mechanism
```

### Pull Request Standards
- **Title**: Imperative mood reflecting main purpose
- **Description**: What, why, how, and testing approach
- **Base Branch**: Target correct branch (main/develop)
- **References**: Link related issues with "Closes #X"

## Important Context

- **Empty requirements.txt**: Dependencies not properly tracked yet
- **AI Integration**: Basic rule-based budget suggestions in `src/utils/ai/`
- **Plugin Architecture**: Extensible design for adding features without core modifications
- **Path Management**: Uses `pathlib.Path` with relative project structure
- **Test Infrastructure**: Separate test mode available via `main_test()`

When modifying this codebase, maintain the established patterns for database access, GUI inheritance, logging decoration, and plugin organization.