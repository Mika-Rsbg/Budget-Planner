import sqlite3


def create_database():
    # Database location
    db_location = 'src/data/database.db'
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

    def create_category_table():
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tbl_Category (
            i8_CategoryID INTEGER PRIMARY KEY AUTOINCREMENT,
            str_CategoryName TEXT NOT NULL,
            i8_UserID INTEGER DEFAULT 1
            );
        ''')
        cursor.execute('''
            INSERT INTO tbl_Category (str_CategoryName)
            SELECT 'Sonstiges'
            WHERE NOT EXISTS (SELECT 1 FROM tbl_Category);
        ''')
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

    def create_account_table():
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tbl_Account (
            i8_AccountID INTEGER PRIMARY KEY AUTOINCREMENT,
            str_AccountName TEXT NOT NULL,
            str_AccountNumber TEXT NOT NULL,
            i8_UserID INTEGER DEFAULT 1
            );
        ''')
        conn.commit()

    create_category_table()
    create_counterparty_table()
    create_account_table()
    create_transactions_table()


if __name__ == '__main__':
    create_database()
