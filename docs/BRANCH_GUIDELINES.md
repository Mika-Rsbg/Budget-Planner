# Branch Guidelines for Extended SIR Model Repository

This document outlines the standards and conventions for branch creation, naming, and merging in this repository. Adhering to these guidelines ensures a consistent workflow and a clean project history.

---

## 1. Branch Structure

- **Main Branches:**
  - **`main`:** Contains production-ready code.
  - **`develop`:** Serves as the integration branch for features and fixes.

- **Supporting Branches:**
  - **Feature Branches:** For new functionalities. Prefix with `feat/` (e.g., `feat/add-exposed-compartment`).
  - **Bugfix Branches:** For fixing errors or issues. Prefix with `fix/` (e.g., `fix/numerical-integration`).
  - **Hotfix Branches:** For critical fixes in production. Prefix with `hotfix/` (e.g., `hotfix/crash-on-launch`).
  - **Release Branches:** For preparing a new release. Prefix with `release/` (e.g., `release/v1.2.0`).

---

## 2. Branch Naming Conventions

- **Consistency:**  
  Use lowercase letters and hyphens to separate words for clarity and consistency.

- **Descriptiveness:**  
  Ensure branch names are descriptive yet concise, directly reflecting the changes or features being developed.

**Examples:**
- Feature: `feat/add-exposed-compartment`
- Bugfix: `fix/numerical-integration`
- Hotfix: `hotfix/fix-login-error`
- Release: `release/v1.2.0`

---

## 3. Branch Workflow

- **Branch Off:**  
  Always create new branches from the most recent `develop` (or `main` when applicable) to minimize merge conflicts.

- **Regular Updates:**  
  Frequently update your branch with changes from the base branch to keep it in sync and reduce potential conflicts.

- **Pull Requests:**  
  Merge branches via pull requests to ensure proper code review and integration before merging into `develop` or `main`.

---

## 4. Merging and Cleanup

- **Merge Strategy:**  
  Follow the repository’s defined merge strategy (e.g., "Squash and Merge", "Rebase and Merge", or "Merge Commit") when integrating changes.

- **Branch Deletion:**  
  Once a branch has been merged and is no longer needed, delete it to maintain a clean repository.

---

By following these branch guidelines, we ensure a structured and efficient development process that minimizes conflicts and clarifies project history.
