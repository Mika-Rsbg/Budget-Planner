import sqlite3
from pathlib import Path


def get_accounts(db_location: Path,
                 selected_columns: list[bool] = [True, True, True, True, True]
                 ) -> list[tuple]:
    """
    Retrieves account data from the database.
    Args:
        db_location (Path): Path to the SQLite database file.
        selected_columns (list[bool]): List of booleans indicating which
                                       columns to select.
                                       [AccountID, AccountName, AccountNumber,
                                       AccountBalance, AccountDifference]
    Return:
        List of tuples containing account data (AccountID, AccountName).
    """
    conn = sqlite3.connect(db_location)
    cursor = conn.cursor()
    columns = ["i8_AccountID", "str_AccountName", "str_AccountNumber",
               "real_AccountBalance", "real_AccountDifference"]
    query = 'SELECT '
    for i, col in enumerate(columns):
        if selected_columns[i]:
            query += f'{col}, '
    query = query[:-2] + ' FROM tbl_Account'

    cursor.execute(query)
    account_data = cursor.fetchall()
    conn.close()
    return account_data


# Pfad zum aktuellen Skript
current_path = Path(__file__).resolve()

# Elternverzeichnis (übergeordneter Ordner von "src")
parent_directory = current_path.parent.parent.parent.parent

# Ordner, der sich auf derselben Ebene wie "src" befindet
sibling_folder = parent_directory / "data"

# Datei innerhalb des Zielordners
file_path = sibling_folder / "database.db"

print(get_accounts(file_path, [True, True, True, True, True]))
