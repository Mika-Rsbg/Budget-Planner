from pathlib import Path
import sqlite3
import config


def create_database(path: Path = None) -> None:
    def create_transactions_table(cursor, conn):
        try:
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS tbl_Transaction (
                    i8_TransactionID INTEGER PRIMARY KEY AUTOINCREMENT,
                    i8_AccountID INTEGER NOT NULL,
                    i8_Date INTEGER NOT NULL,  -- Format: YYMMDD
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
                        ON DELETE CASCADE
                );
                '''
            )
            conn.commit()
        except sqlite3.Error as e:
            print("[Fehler] Tabelle 'tbl_Transaction' konnte"
                  f"nicht erstellt werden: {e}")

    def create_category_table(cursor, conn):
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

    def create_budget_period_table(cursor, conn):
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

    def insert_initial_budget_periods(cursor, conn):
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

    def insert_initial_categories(cursor, conn):
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

    def create_counterparty_table(cursor, conn):
        try:
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS tbl_Counterparty (
                    i8_CounterpartyID INTEGER PRIMARY KEY AUTOINCREMENT,
                    str_CounterpartyName TEXT UNIQUE NOT NULL
                );
                '''
            )
            conn.commit()
        except sqlite3.Error as e:
            print("[Fehler] Tabelle 'tbl_Counterparty' konnte"
                  f"nicht erstellt werden: {e}")

    def create_account_table(cursor, conn):
        try:
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS tbl_Account (
                i8_AccountID INTEGER PRIMARY KEY AUTOINCREMENT,
                str_AccountName TEXT UNIQUE NOT NULL,
                str_AccountNumber TEXT,
                real_AccountBalance REAL DEFAULT 0.0,
                real_AccountDifference REAL DEFAULT 0.0
                );
            ''')
            conn.commit()
        except sqlite3.Error as e:
            print("[Fehler] Tabelle 'tbl_Account' konnte"
                  f"nicht erstellt werden: {e}")

    try:
        db_location = path if path else config.Database.PATH
        db_location.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_location)
        cursor = conn.cursor()

        # Tabellen erstellen
        create_category_table(cursor, conn)
        create_counterparty_table(cursor, conn)
        create_account_table(cursor, conn)
        create_transactions_table(cursor, conn)

        print(f'Datenbank wurde erstellt unter: {db_location}')

    except sqlite3.Error as e:
        print(f"[Fehler] Datenbankverbindung fehlgeschlagen: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


if __name__ == '__main__':
    create_database(Path(__file__).resolve().parent.parent.parent.parent
                    / 'data' / 'database.db')
