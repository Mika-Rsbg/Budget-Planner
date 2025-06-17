from pathlib import Path
import sqlite3
import logging
from utils.logging.logging_tools import logg
from utils.data.database_connection import DatabaseConnection
import config

logger = logging.getLogger(__name__)


class Error(Exception):
    """General exception class for database errors."""
    pass


@logg
def create_database(db_path: Path = config.Database.PATH) -> None:
    def create_transactions_table(cursor, conn) -> None:
        """
        Create the transactions table in the database.
        """
        logger.debug("Creating transactions table...")
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
            logger.debug("Transactions table created successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error creating transactions table: {e}")

    def create_category_table(cursor, conn) -> None:
        """
        Create the category table in the database.
        """
        logger.debug("Creating category table...")
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
            logger.debug("Category table created successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error creating category table: {e}")
        insert_initial_categories(cursor, conn)

    def create_budget_period_table(cursor, conn) -> None:
        """
        Create the budget period table in the database.
        """
        logger.debug("Creating budget period table...")
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
            logger.debug("Budget period table created successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error creating budget period table: {e}")
        insert_initial_budget_periods(cursor, conn)

    def insert_initial_budget_periods(cursor, conn) -> None:
        """
        Insert initial budget periods into the database.
        """
        logger.debug("Inserting initial budget periods...")
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
            logger.debug("Initial budget periods inserted successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error inserting initial budget periods: {e}")

    def insert_initial_categories(cursor, conn) -> None:
        """
        Insert initial categories into the database.
        """
        logger.debug("Inserting initial categories...")
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
            logger.debug("Initial categories inserted successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error inserting initial categories: {e}")

    def create_counterparty_table(cursor, conn) -> None:
        """
        Create the counterparty table in the database.
        """
        logger.debug("Creating counterparty table...")
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
            logger.debug("Counterparty table created successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error creating counterparty table: {e}")

    def create_transaction_typ_table(cursor, conn) -> None:
        """
        Create the transaction type table in the database.
        """
        logger.debug("Creating transaction type table...")
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
            logger.debug("Transaction type table created successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error creating transaction type table: {e}")

    def create_account_table(cursor, conn) -> None:
        """
        Create the account table in the database.
        """
        logger.debug("Creating account table...")
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
            logger.debug("Account table created successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error creating account table: {e}")

    def create_account_history_table(cursor, conn) -> None:
        """
        Create the account history table in the database.
        """
        logger.debug("Creating account history table...")
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
            logger.debug("Account history table created successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error creating account history table: {e}")

    def create_indexes_for_transaction_table(cursor) -> None:
        """
        Create indexes for the transaction table.
        """
        logger.debug("Creating indexes for transaction table...")
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
        logger.debug("Indexes for transaction table created successfully.")

    def create_indexes_for_account_table(cursor) -> None:
        """
        Create indexes for the account table.
        """
        logger.debug("Creating indexes for account table...")
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_account_widget_position
            ON tbl_Account(i8_WidgetPosition);
        ''')
        logger.debug("Indexes for account table created successfully.")

    def create_indexes_for_account_history_table(cursor) -> None:
        """
        Create indexes for the account history table.
        """
        logger.debug("Creating indexes for account history table...")
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_accounthistory_account
            ON tbl_AccountHistory(i8_AccountID);
        ''')
        logger.debug("Indexes for account history table created successfully.")

    def create_indexes_for_category_table(cursor) -> None:
        """
        Create indexes for the category table.
        """
        logger.debug("Creating indexes for category table...")
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_category_budgetperiod
            ON tbl_Category(i8_BudgetPeriodID);
        ''')
        logger.debug("Indexes for category table created successfully.")

    def create_all_indexes(cursor, conn) -> None:
        """
        Create all indexes in the database.
        """
        logger.debug("Creating all indexes...")
        create_indexes_for_transaction_table(cursor)
        create_indexes_for_account_table(cursor)
        create_indexes_for_account_history_table(cursor)
        create_indexes_for_category_table(cursor)
        conn.commit()
        logger.debug("All indexes created successfully.")

    try:
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

        logger.info('Tables created successfully.')

        # Indizes erstellen
        create_all_indexes(cursor, conn)
        logger.info("Indexes were created successfully.")
        logger.info(f"Database created successfully: {db_path}")
    except sqlite3.Error as e:
        logger.error(f"Database couldn't be created: {e}")
    finally:
        DatabaseConnection.close_cursor()


@logg
def delete_database(db_path: Path = config.Database.PATH) -> None:
    """
    Delete the database file.

    Args:
        path (Path): Path to the database file.

    Raises:
        FileNotFoundError: If the database file does not exist.
        Exception: If there is an error deleting the database file.
    """
    try:
        DatabaseConnection.close_connection()
        db_path.unlink()
        logger.info(f'Database deleted: {db_path}')
        # print(f'Datenbank wurde gelöscht: {db_path}')
    except FileNotFoundError:
        logger.error(f"Database not found: {db_path}")
        raise Error(f'Database not found: {db_path}')
    except Exception as e:
        logger.error(f"Database couldn't be deleted: {e}")
        raise Error(f"Database couldn't be deleted: {e}")
