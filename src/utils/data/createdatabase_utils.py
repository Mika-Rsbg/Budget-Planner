from pathlib import Path
import sqlite3
import config


def create_database(path: Path = None) -> None:
    # Database location
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    db_location = base_dir / 'data' / 'database.db'
    db_location = config.Database.PATH if path is None else path
    # Create the directory if it doesn't exist
    db_location.parent.mkdir(parents=True, exist_ok=True)
    # Connect to the database
    conn = sqlite3.connect(db_location)
    cursor = conn.cursor()

    def create_transactions_table():
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tbl_Transaction (
            i8_TransactionID INTEGER PRIMARY KEY AUTOINCREMENT,
            i8_UserID INTEGER DEFAULT 1,
            i8_AccountID INTEGER NOT NULL,
            i8_Date INTEGER NOT NULL,   -- (YYMMDD)
            i8_AmountType INTEGER CHECK(i8_AmountType IN (0, 1)) NOT NULL,
                       -- Art des Betrags (+(1) oder -(0))
            real_Amount REAL NOT NULL,
            str_Purpose TEXT NOT NULL,
            i8_CounterpartyID INTEGER,
            i8_CategoryID INTEGER DEFAULT 1,
            str_UserComments TEXT,
            str_DisplayedName TEXT,
            FOREIGN KEY (i8_CategoryID) REFERENCES Category_tbl(i8_CategoryID),
                    -- Verknüpfung zur Kategorie
            FOREIGN KEY (i8_CounterpartyID) REFERENCES
           Counterparty_tbl(i8_CounterpartyID)
           -- Verknüpfung zu Counterparty_tbl
            FOREIGN KEY (i8_AccountID) REFERENCES Account_tbl(i8_AccountID)
            );
        ''')
        conn.commit()

    def create_category_table(cursor, conn):
        create_budget_period_table(cursor, conn)

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

        insert_initial_categories(cursor, conn)

    def create_budget_period_table(cursor, conn):
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS tbl_BudgetPeriod (
                i8_BudgetPeriodID INTEGER PRIMARY KEY,
                str_Name TEXT UNIQUE
            );
            '''
        )
        conn.commit()

        insert_initial_budget_periods(cursor, conn)

    def insert_initial_budget_periods(cursor, conn):
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

    def insert_initial_categories(cursor, conn):
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

    def create_counterparty_table():
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tbl_Counterparty (
            i8_CounterpartyID INTEGER PRIMARY KEY AUTOINCREMENT,
            str_CounterpartyName TEXT NOT NULL,
            i8_UserID INTEGER DEFAULT 1
            );
        ''')
        conn.commit()

    def create_account_table(cursor, conn):
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

    create_category_table(cursor, conn)
    # create_counterparty_table()
    create_account_table(cursor, conn)
    # create_transactions_table()

    print(f'Datenbank wurde erstellt unter: {db_location}')
    cursor.close()
    conn.close()


if __name__ == '__main__':
    create_database(Path(__file__).resolve().parent.parent.parent.parent
                    / 'data' / 'database.db')
