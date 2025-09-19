# Contributing Guidelines

Welcome to the Budget Planner project! We appreciate your interest in contributing. This guide will help you understand our development process, coding standards, and how to make meaningful contributions to the project.

## 🚀 Quick Start for Contributors

1. **Fork the Repository**: Create your own fork of the Budget Planner repository
2. **Set Up Development Environment**: Follow the [Getting Started](Getting-Started) guide
3. **Choose an Issue**: Look for issues labeled `good first issue` or `help wanted`
4. **Create a Branch**: Follow our [Branch Guidelines](../docs/BRANCH_GUIDELINES.md)
5. **Make Changes**: Implement your feature or fix following our coding standards
6. **Test Your Changes**: Ensure everything works as expected
7. **Submit a Pull Request**: Follow our [Pull Request Guidelines](../docs/PULL_REQUEST_GUIDELINES.md)

## 📋 Development Workflow

### 1. Setting Up Your Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Budget-Planner.git
cd Budget-Planner

# Create virtual environment
python -m venv budget_planner_env
source budget_planner_env/bin/activate  # Linux/Mac
# OR: budget_planner_env\Scripts\activate  # Windows

# Install dependencies (if any)
pip install -r requirements.txt
```

### 2. Branch Management

Follow our branching strategy as outlined in [`docs/BRANCH_GUIDELINES.md`](../docs/BRANCH_GUIDELINES.md):

```bash
# Always branch from develop (or main if no develop)
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feat/your-feature-name

# Or bug fix branch  
git checkout -b fix/issue-description
```

### 3. Making Changes

#### Code Organization
- **Follow existing patterns**: Look at similar implementations in the codebase
- **Respect module boundaries**: Don't mix GUI code with database logic
- **Use the plugin system**: For new features that extend functionality
- **Maintain separation of concerns**: Keep business logic separate from presentation

#### Testing Your Changes

##### Manual Testing
```bash
# Test main application
python src/main.py

# Test specific components (modify main.py)
# Set TEST_MODE = True and uncomment desired test function
python src/main.py
```

##### Database Testing
```bash
# Test database functions individually
# Use main_fn_test() mode for isolated database testing
```

##### Plugin Testing
```bash
# Create test plugins following naming convention
# Use "test" scope for development plugins
plugin_test_menu_example.py
```

### 4. Code Quality Standards

#### Logging
All functions should use the `@log_fn` decorator for consistency:

```python
from utils.logging.logging_tools import log_fn

@log_fn
def your_function():
    """Function with automatic logging"""
    pass
```

#### Error Handling
Implement proper error handling with informative messages:

```python
try:
    # Your code
    pass
except SpecificException as e:
    logger.error(f"Specific error occurred: {e}")
    # Handle gracefully
except Exception as e:
    logger.exception(f"Unexpected error in {__name__}")
    # Prevent crash, inform user
```

#### Database Operations
Always use the database utilities and connection management:

```python
from utils.data.database_connection import DatabaseConnection
from utils.data.database.account_utils import get_account_data

# Good: Use existing utility functions
accounts = get_account_data()

# Avoid: Direct database access in GUI code
```

## 🔍 Code Review Process

### Before Submitting

1. **Self-Review**: Review your own changes thoroughly
2. **Test All Paths**: Test both success and error scenarios
3. **Check Logs**: Verify logging output is appropriate
4. **Documentation**: Update relevant documentation
5. **Clean History**: Squash commits if necessary

### Pull Request Requirements

#### Required Information
- **Clear Description**: Explain what changes you made and why
- **Issue Reference**: Link to related issues (`Fixes #123`)
- **Testing Notes**: Describe how you tested the changes
- **Screenshots**: For UI changes, include before/after screenshots

#### Code Quality Checklist
- [ ] Code follows existing patterns and style
- [ ] All functions use appropriate logging
- [ ] Error handling is implemented where needed
- [ ] No debugging code or commented-out lines
- [ ] Database operations use proper utilities
- [ ] Plugin naming conventions followed (if applicable)

### Review Process

1. **Automated Checks**: Ensure code compiles and follows basic standards
2. **Manual Review**: Code will be reviewed for functionality and style
3. **Testing**: Changes will be tested in development environment
4. **Feedback**: Address any review comments or requested changes
5. **Approval**: Once approved, changes will be merged

## 🎯 Contribution Areas

### 🐛 Bug Fixes

Perfect for first-time contributors:
- **Database Issues**: SQL query problems or data inconsistencies
- **GUI Bugs**: Interface problems or user experience issues
- **Logging Problems**: Missing or incorrect log messages
- **Performance Issues**: Slow operations or resource leaks

**Where to Look**:
- GitHub Issues labeled `bug`
- User-reported problems
- TODO comments in code
- Performance bottlenecks

### ✨ Feature Development

#### GUI Enhancements
- **New Windows**: Additional financial management screens
- **Widget Improvements**: Better account display or transaction entry
- **User Experience**: Keyboard shortcuts, tooltips, better navigation
- **Accessibility**: Screen reader support, high contrast themes

#### Database Features
- **Report Generation**: Monthly/yearly financial reports
- **Data Import/Export**: Support for additional file formats
- **Advanced Queries**: Complex financial analysis queries
- **Data Validation**: Enhanced input validation and constraints

#### Plugin Development
- **Menu Extensions**: New menu items and functionality
- **Data Tools**: Backup, restore, or migration utilities
- **Integration**: Connect with external financial services
- **Automation**: Scheduled tasks or automatic categorization

### 📚 Documentation

- **Code Comments**: Improve inline documentation
- **Wiki Pages**: Expand developer documentation
- **User Guides**: End-user documentation and tutorials
- **API Documentation**: Document functions and classes
- **Examples**: Code examples and usage patterns

### 🧪 Testing

- **Unit Tests**: Test individual functions and components
- **Integration Tests**: Test workflows and interactions
- **UI Tests**: Automated GUI testing
- **Performance Tests**: Benchmark critical operations
- **Error Handling Tests**: Verify graceful error handling

## 📝 Coding Standards

### Python Style Guidelines

#### General Principles
- **PEP 8 Compliance**: Follow Python's official style guide
- **Descriptive Names**: Use clear, descriptive variable and function names
- **Type Hints**: Include type hints for function parameters and returns
- **Docstrings**: Provide clear documentation for all public functions

#### Specific Conventions

##### Naming Conventions
```python
# Variables and functions: snake_case
user_name = "example"
def get_user_data():
    pass

# Classes: PascalCase
class BaseWindow:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3
```

##### Database Naming
```python
# Table names: tbl_TableName
# Primary keys: i8_TableNameID
# String fields: str_FieldName
# Numeric fields: real_FieldName or i8_FieldName
```

##### Import Organization
```python
# Standard library imports
import os
import sys
import logging

# Third-party imports
import tkinter as tk

# Local application imports
from utils.logging.logging_tools import log_fn
from gui.basewindow import BaseWindow
```

#### Function Structure
```python
@log_fn
def example_function(param1: str, param2: int = 0) -> bool:
    """
    Brief description of function purpose.
    
    Args:
        param1 (str): Description of parameter
        param2 (int, optional): Description with default value
        
    Returns:
        bool: Description of return value
        
    Raises:
        ValueError: When input is invalid
        DatabaseError: When database operation fails
    """
    try:
        # Implementation
        return True
    except Exception as e:
        logger.error(f"Error in example_function: {e}")
        raise
```

### GUI Development Standards

#### Window Structure
```python
class YourWindow(BaseWindow):
    def __init__(self, specific_params):
        super().__init__(
            plugin_scope="your_scope",
            title="Your Window Title",
            geometry="800x600"
        )
        
    def init_ui(self):
        """Implement the abstract method from BaseWindow"""
        # UI setup code here
        pass
```

#### Widget Naming
```python
# Descriptive names with widget type
self.account_name_label = tk.Label(...)
self.amount_entry = tk.Entry(...)
self.submit_button = tk.Button(...)
```

#### Event Handlers
```python
@log_fn
def on_submit_clicked(self):
    """Handle submit button click"""
    # Event handling code
    pass
```

### Database Development Standards

#### Query Functions
```python
@log_fn
def get_transactions_by_account(account_id: int, 
                               start_date: str = None,
                               end_date: str = None) -> List[Tuple]:
    """
    Retrieve transactions for an account within date range.
    
    Args:
        account_id (int): Account identifier
        start_date (str, optional): Start date in YYYY-MM-DD format
        end_date (str, optional): End date in YYYY-MM-DD format
        
    Returns:
        List[Tuple]: List of transaction records
    """
    conn = DatabaseConnection.get_connection()
    cursor = DatabaseConnection.get_cursor()
    
    try:
        # Parameterized query to prevent SQL injection
        query = """
            SELECT t.i8_TransactionID, t.str_Date, t.real_Amount, t.str_Purpose
            FROM tbl_Transaction t
            WHERE t.i8_AccountID = ?
        """
        params = [account_id]
        
        if start_date:
            query += " AND t.str_Date >= ?"
            params.append(start_date)
            
        if end_date:
            query += " AND t.str_Date <= ?"
            params.append(end_date)
            
        cursor.execute(query, params)
        return cursor.fetchall()
        
    except sqlite3.Error as e:
        logger.error(f"Database error in get_transactions_by_account: {e}")
        raise
    finally:
        DatabaseConnection.close_cursor()
```

## 🔧 Common Development Tasks

### Adding a New Window

1. **Create Window Class**:
```python
# src/gui/your_feature/your_window.py
from gui.basewindow import BaseWindow

class YourWindow(BaseWindow):
    def __init__(self):
        super().__init__(plugin_scope="your_feature")
        
    def init_ui(self):
        # Implement UI setup
        pass
```

2. **Create Plugin Integration**:
```python
# src/gui/plugins/menu_extension/plugin_all_menu_your_feature.py
menu_id = 300

def add_to_menu(parent_window, menu_bar):
    # Add menu item to launch your window
    pass
```

### Adding Database Functionality

1. **Create Utility Module**:
```python
# src/utils/data/database/your_feature_utils.py
from utils.data.database_connection import DatabaseConnection

@log_fn
def your_database_function():
    # Database operations
    pass
```

2. **Update Schema** (if needed):
```python
# Add to createdatabase_utils.py
def create_your_table(cursor, conn):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tbl_YourTable (
            i8_YourTableID INTEGER PRIMARY KEY AUTOINCREMENT,
            str_YourField TEXT NOT NULL
        );
    """)
```

### Creating a Plugin

1. **Choose Naming**:
```
plugin_<scope>_<type>_<name>.py
```

2. **Implement Interface**:
```python
menu_id = 200  # Ordering

def add_to_menu(parent_window, menu_bar):
    # Plugin implementation
    pass
```

## 🐛 Debugging and Troubleshooting

### Using the Logging System

#### Enable Debug Logging
```python
# In logger_config.py, set level to DEBUG
logging.basicConfig(level=logging.DEBUG)
```

#### Add Debug Information
```python
logger.debug(f"Processing account {account_id}")
logger.info(f"Created {len(transactions)} transactions")
logger.warning(f"Invalid date format: {date_str}")
logger.error(f"Database connection failed: {error}")
```

### Common Issues

#### Database Connection Problems
```python
try:
    conn = DatabaseConnection.get_connection()
    # Database operations
except sqlite3.Error as e:
    logger.error(f"Database error: {e}")
    # Handle gracefully
```

#### Plugin Loading Failures
- Check filename follows naming convention exactly
- Verify `menu_id` is defined
- Check for syntax errors in plugin file
- Review logs for import errors

#### GUI Layout Issues
- Use `.grid()` or `.pack()` consistently within same parent
- Check for conflicting geometry managers
- Verify parent-child widget relationships

## 🎉 Recognition

Contributors are recognized in several ways:
- **GitHub Contributors**: Automatic recognition in repository
- **Release Notes**: Major contributors mentioned in releases
- **Code Comments**: Credit for significant implementations
- **Community**: Recognition in project discussions

## 📞 Getting Help

### Development Questions
- **GitHub Discussions**: For general development questions
- **Issues**: For bug reports or feature requests
- **Wiki**: Comprehensive documentation and examples
- **Code Comments**: Inline documentation and examples

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community discussion
- **Pull Request Comments**: Code-specific discussions

---

Thank you for contributing to Budget Planner! Your efforts help make financial management more accessible and effective for everyone.