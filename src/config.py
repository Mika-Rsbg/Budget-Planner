from pathlib import Path


class Database:
    PATH = Path(__file__).resolve().parent.parent / 'data' / 'database.db'


class Logging:
    LOG_DIR = Path(__file__).resolve().parent.parent / 'log'
    LOG_FILE = LOG_DIR / 'app.log'
    LOG_FILE_NO_DEBUG = LOG_DIR / 'app_no_debug.log'

    @staticmethod
    def ensure_log_directory_exists():
        Logging.LOG_DIR.mkdir(parents=True, exist_ok=True)
