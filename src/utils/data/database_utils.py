import sqlite3
from pathlib import Path
import config


def get_account_data(db_location: Path = config.Database.PATH,
                     selected_columns: list[bool] = [True, True, True,
                                                     True, True]
                     ) -> list[tuple]:
    """
    Retrieves account data from the database.
    Args:
        db_location (Path): Path to the SQLite database file. Def
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


if __name__ == '__main__':
    print(get_account_data(config.Database.PATH, [False, True, False,
                                                  False, False]))
