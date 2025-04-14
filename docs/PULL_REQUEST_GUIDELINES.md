# Pull Request Guidelines for Extended SIR Model Repository

This document defines the rules and standards for creating pull requests in this repository. Adhering to these guidelines helps maintain a clear, consistent, and review-friendly project history.

---

## 1. Pull Request Title (Name)

- **Purpose:** The title should be short, descriptive, and written in the imperative mood.
- **Content:** It should reflect the main purpose of the changes and, if possible, indicate the affected part of the project.

**Examples:**
- `feat(model): Add exposed compartment to SIR model`
- `fix(simulation): Correct integration error in simulation`

---

## 2. Pull Request Description

The description should provide detailed context for the changes, including:

- **What** has been changed? (Describe the modifications)
- **Why** were these changes necessary? (E.g., bug fixes, new features, improvements)
- **How** were the changes tested? (Briefly explain testing approaches)
- **References** to related issues or discussions (e.g., `Closes #42`)

**Example:**

This pull request implements the new 'Exposed' compartment for the extended SIR model.
It addresses inaccuracies in early outbreak simulations and improves overall model performance.
Additional unit tests have been added to verify the new functionality. Closes #42.

---

## 3. Base Branch

- **Definition:** The base branch is the target branch into which the pull request will be merged.
- **Guidelines:**
  - Ensure that the pull request is created against the correct branch (e.g., `main` or `develop`).
  - Keep the base branch updated to minimize merge conflicts.

**Example:**

Base: main

---

## 4. Merge Strategy

- **Pre-Merge Checks:** 
  - Verify that all review comments have been addressed.
  - Ensure that all CI/CD tests have passed successfully.
- **Merge Methods:** Use the repository’s defined merge strategy (e.g., "Squash and Merge", "Rebase and Merge", or "Merge Commit").
- **Steps for a Clean Merge:**
  1. Rebase your feature branch onto the latest base branch.
  2. Resolve any conflicts that may arise.
  3. Update the pull request with the rebased commits.
  4. Once approved and tests pass, merge the pull request using the chosen strategy.

---

By following these guidelines, we ensure that pull requests are consistent, informative, and easy to review, leading to a smoother collaboration process and a more maintainable codebase.
