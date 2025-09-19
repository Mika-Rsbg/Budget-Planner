# Architecture Overview

This document provides a comprehensive overview of the Budget Planner's architecture, design decisions, and key patterns that drive the application.

## High-Level Architecture

Budget Planner follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────┐
│            GUI Layer                │
│  ┌─────────────┐  ┌─────────────┐   │
│  │  BaseWindow │  │   Plugins   │   │
│  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│          Business Layer             │
│  ┌─────────────┐  ┌─────────────┐   │
│  │   Utils     │  │    AI       │   │
│  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│           Data Layer                │
│  ┌─────────────┐  ┌─────────────┐   │
│  │  Database   │  │   Config    │   │
│  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────┘
```

## Design Principles

### 1. Modular Design
- **Plugin Architecture**: Extensible through plugins without core modifications
- **Component-Based GUI**: Reusable UI components with consistent interfaces
- **Utility Separation**: Clear separation between data, GUI, and business logic

### 2. Decorator Pattern for Cross-Cutting Concerns
- **Logging Decorator**: `@log_fn` provides automatic function-level logging
- **Performance Tracking**: Built into the logging decorator
- **Error Handling**: Centralized through decorators and logging

### 3. Configuration-Driven Development
- **Centralized Config**: All paths and settings in `config.py`
- **Environment Flexibility**: Easy switching between test and production modes
- **Path Management**: Automatic directory creation and path resolution

## Core Components

### Application Entry Point (`main.py`)

The application follows a clean bootstrap pattern:

```python
@log_fn
def main() -> None:
    """Main application entry point"""
    from gui.homepage.homepage import Homepage
    from utils.data.createdatabase_utils import create_database
    
    create_database()
    app = Homepage(fullscreen=True)
    app.run()
```

**Key Features:**
- **Database Initialization**: Ensures database exists before GUI launch
- **Logging Setup**: Comprehensive logging configuration
- **Test Modes**: Multiple test configurations for development

### GUI Architecture

#### BaseWindow Pattern

All GUI components inherit from `BaseWindow`, providing:

```python
class BaseWindow(tk.Tk):
    def __init__(self, plugin_scope: str, title: str = "Fenster",
                 geometry: str = "800x600", bg_color: str = "white",
                 fullscreen: bool = False) -> None:
        # Base window setup
        self._setup_main_frame()
        self._setup_status_bar() 
        self._setup_menu()
        self.init_ui()  # Implemented by subclasses
```

**Design Benefits:**
- **Consistent UI**: Standardized window setup and styling
- **Plugin Integration**: Automatic plugin loading per window scope
- **Status Management**: Built-in status bar and message handling
- **Lifecycle Management**: Proper initialization order

#### Plugin System Architecture

The plugin system uses **file-based discovery** with **naming conventions**:

```
plugin_<scope>_<type>_<name>.py
```

Example: `plugin_homepage_menu_account.py`

**Plugin Loading Process:**
1. **Discovery**: Scan plugin directories for matching files
2. **Filtering**: Match scope (`all`, `homepage`, etc.) and type (`menu`)
3. **Loading**: Dynamic import with error handling
4. **Sorting**: Order by `menu_id` attribute
5. **Integration**: Automatic menu injection

### Data Layer Architecture

#### Database Connection Management

Centralized database handling through `DatabaseConnection`:

```python
class DatabaseConnection:
    @staticmethod
    def get_connection(db_path: Path) -> sqlite3.Connection:
        # Singleton-like connection management
    
    @staticmethod
    def get_cursor(db_path: Path) -> sqlite3.Cursor:
        # Cursor management with connection reuse
```

**Features:**
- **Connection Pooling**: Reuses connections efficiently
- **Transaction Management**: Proper commit/rollback handling
- **Resource Cleanup**: Automatic connection and cursor cleanup

#### Database Schema Design

The schema follows **normalized design** with clear relationships:

```sql
-- Core entities
tbl_Account (Account management)
tbl_Category (Transaction categorization)  
tbl_Counterparty (Transaction parties)
tbl_Transaction (Financial transactions)

-- Supporting entities
tbl_TransactionTyp (Transaction types)
tbl_BudgetPeriod (Budget time periods)
tbl_AccountHistory (Balance history tracking)
```

**Key Design Decisions:**
- **Foreign Keys**: Enforce referential integrity
- **Indexes**: Optimized for common query patterns
- **Default Values**: Sensible fallbacks for optional fields
- **Audit Trail**: Change tracking through history tables

## Data Flow Architecture

### 1. Application Startup Flow

```
main.py
├── setup_logging()
├── create_database()
│   ├── Create tables
│   ├── Insert initial data
│   └── Create indexes
└── Homepage()
    ├── Load account data
    ├── Initialize widgets
    └── Start event loop
```

### 2. Transaction Processing Flow

```
User Input → GUI Validation → Database Utils → Database → UI Update
```

**Example Flow:**
1. **User Action**: Add new transaction through GUI
2. **Validation**: GUI validates input data
3. **Processing**: Utils module handles business logic
4. **Persistence**: Database utils execute SQL operations
5. **Update**: GUI refreshes to show changes

### 3. Plugin Integration Flow

```
Window Creation → Plugin Discovery → Plugin Loading → Menu Integration
```

## Logging Architecture

### Decorator-Based Logging

The `@log_fn` decorator provides comprehensive function tracking:

```python
def log_fn(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.debug(f'Start: {func.__name__}')
        start: float = time.time()
        result: Any = func(*args, **kwargs)
        end: float = time.time()
        logger.debug(f'End: {func.__name__} (Duration: {end - start:.2f}s)')
        return result
    return wrapper
```

**Benefits:**
- **Automatic Tracking**: No manual logging code in functions
- **Performance Metrics**: Built-in duration measurement
- **Consistent Format**: Standardized log message format
- **Debug Information**: Detailed execution flow tracking

### Multi-Level Logging

- **Console**: Real-time debugging output
- **app.log**: Complete application log (DEBUG+)
- **app_no_debug.log**: Production-level log (INFO+)

## Error Handling Strategy

### 1. Exception Hierarchies
Custom exception classes for specific error types:

```python
class Error(Exception):
    """General exception class for database errors."""
    pass
```

### 2. Graceful Degradation
- **Database Errors**: Application continues with limited functionality
- **Plugin Failures**: Core application remains functional
- **GUI Errors**: Individual components fail without crashing the app

### 3. User Feedback
- **Status Bar Updates**: Real-time status information
- **Message Dialogs**: User-friendly error messages
- **Log Details**: Technical details captured in logs

## Performance Considerations

### Database Optimization
- **Indexes**: Strategic indexing for common query patterns
- **Connection Reuse**: Minimize connection overhead
- **Batch Operations**: Efficient bulk data operations

### GUI Performance
- **Lazy Loading**: Load data only when needed
- **Widget Reuse**: Minimize widget creation/destruction
- **Event Handling**: Efficient event delegation

### Memory Management
- **Resource Cleanup**: Proper disposal of database resources
- **Image Caching**: Reuse of GUI resources
- **Plugin Isolation**: Prevent plugin memory leaks

## Security Considerations

### Data Protection
- **Local Storage**: No sensitive data transmitted over network
- **SQL Injection**: Parameterized queries throughout
- **Path Traversal**: Secure file path handling

### Input Validation
- **GUI Validation**: Client-side input validation
- **Database Constraints**: Server-side validation through constraints
- **Type Safety**: Strong typing throughout the application

## Testing Strategy

### Test Modes
The application includes multiple test modes:

- **main_test()**: GUI component testing
- **main_fn_test()**: Database function testing
- **Plugin Testing**: Individual plugin verification

### Development Testing
- **Manual Testing**: GUI interaction testing
- **Database Testing**: Direct database operation testing
- **Integration Testing**: End-to-end workflow testing

## Future Architecture Considerations

### Scalability
- **Multi-User Support**: Database design supports user separation
- **Concurrent Access**: Connection pooling enables concurrent operations
- **Plugin Ecosystem**: Architecture supports third-party plugin development

### Extensibility
- **API Design**: Clean interfaces for extending functionality
- **Configuration**: Flexible configuration system
- **Modular Design**: Easy addition of new features

### Technology Evolution
- **Framework Migration**: Modular design enables GUI framework changes
- **Database Migration**: Abstracted data layer supports database changes
- **Python Version**: Forward-compatible coding practices

---

This architecture provides a solid foundation for the Budget Planner application while maintaining flexibility for future enhancements and modifications.