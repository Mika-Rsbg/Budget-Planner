# 📝 Logging Guidelines

## 🎯 Purpose

This document defines the conventions and best practices for logging in this Python project. The goal is to ensure that log output is structured, informative, and useful for debugging, monitoring, and understanding the application's behavior.

---

## 🛠️ Logging Setup Overview

Logs are configured using Python's built-in `logging` module with the following setup:

* **Console output** (level: `DEBUG`)
* **File output to `app.log`** (level: `DEBUG`)
* **File output to `app_no_debug.log`** (level: `INFO`)

**Log format**:

```
%(asctime)s - %(name)s - [%(levelname)s] - %(message)s
```

---

## 📂 Logging Levels & Usage

| Level      | Use For                                                    | Logged In File                         |
| ---------- | ---------------------------------------------------------- | -------------------------------------- |
| `DEBUG`    | Detailed information for diagnosing problems.              | `app.log`, console                     |
| `INFO`     | General runtime events (app start, major actions, status). | `app.log`, `app_no_debug.log`, console |
| `WARNING`  | Indications of potential issues or recoverable problems.   | `app.log`, `app_no_debug.log`, console |
| `ERROR`    | Serious problems, exceptions that are caught and handled.  | `app.log`, `app_no_debug.log`, console |
| `CRITICAL` | Severe errors causing shutdown or serious disruption.      | `app.log`, `app_no_debug.log`, console |

---

## 📏 Best Practices

### ✅ When to Log

* At the **start and end** of major functions.
* Before and after **critical operations** (e.g., file/database access).
* In **exception handling blocks** (`try/except`).
* To **confirm actions** taken (e.g., user actions, API calls, data processed).

### ❌ What Not to Log

* Sensitive data: passwords, tokens, personal user information.
* Excessive debugging output in production unless needed.
* Repetitive logs that add no diagnostic value.

### 📌 Logger Usage Pattern

```python
import logging

logger = logging.getLogger(__name__)

def some_function():
    logger.debug("This is a debug message.")
    logger.info("Something informative happened.")
    logger.warning("This could be a problem.")
    logger.error("An error occurred.")
    logger.critical("Critical failure!")
```

---

## 🧪 Decorator Logging

Use the `@logg` decorator to automatically log when a function starts and ends, including how long it took to run.

### 📚 Implementation

```python
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)

def logg(func):
    """
    Decorator to log the start and end of a function call,
    including its duration.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f'Start: {func.__name__}')
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug(
            f'End: {func.__name__} (Duration: {end - start:.2f}s)'
        )
        return result
    return wrapper
```

### ✅ When to Use

Apply this decorator to functions where:

* You want automatic timing and debug tracing.
* You want to avoid manually writing start/end logs.
* Performance measurement is useful (e.g., in database, file I/O, or GUI operations).

### 📌 Usage Example

```python
@logg
def load_data():
    time.sleep(1.5)
    return "Data loaded"

load_data()
```

### 🧾 Log Output Example

```
2025-05-06 12:01:00,100 - mymodule - [DEBUG] - Start: load_data
2025-05-06 12:01:01,600 - mymodule - [DEBUG] - End: load_data (Duration: 1.50s)
```

---

## 🧼 Clean Setup in `main.py`

Make sure logging is initialized before running the main application logic:

```python
if __name__ == "__main__":
    setup_logging()
    main()
```

---

## 🧾 Example Log Output

```
2025-05-06 12:00:00,123 - __main__ - [INFO] - Application started.
2025-05-06 12:00:01,456 - db.utils - [DEBUG] - Created database schema.
2025-05-06 12:00:02,789 - gui.homepage - [INFO] - Homepage GUI launched.
```

---

## 📎 File Overview

| File               | Purpose                           |
| ------------------ | --------------------------------- |
| `logger_config.py` | Initializes and sets up handlers. |
| `logging_tools.py` | Provides the `@logg` decorator.   |
| `app.log`          | Full log (all levels).            |
| `app_no_debug.log` | Production-level log (INFO+).     |