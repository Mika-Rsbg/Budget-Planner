from pathlib import Path


class Database:
    PATH = Path(__file__).resolve().parent.parent / 'data' / 'database.db'


class Logging:
    LOG_DIR = Path(__file__).resolve().parent.parent / "log"

    _log_file_name = "app.log"
    _log_file_name_no_debug = "app_no_debug.log"
    _log_file_name_last = "last.log"
    _log_file_name_last_no_debug = "last_no_debug.log"

    @classmethod
    def ensure_log_directory_exists(cls):
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def set_to_test_mode(cls):
        cls.LOG_DIR = Path(__file__).resolve().parent.parent / "log" / "test"
        cls._log_file_name = "test_log.log"
        cls._log_file_name_no_debug = "test_log_no_debug.log"
        cls._log_file_name_last = "test_last.log"
        cls._log_file_name_last_no_debug = "test_last_no_debug.log"

    @classmethod
    def get_log_file(cls):
        return cls.LOG_DIR / cls._log_file_name

    @classmethod
    def get_log_file_no_debug(cls):
        return cls.LOG_DIR / cls._log_file_name_no_debug

    @classmethod
    def get_log_file_last(cls):
        return cls.LOG_DIR / cls._log_file_name_last

    @classmethod
    def get_log_file_last_no_debug(cls):
        return cls.LOG_DIR / cls._log_file_name_last_no_debug
