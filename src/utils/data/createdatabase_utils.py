from pathlib import Path
import sqlite3
from utils.data.database_connection import DatabaseConnection
import config


class Error(Exception):
    """General exception class for database errors."""
    pass


def create_database(db_path: Path = None) -> None:
    def create_transactions_table(cursor, conn) -> None:
        try:
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS tbl_Transaction (
                    i8_TransactionID INTEGER PRIMARY KEY AUTOINCREMENT,
                    i8_AccountID INTEGER NOT NULL,
                    str_Date TEXT NOT NULL,  -- Format: YYYY-MM-DD
                    str_Bookingdate TEXT NOT NULL,  -- Format: YYYY-MM-DD
                    i8_TransactionTypeID INTEGER,
                    real_Amount REAL NOT NULL,
                    str_Purpose TEXT NOT NULL,
                    i8_CounterpartyID INTEGER,
                    i8_CategoryID INTEGER DEFAULT 1,
                    str_UserComments TEXT,
                    str_DisplayedName TEXT,
                    FOREIGN KEY (i8_CategoryID)
                        REFERENCES tbl_Category(i8_CategoryID)
                        ON DELETE SET DEFAULT,
                    FOREIGN KEY (i8_CounterpartyID)
                        REFERENCES tbl_Counterparty(i8_CounterpartyID)
                        ON DELETE SET NULL,
                    FOREIGN KEY (i8_AccountID)
                        REFERENCES tbl_Account(i8_AccountID)
                        ON DELETE CASCADE,
                    FOREIGN KEY (i8_TransactionTypeID)
                        REFERENCES tbl_TransactionType(i8_TransactionTypeID)
                        ON DELETE SET NULL
                );
                '''
            )
            conn.commit()
        except sqlite3.Error as e:
            print("[Fehler] Tabelle 'tbl_Transaction' konnte"
                  f"nicht erstellt werden: {e}")

    def create_category_table(cursor, conn) -> None:
        create_budget_period_table(cursor, conn)
        try:
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS tbl_Category (
                    i8_CategoryID INTEGER PRIMARY KEY AUTOINCREMENT,
                    str_CategoryName TEXT UNIQUE NOT NULL,
                    real_Budget REAL DEFAULT 0.0,
                    i8_BudgetPeriodID INTEGER DEFAULT 3,
                    FOREIGN KEY (i8_BudgetPeriodID)
                        REFERENCES tbl_BudgetPeriod(i8_BudgetPeriodID)
                );
                '''
            )
            conn.commit()
        except sqlite3.Error as e:
            print("[Fehler] Tabelle 'tbl_Category' konnte"
                  f"nicht erstellt werden: {e}")
        insert_initial_categories(cursor, conn)

    def create_budget_period_table(cursor, conn) -> None:
        try:
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS tbl_BudgetPeriod (
                    i8_BudgetPeriodID INTEGER PRIMARY KEY,
                    str_Name TEXT UNIQUE
                );
                '''
            )
            conn.commit()
        except sqlite3.Error as e:
            print("[Fehler] Tabelle 'tbl_BudgetPeriod' konnte"
                  f"nicht erstellt werden: {e}")
        insert_initial_budget_periods(cursor, conn)

    def insert_initial_budget_periods(cursor, conn) -> None:
        try:
            cursor.executemany(
                '''
                INSERT OR IGNORE INTO tbl_BudgetPeriod
                (i8_BudgetPeriodID, str_Name)
                VALUES (?, ?)
                ''',
                [
                    (1, 'daily'),
                    (2, 'weekly'),
                    (3, 'monthly'),
                    (4, 'yearly')
                ]
            )
            conn.commit()
        except sqlite3.Error as e:
            print("[Fehler] Budgetperioden konnten nicht"
                  f"erstellt werden: {e}")

    def insert_initial_categories(cursor, conn) -> None:
        try:
            cursor.executemany(
                '''
                INSERT OR IGNORE INTO tbl_Category
                (str_CategoryName, real_Budget, i8_BudgetPeriodID)
                VALUES (?, ?, ?)
                ''',
                [
                    ('Sonstiges', 0.0, 3),
                    ('Spareinlagen', 100.0, 3)
                ]
            )
            conn.commit()
        except sqlite3.Error as e:
            print("[Fehler] Initialkategorien konnten nicht"
                  f"erstellt werden: {e}")

    def create_counterparty_table(cursor, conn) -> None:
        try:
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS tbl_Counterparty (
                    i8_CounterpartyID INTEGER PRIMARY KEY AUTOINCREMENT,
                    str_CounterpartyName TEXT UNIQUE NOT NULL,
                    str_CounterpartyNumber TEXT UNIQUE NOT NULL
                );
                '''
            )
            conn.commit()
        except sqlite3.Error as e:
            print("[Fehler] Tabelle 'tbl_Counterparty' konnte"
                  f"nicht erstellt werden: {e}")

    def create_transaction_typ_table(cursor, conn) -> None:
        try:
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS tbl_TransactionTyp (
                    i8_TransactionTypID INTEGER PRIMARY KEY AUTOINCREMENT,
                    str_TransactionTypName TEXT NOT NULL,
                    str_TransactionTypNumber TEXT NOT NULL
                );
                '''
            )
            conn.commit()
        except sqlite3.Error as e:
            print("[Fehler] Tabelle 'tbl_TransactionTyp' konnte"
                  f"nicht erstellt werden: {e}")

    def create_account_table(cursor, conn) -> None:
        try:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS tbl_Account (
                i8_AccountID INTEGER PRIMARY KEY AUTOINCREMENT,
                i8_WidgetPosition INTEGER UNIQUE NOT NULL,
                str_AccountName TEXT UNIQUE NOT NULL,
                str_AccountNumber TEXT UNIQUE NOT NULL,
                real_AccountBalance REAL DEFAULT 0.0,
                real_AccountDifference REAL DEFAULT 0.0,
                str_RecordDate INTEGER,
                str_ChangeDate INTEGER
                );
            ''')
            conn.commit()
            add_cash_account(cursor, conn)
        except sqlite3.Error as e:
            print("[Fehler] Tabelle 'tbl_Account' konnte"
                  f"nicht erstellt werden: {e}")

    def add_cash_account(cursor, conn):
        if config.Database.CASH_ENABLED or True:
            try:
                cursor.execute(
                    '''
                    INSERT OR IGNORE INTO tbl_Account
                    (str_AccountName, str_AccountNumber, real_AccountBalance,
                    real_AccountDifference, str_RecordDate, str_ChangeDate)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''',
                    ('Cash', '-', 0.0, 0.0, 0, 0)
                )
                conn.commit()
            except sqlite3.Error as e:
                print("[Fehler] Bargeldkonto konnte nicht"
                      f"erstellt werden: {e}")
        else:
            print("[Info] Bargeldkonto ist deaktiviert.")

    def create_account_history_table(cursor, conn):
        try:
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS tbl_AccountHistory (
                    i8_AccountHistoryID INTEGER PRIMARY KEY AUTOINCREMENT,
                    i8_AccountID INTEGER NOT NULL,
                    real_Balance REAL,
                    str_RecordDate TEXT NOT NULL,
                    str_ChangeDate TEXT NOT NULL,
                    FOREIGN KEY (i8_AccountID)
                        REFERENCES tbl_Account(i8_AccountID)
                        ON DELETE CASCADE
                );
                '''
            )
            conn.commit()
        except sqlite3.Error as e:
            print("[Fehler] Tabelle 'tbl_AccountHistory' konnte nicht"
                  "erstellt werden:", e)

    def create_indexes_for_transaction_table(cursor) -> None:
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_transaction_account_date
            ON tbl_Transaction(i8_AccountID, str_Date);
        ''')
        # cursor.execute('''
        #     CREATE INDEX IF NOT EXISTS idx_transaction_bookingdate
        #     ON tbl_Transaction(str_Bookingdate);
        # ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_transaction_category
            ON tbl_Transaction(i8_AccountID, i8_CategoryID, str_Date);
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_transaction_counterparty_date
            ON tbl_Transaction(i8_CounterpartyID, str_Date);
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS
                idx_transaction_account_counterparty_date
            ON tbl_Transaction(i8_AccountID, i8_CounterpartyID, str_Date);
        ''')

    def create_indexes_for_account_table(cursor) -> None:
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_account_widget_position
            ON tbl_Account(i8_WidgetPosition);
        ''')

    def create_indexes_for_account_history_table(cursor) -> None:
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_accounthistory_account
            ON tbl_AccountHistory(i8_AccountID);
        ''')

    def create_indexes_for_category_table(cursor) -> None:
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_category_budgetperiod
            ON tbl_Category(i8_BudgetPeriodID);
        ''')

    def create_all_indexes(cursor, conn) -> None:
        create_indexes_for_transaction_table(cursor)
        create_indexes_for_account_table(cursor)
        create_indexes_for_account_history_table(cursor)
        create_indexes_for_category_table(cursor)
        conn.commit()

    try:
        db_path = db_path if db_path else config.Database.PATH
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = DatabaseConnection.get_connection(db_path)
        cursor = DatabaseConnection.get_cursor(db_path)

        # Tabellen erstellen
        create_category_table(cursor, conn)
        create_counterparty_table(cursor, conn)
        create_account_table(cursor, conn)
        create_account_history_table(cursor, conn)
        create_transaction_typ_table(cursor, conn)
        create_transactions_table(cursor, conn)

        print(f'Database created successfully: {db_path}')

        # Indizes erstellen
        create_all_indexes(cursor, conn)
        print("Indexes were created successfully.")
    except sqlite3.Error as e:
        print(f"[Fehler] Datenbankverbindung fehlgeschlagen: {e}")
    finally:
        DatabaseConnection.close_cursor()


def delete_database(path: Path = None) -> None:
    """
    Delete the database file.

    Args:
        path (Path): Path to the database file.

    Raises:
        FileNotFoundError: If the database file does not exist.
        Exception: If there is an error deleting the database file.
    """
    db_path = path if path else config.Database.PATH
    try:
        DatabaseConnection.close_connection()
        db_path.unlink()
        print(f'Datenbank wurde gelöscht: {db_path}')
    except FileNotFoundError:
        raise Error(f'Datenbank nicht gefunden: {db_path}')
    except Exception as e:
        raise Error(f"[Fehler] Datenbank konnte nicht gelöscht werden: {e}")
