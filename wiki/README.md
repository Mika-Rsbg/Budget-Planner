# Budget Planner Developer Wiki

This directory contains comprehensive developer documentation for the Budget Planner project. These markdown files are designed to be easily copied to GitHub Wiki pages.

## 📋 Wiki Contents

| Page | Description | Target Audience |
|------|-------------|-----------------|
| **[Home.md](Home.md)** | Wiki landing page with navigation and project overview | All developers |
| **[Getting-Started.md](Getting-Started.md)** | Onboarding guide for new contributors | New developers |
| **[Architecture-Overview.md](Architecture-Overview.md)** | High-level system design and patterns | All developers |
| **[Core-Modules-Structure.md](Core-Modules-Structure.md)** | Detailed component breakdown | All developers |
| **[Database-Schema.md](Database-Schema.md)** | Complete database documentation | Backend developers |
| **[Plugin-Development.md](Plugin-Development.md)** | Creating and extending plugins | Feature developers |
| **[Development-Workflows.md](Development-Workflows.md)** | Common development patterns | All developers |
| **[Testing-Debugging.md](Testing-Debugging.md)** | Testing strategies and debugging guide | All developers |

## 🚀 How to Use This Documentation

### For GitHub Wiki

These markdown files can be directly copied to GitHub Wiki pages:

1. **Create Wiki Pages**: Go to your repository's Wiki tab
2. **Copy Content**: Copy the markdown content from each file
3. **Set Page Titles**: Use the filename (without .md) as the page title
4. **Create Navigation**: Use the Home.md content for the main wiki page

### For Local Documentation

You can also use these files locally:

```bash
# View with any markdown viewer
mdcat wiki/Getting-Started.md

# Or use a markdown preview tool
grip wiki/Home.md --browser

# Convert to other formats with pandoc
pandoc wiki/Architecture-Overview.md -o architecture.pdf
```

## 📚 Documentation Structure

The documentation follows a logical flow:

```
Start Here → Getting Started → Architecture Overview → Core Modules
                    ↓
            Development Workflows ← Plugin Development ← Database Schema
                    ↓
              Testing & Debugging
```

### Learning Path for New Developers

1. **Start with [Getting Started](Getting-Started.md)** - Set up your environment and run the app
2. **Read [Architecture Overview](Architecture-Overview.md)** - Understand the system design
3. **Study [Core Modules](Core-Modules-Structure.md)** - Learn about specific components
4. **Review [Development Workflows](Development-Workflows.md)** - Learn coding patterns
5. **Refer to [Database Schema](Database-Schema.md)** - When working with data
6. **Use [Plugin Development](Plugin-Development.md)** - When adding features
7. **Consult [Testing & Debugging](Testing-Debugging.md)** - When issues arise

### Quick Reference

For experienced developers, key reference sections:

- **Plugin naming**: See Plugin-Development.md#naming-convention
- **Database utilities**: See Core-Modules-Structure.md#database-utilities  
- **Coding style**: See Development-Workflows.md#coding-conventions
- **Architecture patterns**: See Architecture-Overview.md#design-patterns-used

## 🎯 Documentation Goals

This documentation aims to:

- **Reduce onboarding time** for new contributors
- **Explain architectural decisions** and why code is structured this way
- **Provide practical examples** for common development tasks
- **Establish consistent patterns** for future development
- **Enable independent problem-solving** through debugging guides

## 💡 Key Design Principles Covered

The documentation emphasizes these project patterns:

1. **Plugin-Based Architecture**: Extensibility without core modifications
2. **Base Class Inheritance**: Consistent window behavior  
3. **Singleton Database Pattern**: Reliable data access
4. **Decorator Logging**: Automatic timing and debugging
5. **Configuration Centralization**: Single source of truth for settings

## 🔄 Keeping Documentation Updated

This documentation should be updated when:

- **New architectural patterns** are introduced
- **Database schema changes** occur
- **Plugin system evolves** with new types
- **Development workflows change** 
- **New debugging techniques** are discovered

### Contributing to Documentation

When making code changes, please:

1. **Update relevant wiki pages** if behavior changes
2. **Add new examples** for new features
3. **Keep code snippets current** with actual implementation
4. **Maintain consistent formatting** with existing pages

## 📖 External References

The documentation references these external resources:

- **[Branch Guidelines](../docs/BRANCH_GUIDELINES.md)** - Git workflow standards
- **[Commit Guidelines](../docs/COMMIT_GUIDELINES.md)** - Commit message format  
- **[Logging Guidelines](../docs/LOGGING_GUIDELINES.md)** - Logging conventions
- **[Plugin System README](../docs/README_GUI_PLUGIN.md)** - Plugin technical details

## 🤝 Community and Support

This documentation supports the project's goal of making Budget Planner:

- **Easy to understand** for new developers
- **Consistent** in coding patterns and architecture
- **Extensible** through well-documented plugin systems
- **Maintainable** with clear debugging and testing guidance

For questions not covered in the documentation:

- **Open an issue** for clarification requests
- **Start a discussion** for architectural questions
- **Submit a PR** to improve the documentation

---

*This developer documentation makes Budget Planner accessible to contributors while maintaining code quality and architectural consistency.*