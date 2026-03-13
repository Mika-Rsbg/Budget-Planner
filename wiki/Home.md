# Budget Planner Developer Wiki

Welcome to the Budget Planner developer documentation! This wiki provides comprehensive guidance for developers who want to understand, contribute to, or extend this Python GUI budget tracking application.

## 📋 Quick Navigation

### Getting Started
- **[Getting Started](Getting-Started)** - Onboarding guide for new contributors
- **[Development Setup](Development-Setup)** - Environment setup and first run

### Architecture & Design  
- **[Architecture Overview](Architecture-Overview)** - High-level system design and patterns
- **[Core Modules & Structure](Core-Modules-Structure)** - Detailed component breakdown
- **[Database Schema](Database-Schema)** - Data model and relationships

### Development Guides
- **[GUI Development](GUI-Development)** - Working with windows and UI components
- **[Plugin Development](Plugin-Development)** - Creating and extending plugins
- **[Development Workflows](Development-Workflows)** - Common development patterns
- **[Testing & Debugging](Testing-Debugging)** - How to test and debug changes

## 🎯 Project Overview

Budget Planner is a Python GUI application built with Tkinter that provides comprehensive budget tracking and financial management capabilities. The application follows a modular architecture with clear separation between GUI, data handling, and business logic.

### Key Features
- **Modular Architecture**: Clean separation of concerns with base classes and plugins
- **Plugin System**: Extensible design allowing new features without core modifications  
- **Database Integration**: SQLite database with proper schema and foreign key relationships
- **Comprehensive Logging**: Multi-level logging with decorators for debugging and monitoring
- **Responsive GUI**: Tkinter-based interface with consistent styling and layout

### Technology Stack
- **Language**: Python 3.x
- **GUI Framework**: Tkinter with ttk styling
- **Database**: SQLite with foreign key constraints
- **Architecture Pattern**: Plugin-based modular design
- **Logging**: Python's built-in logging module with custom decorators

## 🏗️ Architecture Highlights

The application is structured around several key architectural patterns:

1. **Base Window Classes**: `BaseWindow` (main windows) and `BaseToplevelWindow` (dialogs) provide consistent behavior
2. **Plugin System**: Dynamic loading of plugins with naming convention `plugin_{scope}_{type}_{name}.py`
3. **Database Layer**: Singleton connection pattern with utility modules organized by domain
4. **Configuration Management**: Centralized configuration with pathlib for cross-platform compatibility
5. **Logging Strategy**: Decorator-based logging with multiple output targets and rotation

## 👥 Contributing

This wiki is designed to make contributing to Budget Planner straightforward and efficient. Whether you're fixing a bug, adding a feature, or improving documentation, the guides here will help you understand the codebase and maintain consistency with existing patterns.

### Quick Start for Contributors
1. Read the **[Getting Started](Getting-Started)** guide
2. Review the **[Architecture Overview](Architecture-Overview)** to understand the system
3. Check the **[Development Workflows](Development-Workflows)** for common patterns
4. Follow existing **[coding conventions](Development-Workflows#coding-conventions)** and **[commit guidelines](https://github.com/Mika-Rsbg/Budget-Planner/blob/main/docs/COMMIT_GUIDELINES.md)**

## 📚 Additional Resources

- **[Project README](https://github.com/Mika-Rsbg/Budget-Planner/blob/main/README.md)** - General project information
- **[Branch Guidelines](https://github.com/Mika-Rsbg/Budget-Planner/blob/main/docs/BRANCH_GUIDELINES.md)** - Git workflow standards
- **[Commit Guidelines](https://github.com/Mika-Rsbg/Budget-Planner/blob/main/docs/COMMIT_GUIDELINES.md)** - Commit message format
- **[Logging Guidelines](https://github.com/Mika-Rsbg/Budget-Planner/blob/main/docs/LOGGING_GUIDELINES.md)** - Logging best practices

---

*This documentation is maintained by the Budget Planner development team. If you find errors or have suggestions for improvement, please open an issue or submit a pull request.*