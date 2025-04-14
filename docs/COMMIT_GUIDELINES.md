# Commit Message Guidelines for Extended SIR Model Project

This document defines the rules and standards for writing commit messages in this repository. Adhering to these guidelines helps maintain a clear, consistent, and understandable project history.

---

## 1. Commit Message Structure

Each commit message must follow the format:

`<type>(<scope>): <short, imperative summary>`

- **type:** Indicates the nature of the commit.
- **scope:** Specifies the part of the project affected.
- **short, imperative summary:** A concise description of the changes in the imperative mood.

### Examples:
- `feat(model): add exposed compartment`
- `fix(simulation): correct integration bug`
- `docs(readme): update model description`
- `style(model): reformat code`
- `refactor(simulation): simplify integration method`
- `test(model): add unit tests for new compartment`
- `chore: update dependency versions`

---

## 2. Commit Message Body

The commit body is optional but recommended when further explanation is needed. It should describe:

- **Why** the change was made.
- **What** issues are addressed.
- **How** the change impacts the system or any side effects.

### Example:

`This commit implements the initial structure of the extended SIR model.
It introduces an 'Exposed' compartment to better simulate the early stages of an outbreak.
The numerical integration method has been updated to a more stable Runge-Kutta variant.`

---

## 3. Commit Message Footer

The footer is used to reference related issues or include additional notes, such as breaking changes or dependencies.

### Example:

`Closes #42`

---

## 4. Allowed Commit Types

Use the following commit types to indicate the nature of your changes:

- **feat:** Adds a new feature.
- **fix:** Fixes a bug.
- **docs:** Changes or updates to documentation.
- **style:** Code formatting changes that do not affect functionality.
- **refactor:** Code refactoring without new features.
- **test:** Adds or modifies tests.
- **chore:** Miscellaneous tasks such as dependency updates or configuration changes.

---

## 5. Commit Scopes

The commit scope helps to specify which part of the project is affected. Use one of the following scopes where applicable:

- **model:** Changes directly related to the SIR or extended SIR algorithm.
- **simulation:** Adjustments in simulation logic.
- **integration:** Modifications to numerical integration methods.
- **api:** Changes to the interface between different components.
- **config:** Updates to configuration files or build processes.
- **gui:** Changes to the GUI.

---

## 6. Final Notes

- **Consistency:** Always follow the specified format to maintain a consistent project history.
- **Clarity:** Ensure that commit messages are clear and descriptive.
- **Imperative Mood:** Write the commit summary in the imperative mood (e.g., "add", "update", "fix").

By following these guidelines, we ensure that our commit history is informative and useful for current and future collaborators.