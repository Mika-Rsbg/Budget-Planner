# Budget Planner Wiki Documentation

This directory contains comprehensive developer documentation for the Budget Planner project, designed to be used as GitHub Wiki pages.

## 📚 Documentation Structure

| Page | Description | Audience |
|------|-------------|----------|
| **[Home](Home.md)** | Overview and navigation for all documentation | All developers |
| **[Getting Started](Getting-Started.md)** | Development setup and first steps | New contributors |
| **[Architecture Overview](Architecture-Overview.md)** | High-level design and architectural decisions | All developers |
| **[Modules & Components](Modules-and-Components.md)** | Detailed breakdown of all code modules | Developers extending functionality |
| **[Database Schema](Database-Schema.md)** | Complete database structure and relationships | Database developers |
| **[Plugin System](Plugin-System.md)** | How to create and integrate plugins | Plugin developers |
| **[Contributing Guidelines](Contributing-Guidelines.md)** | How to contribute to the project | All contributors |
| **[Code Patterns & Conventions](Code-Patterns-and-Conventions.md)** | Coding standards and patterns | All developers |

## 🚀 How to Use This Documentation

### For New Developers
1. Start with **[Getting Started](Getting-Started.md)** to set up your environment
2. Read **[Architecture Overview](Architecture-Overview.md)** to understand the big picture
3. Review **[Contributing Guidelines](Contributing-Guidelines.md)** before making changes
4. Use **[Code Patterns & Conventions](Code-Patterns-and-Conventions.md)** as a reference while coding

### For Feature Development
1. Check **[Modules & Components](Modules-and-Components.md)** to understand existing functionality
2. Review **[Database Schema](Database-Schema.md)** if working with data
3. Use **[Plugin System](Plugin-System.md)** for extending functionality
4. Follow **[Code Patterns & Conventions](Code-Patterns-and-Conventions.md)** for consistency

### For Project Maintainers
1. Use all pages as reference for code reviews
2. Update documentation when architectural changes are made
3. Ensure new contributors start with **[Getting Started](Getting-Started.md)**

## 🌐 Setting Up GitHub Wiki

To use this documentation as GitHub Wiki pages:

### Option 1: Manual Copy-Paste
1. Go to your repository's Wiki tab on GitHub
2. Create new pages with the same names as the markdown files
3. Copy the content from each `.md` file to the corresponding Wiki page

### Option 2: Wiki Repository Clone
1. Clone the Wiki repository:
   ```bash
   git clone https://github.com/your-username/Budget-Planner.wiki.git
   ```
2. Copy all `.md` files from `wiki-docs/` to the wiki repository
3. Commit and push:
   ```bash
   cd Budget-Planner.wiki
   cp ../Budget-Planner/wiki-docs/*.md .
   git add *.md
   git commit -m "Add comprehensive developer documentation"
   git push origin master
   ```

### Option 3: Automated Sync (Future Enhancement)
Consider setting up a GitHub Action to automatically sync changes from the `wiki-docs/` folder to the Wiki repository when the main repository is updated.

## 📝 Maintaining Documentation

### When to Update Documentation

- **New Features**: Update relevant modules and add examples
- **Architecture Changes**: Update Architecture Overview and affected pages
- **Database Changes**: Update Database Schema documentation
- **New Patterns**: Add to Code Patterns & Conventions
- **Setup Changes**: Update Getting Started guide

### Documentation Standards

- **Code Examples**: Always include real, working code snippets
- **Up-to-Date**: Keep documentation current with codebase changes
- **Cross-References**: Link between related sections and pages
- **Clarity**: Write for developers unfamiliar with the codebase
- **Completeness**: Cover both the "how" and "why" of implementations

## 🔗 Links to Existing Documentation

This wiki documentation complements the existing documentation in the `/docs` folder:

- **[Branch Guidelines](../docs/BRANCH_GUIDELINES.md)** - Git workflow and branch naming
- **[Commit Guidelines](../docs/COMMIT_GUIDELINES.md)** - Commit message format
- **[Pull Request Guidelines](../docs/PULL_REQUEST_GUIDELINES.md)** - PR standards
- **[Logging Guidelines](../docs/LOGGING_GUIDELINES.md)** - Logging configuration
- **[GUI Plugin Documentation](../docs/README_GUI_PLUGIN.md)** - Plugin system overview

## 🎯 Documentation Goals

This documentation aims to:

1. **Reduce Onboarding Time**: New developers can understand the codebase quickly
2. **Improve Code Quality**: Clear patterns and conventions lead to consistent code
3. **Enable Contributions**: Lower the barrier for community contributions
4. **Preserve Knowledge**: Document design decisions and architectural rationale
5. **Support Growth**: Provide foundation for scaling the development team

## 🤝 Contributing to Documentation

Documentation improvements are welcome! When contributing:

1. **Follow the Style**: Match the existing documentation style and structure
2. **Include Examples**: Provide concrete code examples where applicable
3. **Test Examples**: Ensure all code examples actually work
4. **Cross-Reference**: Link to related sections and external resources
5. **Update Index**: Update this README if adding new documentation pages

## 📞 Getting Help

If you need help understanding any part of the documentation:

1. **Check Cross-References**: Look for links to related sections
2. **Review Code Examples**: Study the provided code snippets
3. **Ask Questions**: Open a GitHub issue or discussion
4. **Suggest Improvements**: Propose documentation enhancements

---

This documentation is a living resource that grows with the project. Keep it current, accurate, and helpful for all developers working on Budget Planner!