from pathlib import Path


class Database:
    PATH = Path(__file__).resolve().parent.parent / 'data' / 'database.db'
