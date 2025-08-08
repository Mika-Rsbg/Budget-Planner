from pathlib import Path


class Database:
    PATH = Path(__file__).resolve().parent.parent / 'data' / 'database.db'


class Logging:
    LOG_DIR = Path(__file__).resolve().parent.parent / 'log'
    log_file_name = 'app.log'
    log_file_name_no_debug = 'app_no_debug.log'
    LOG_FILE = LOG_DIR / log_file_name
    LOG_FILE_NO_DEBUG = LOG_DIR / log_file_name_no_debug

    @staticmethod
    def ensure_log_directory_exists():
        Logging.LOG_DIR.mkdir(parents=True, exist_ok=True)
