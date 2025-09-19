# Getting Started

This guide will help you set up the development environment and get the Budget Planner application running on your local machine.

## Prerequisites

- **Python 3.8+** - The application is built with Python
- **tkinter** - Usually comes with Python, required for the GUI
- **SQLite3** - Included with Python for database functionality
- **Git** - For version control and repository management

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Mika-Rsbg/Budget-Planner.git
cd Budget-Planner
```

### 2. Set Up Python Environment (Recommended)

Create a virtual environment to isolate dependencies:

```bash
# Create virtual environment
python -m venv budget_planner_env

# Activate it (Linux/Mac)
source budget_planner_env/bin/activate

# Activate it (Windows)
budget_planner_env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** The requirements.txt file is currently empty as the application primarily uses Python standard library modules.

## Running the Application

### Standard Mode

```bash
python src/main.py
```

This will:
1. Set up logging configuration
2. Create the SQLite database (if it doesn't exist)
3. Launch the main application window in fullscreen mode

### Test Mode

You can run the application in different test modes by modifying `src/main.py`:

```python
# In main.py, set TEST_MODE to True and choose a test function
TEST_MODE: bool = True

# Then uncomment one of these in the main block:
# main_test()       # Test with TransactionPage
# main_fn_test()    # Test database functions
```

## Project Structure Overview

```
Budget-Planner/
├── src/                    # Main source code
│   ├── main.py            # Application entry point
│   ├── config.py          # Configuration settings
│   ├── gui/               # GUI components
│   │   ├── basewindow.py  # Base window class
│   │   ├── homepage/      # Main application window
│   │   ├── plugins/       # Plugin system
│   │   └── ...           # Other GUI components
│   └── utils/             # Utility modules
│       ├── data/          # Database and data handling
│       ├── logging/       # Logging configuration
│       └── ai/            # AI-powered features
├── data/                  # Database files (created at runtime)
├── log/                   # Log files (created at runtime)
├── docs/                  # Project documentation
├── src_old/               # Legacy code (for reference)
└── wiki-docs/             # Developer Wiki documentation
```

## Configuration

The application uses configuration settings defined in `src/config.py`:

```python
class Database:
    PATH = Path(__file__).resolve().parent.parent / 'data' / 'database.db'

class Logging:
    LOG_DIR = Path(__file__).resolve().parent.parent / 'log'
    log_file_name = 'app.log'
    log_file_name_no_debug = 'app_no_debug.log'
```

Key configuration points:
- **Database**: SQLite database stored in `data/database.db`
- **Logging**: Log files stored in `log/` directory
- **GUI**: tkinter-based interface with plugin support

## First Run

When you run the application for the first time:

1. **Database Creation**: The SQLite database will be created with all required tables
2. **Directory Setup**: `data/` and `log/` directories will be created
3. **Initial Data**: Default categories and transaction types will be inserted
4. **GUI Launch**: The main homepage window will open

## Development Workflow

1. **Make Changes**: Edit source files in the `src/` directory
2. **Test Changes**: Run the application to verify functionality
3. **Check Logs**: Review log files in `log/` for debugging information
4. **Follow Conventions**: See [Code Patterns & Conventions](Code-Patterns-and-Conventions) for coding standards

## Troubleshooting

### Common Issues

**tkinter not found:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS (with Homebrew)
brew install python-tk

# Windows: tkinter should be included with Python
```

**Permission errors:**
- Ensure the application has write permissions for `data/` and `log/` directories
- Check that SQLite database file isn't locked by another process

**Import errors:**
- Verify you're running from the project root directory
- Check that all source files are in the correct locations

### Debugging

The application includes comprehensive logging:

- **Console Output**: Real-time logging during development
- **app.log**: Complete log including DEBUG level messages
- **app_no_debug.log**: Production-level logging (INFO and above)

Enable more detailed logging by setting the log level in the logging configuration.

## Next Steps

Once you have the application running:

1. Explore the [Architecture Overview](Architecture-Overview) to understand the design
2. Read about [Modules & Components](Modules-and-Components) for detailed code structure
3. Review [Contributing Guidelines](Contributing-Guidelines) before making changes
4. Check out the [Plugin System](Plugin-System) for extending functionality

## Getting Help

- **Documentation**: Check other Wiki pages for detailed information
- **Code Examples**: Look at existing implementations in the codebase
- **Issues**: Open a GitHub issue for bugs or questions
- **Discussions**: Use GitHub Discussions for general questions