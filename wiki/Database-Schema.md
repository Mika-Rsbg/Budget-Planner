# Database Schema

This document provides comprehensive documentation of the Budget Planner's SQLite database schema, including table structures, relationships, and design decisions.

## 🗃️ Database Overview

The Budget Planner uses **SQLite** as its database engine with a well-structured relational schema that supports:

- **Financial Accounts** with balance tracking
- **Transactions** with categorization and counterparty information  
- **Categories** with budget periods and spending limits
- **Historical Data** for tracking changes over time
- **Foreign Key Constraints** for data integrity

**Database Location**: `data/database.db` (relative to project root)

## 📊 Entity Relationship Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   tbl_Account   │    │ tbl_Transaction │    │  tbl_Category   │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ i8_AccountID(PK)│◄──┐│ i8_TransactionID│    │ i8_CategoryID   │
│ str_AccountName │   ││   (PK)          │    │   (PK)          │
│ real_Balance    │   │├─────────────────┤    │ str_CategoryName│
│ ...             │   ││ i8_AccountID(FK)│◄───┤ real_Budget     │
└─────────────────┘   │├─────────────────┤ ┌─►│ i8_BudgetPeriod │
                      ││ i8_CategoryID   │─┘  │   ID(FK)        │
┌─────────────────┐   ││   (FK)          │    └─────────────────┘
│tbl_AccountHistory│   │├─────────────────┤           ▲
├─────────────────┤   ││ i8_CounterpartyID│           │
│ i8_AccountID(FK)│◄──┤│   (FK)          │    ┌──────┴──────┐
│ real_Balance    │   │└─────────────────┘    │tbl_BudgetPeriod│
│ str_RecordDate  │   │         │             ├─────────────┤
└─────────────────┘   │         ▼             │ i8_BudgetPer│
                      │┌─────────────────┐    │   iodID(PK) │
┌─────────────────┐   ││tbl_Counterparty │    │ str_Name    │
│tbl_TransactionTyp│   │├─────────────────┤    └─────────────┘
├─────────────────┤   ││ i8_CounterpartyID│
│ i8_TransactionTy│◄──┤│   (PK)          │
│   pID(PK)       │   ││ str_Counterparty│
│ str_Name        │   ││   Name          │
└─────────────────┘   │└─────────────────┘
                      │
                      └─ Foreign Key Relationship
```

## 📋 Table Structures

### 1. tbl_Account

**Purpose**: Store financial account information and current balances

```sql
CREATE TABLE tbl_Account (
    i8_AccountID INTEGER PRIMARY KEY AUTOINCREMENT,
    i8_WidgetPosition INTEGER UNIQUE NOT NULL,
    str_AccountName TEXT UNIQUE NOT NULL,
    str_AccountNumber TEXT UNIQUE NOT NULL,
    real_AccountBalance REAL DEFAULT 0.0,
    real_AccountDifference REAL DEFAULT 0.0,
    str_RecordDate INTEGER,
    str_ChangeDate INTEGER
);
```

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `i8_AccountID` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique account identifier |
| `i8_WidgetPosition` | INTEGER | UNIQUE, NOT NULL | Position in GUI display (1,2,3...) |
| `str_AccountName` | TEXT | UNIQUE, NOT NULL | Display name for account |
| `str_AccountNumber` | TEXT | UNIQUE, NOT NULL | Bank account number/identifier |
| `real_AccountBalance` | REAL | DEFAULT 0.0 | Current account balance |
| `real_AccountDifference` | REAL | DEFAULT 0.0 | Change from previous period |
| `str_RecordDate` | INTEGER | | Date of balance record |
| `str_ChangeDate` | INTEGER | | Date of last modification |

**Design Notes:**
- `WidgetPosition` controls display order in the GUI
- Account names and numbers must be unique
- Balance difference tracks changes for quick overview
- Date fields store as integers (YYYYMMDD format)

### 2. tbl_Transaction

**Purpose**: Store all financial transactions with categorization

```sql
CREATE TABLE tbl_Transaction (
    i8_TransactionID INTEGER PRIMARY KEY AUTOINCREMENT,
    i8_AccountID INTEGER NOT NULL,
    str_Date TEXT NOT NULL,
    str_Bookingdate TEXT NOT NULL,
    i8_TransactionTypeID INTEGER,
    real_Amount REAL NOT NULL,
    str_Purpose TEXT NOT NULL,
    i8_CounterpartyID INTEGER,
    i8_CategoryID INTEGER DEFAULT 1,
    str_UserComments TEXT,
    str_DisplayedName TEXT,
    FOREIGN KEY (i8_CategoryID) REFERENCES tbl_Category(i8_CategoryID) ON DELETE SET DEFAULT,
    FOREIGN KEY (i8_CounterpartyID) REFERENCES tbl_Counterparty(i8_CounterpartyID) ON DELETE SET NULL,
    FOREIGN KEY (i8_AccountID) REFERENCES tbl_Account(i8_AccountID) ON DELETE CASCADE,
    FOREIGN KEY (i8_TransactionTypeID) REFERENCES tbl_TransactionTyp(i8_TransactionTypID) ON DELETE SET NULL
);
```

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `i8_TransactionID` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique transaction identifier |
| `i8_AccountID` | INTEGER | NOT NULL, FK → tbl_Account | Account this transaction belongs to |
| `str_Date` | TEXT | NOT NULL | Transaction date (YYYY-MM-DD) |
| `str_Bookingdate` | TEXT | NOT NULL | Bank booking date (YYYY-MM-DD) |
| `i8_TransactionTypeID` | INTEGER | FK → tbl_TransactionTyp | Type of transaction |
| `real_Amount` | REAL | NOT NULL | Transaction amount (+ credit, - debit) |
| `str_Purpose` | TEXT | NOT NULL | Transaction description/purpose |
| `i8_CounterpartyID` | INTEGER | FK → tbl_Counterparty | Who the transaction is with |
| `i8_CategoryID` | INTEGER | DEFAULT 1, FK → tbl_Category | Budget category |
| `str_UserComments` | TEXT | | User-added comments |
| `str_DisplayedName` | TEXT | | Custom display name override |

**Foreign Key Behaviors:**
- **Account deletion**: CASCADE (delete all transactions)
- **Category deletion**: SET DEFAULT (use default category)
- **Counterparty deletion**: SET NULL (clear counterparty)
- **Transaction type deletion**: SET NULL (clear type)

### 3. tbl_Category

**Purpose**: Budget categories with spending limits and periods

```sql
CREATE TABLE tbl_Category (
    i8_CategoryID INTEGER PRIMARY KEY AUTOINCREMENT,
    str_CategoryName TEXT UNIQUE NOT NULL,
    real_Budget REAL DEFAULT 0.0,
    i8_BudgetPeriodID INTEGER DEFAULT 3,
    FOREIGN KEY (i8_BudgetPeriodID) REFERENCES tbl_BudgetPeriod(i8_BudgetPeriodID)
);
```

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `i8_CategoryID` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique category identifier |
| `str_CategoryName` | TEXT | UNIQUE, NOT NULL | Category display name |
| `real_Budget` | REAL | DEFAULT 0.0 | Budget amount for this category |
| `i8_BudgetPeriodID` | INTEGER | DEFAULT 3, FK → tbl_BudgetPeriod | Budget period (monthly default) |

**Initial Categories:**
- `Sonstiges` (ID: 1) - Default/miscellaneous category
- `Spareinlagen` (ID: 2) - Savings deposits

### 4. tbl_BudgetPeriod

**Purpose**: Define budget period types (daily, weekly, monthly, yearly)

```sql
CREATE TABLE tbl_BudgetPeriod (
    i8_BudgetPeriodID INTEGER PRIMARY KEY,
    str_Name TEXT UNIQUE
);
```

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `i8_BudgetPeriodID` | INTEGER | PRIMARY KEY | Period identifier |
| `str_Name` | TEXT | UNIQUE | Period name |

**Standard Periods:**
- `1` - daily
- `2` - weekly  
- `3` - monthly (default)
- `4` - yearly

### 5. tbl_Counterparty

**Purpose**: Store information about transaction counterparties (payees/payers)

```sql
CREATE TABLE tbl_Counterparty (
    i8_CounterpartyID INTEGER PRIMARY KEY AUTOINCREMENT,
    str_CounterpartyName TEXT UNIQUE NOT NULL,
    str_CounterpartyNumber TEXT UNIQUE NOT NULL
);
```

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `i8_CounterpartyID` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique counterparty identifier |
| `str_CounterpartyName` | TEXT | UNIQUE, NOT NULL | Counterparty display name |
| `str_CounterpartyNumber` | TEXT | UNIQUE, NOT NULL | Counterparty number/ID |

### 6. tbl_TransactionTyp

**Purpose**: Categorize transaction types (manual, import, etc.)

```sql
CREATE TABLE tbl_TransactionTyp (
    i8_TransactionTypID INTEGER PRIMARY KEY AUTOINCREMENT,
    str_TransactionTypName TEXT NOT NULL,
    str_TransactionTypNumber TEXT NOT NULL
);
```

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `i8_TransactionTypID` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique type identifier |
| `str_TransactionTypName` | TEXT | NOT NULL | Type display name |
| `str_TransactionTypNumber` | TEXT | NOT NULL | Type number/code |

**Initial Transaction Types:**
- `Manuelle Transaktion` (Code: 1000) - Manual transactions

### 7. tbl_AccountHistory

**Purpose**: Track account balance changes over time

```sql
CREATE TABLE tbl_AccountHistory (
    i8_AccountHistoryID INTEGER PRIMARY KEY AUTOINCREMENT,
    i8_AccountID INTEGER NOT NULL,
    real_Balance REAL,
    str_RecordDate TEXT NOT NULL,
    str_ChangeDate TEXT NOT NULL,
    FOREIGN KEY (i8_AccountID) REFERENCES tbl_Account(i8_AccountID) ON DELETE CASCADE
);
```

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `i8_AccountHistoryID` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique history record identifier |
| `i8_AccountID` | INTEGER | NOT NULL, FK → tbl_Account | Account this history belongs to |
| `real_Balance` | REAL | | Account balance at this point in time |
| `str_RecordDate` | TEXT | NOT NULL | Date this balance was recorded |
| `str_ChangeDate` | TEXT | NOT NULL | Date this record was created |

**Purpose**: Enables balance history tracking and trend analysis

## 🔗 Relationship Details

### Foreign Key Relationships

#### Account → Transactions (One-to-Many)
```sql
tbl_Transaction.i8_AccountID → tbl_Account.i8_AccountID
ON DELETE CASCADE
```
- **Behavior**: Deleting an account removes all its transactions
- **Rationale**: Transactions cannot exist without their parent account

#### Category → Transactions (One-to-Many)
```sql
tbl_Transaction.i8_CategoryID → tbl_Category.i8_CategoryID  
ON DELETE SET DEFAULT
```
- **Behavior**: Deleting a category sets transactions to default category (ID: 1)
- **Rationale**: Preserves transaction history even if categories are reorganized

#### Counterparty → Transactions (One-to-Many)
```sql
tbl_Transaction.i8_CounterpartyID → tbl_Counterparty.i8_CounterpartyID
ON DELETE SET NULL
```
- **Behavior**: Deleting a counterparty clears the counterparty field
- **Rationale**: Transaction remains valid without counterparty information

#### BudgetPeriod → Categories (One-to-Many)
```sql
tbl_Category.i8_BudgetPeriodID → tbl_BudgetPeriod.i8_BudgetPeriodID
```
- **Behavior**: Categories reference standard budget periods
- **Rationale**: Standardizes budget period types across the application

## 📊 Data Access Patterns

### Common Queries

#### Get Account Summary with Balance
```sql
SELECT 
    a.str_AccountName,
    a.real_AccountBalance,
    a.real_AccountDifference,
    COUNT(t.i8_TransactionID) as transaction_count
FROM tbl_Account a
LEFT JOIN tbl_Transaction t ON a.i8_AccountID = t.i8_AccountID
GROUP BY a.i8_AccountID
ORDER BY a.i8_WidgetPosition;
```

#### Get Transactions with Category and Counterparty
```sql
SELECT 
    t.str_Date,
    t.real_Amount,
    t.str_Purpose,
    c.str_CategoryName,
    cp.str_CounterpartyName,
    a.str_AccountName
FROM tbl_Transaction t
LEFT JOIN tbl_Category c ON t.i8_CategoryID = c.i8_CategoryID
LEFT JOIN tbl_Counterparty cp ON t.i8_CounterpartyID = cp.i8_CounterpartyID
LEFT JOIN tbl_Account a ON t.i8_AccountID = a.i8_AccountID
ORDER BY t.str_Date DESC;
```

#### Budget Analysis by Category
```sql
SELECT 
    c.str_CategoryName,
    c.real_Budget,
    bp.str_Name as budget_period,
    SUM(t.real_Amount) as spent,
    (c.real_Budget - SUM(t.real_Amount)) as remaining
FROM tbl_Category c
LEFT JOIN tbl_BudgetPeriod bp ON c.i8_BudgetPeriodID = bp.i8_BudgetPeriodID
LEFT JOIN tbl_Transaction t ON c.i8_CategoryID = t.i8_CategoryID
GROUP BY c.i8_CategoryID;
```

## 🛠️ Database Utilities

### Utility Module Organization

Database operations are organized by domain in `src/utils/data/database/`:

- **`account_utils.py`** - Account CRUD operations
- **`transaction_utils.py`** - Transaction management  
- **`category_utils.py`** - Category operations
- **`counterparty_utils.py`** - Counterparty management
- **`account_history_utils.py`** - Historical balance tracking

### Example Utility Functions

#### Account Operations
```python
def get_account_data(selected_columns: List[bool] = None) -> List[Tuple]:
    """Get account data with column selection"""
    
def add_account(name: str, number: str) -> bool:
    """Add new account with validation"""
    
def update_account_balance(account_id: int, new_balance: float) -> bool:
    """Update account balance and create history record"""
```

#### Transaction Operations
```python
def add_transaction(account_id: int, amount: float, purpose: str, 
                   category_id: int = 1) -> bool:
    """Add new transaction with validation"""
    
def get_transactions_by_date_range(start_date: str, end_date: str) -> List[Tuple]:
    """Get transactions within date range"""
```

## 🔧 Database Management

### Schema Creation

The database schema is created automatically on first run by `create_database()` in `createdatabase_utils.py`:

```python
@log_fn
def create_database(db_path: Path = config.Database.PATH) -> None:
    """Create database schema with all tables and initial data"""
    conn = DatabaseConnection.get_connection(db_path)
    cursor = conn.cursor()
    
    # Create tables in dependency order
    create_budget_period_table(cursor, conn)
    create_category_table(cursor, conn)
    create_counterparty_table(cursor, conn)
    create_transaction_typ_table(cursor, conn)
    create_account_table(cursor, conn)
    create_transactions_table(cursor, conn)
    create_account_history_table(cursor, conn)
```

### Data Integrity

#### Constraints
- **UNIQUE constraints** prevent duplicate account names, numbers
- **NOT NULL constraints** ensure required fields are populated
- **FOREIGN KEY constraints** maintain referential integrity
- **DEFAULT values** provide sensible fallbacks

#### Validation
- Application-level validation in utility functions
- Parameterized queries prevent SQL injection
- Exception handling with custom exception classes

### Migration Strategy

For future schema changes:
1. **Version tracking** in database or config
2. **Migration scripts** for incremental updates  
3. **Backup creation** before migrations
4. **Rollback procedures** for failed migrations

## 📈 Performance Considerations

### Indexing Strategy
Currently relies on primary keys and unique constraints for indexing. Future considerations:
- Index on `tbl_Transaction.str_Date` for date range queries
- Index on `tbl_Transaction.i8_AccountID` for account-specific queries
- Composite index on `(i8_AccountID, str_Date)` for account history

### Query Optimization
- Use column selection to reduce data transfer
- Parameterized queries for prepared statement benefits
- LEFT JOINs to handle optional relationships properly

## 🔍 Debugging Database Issues

### Tools
- **DB Browser for SQLite** - Visual inspection and queries
- **Application logs** - Database operation timing and errors
- **SQL queries** - Direct database interaction for debugging

### Common Issues
- **Foreign key violations** - Check constraint definitions
- **Unique constraint violations** - Verify data uniqueness
- **Connection issues** - Check singleton connection management

---

*This schema provides a solid foundation for financial tracking while maintaining flexibility for future enhancements. The foreign key relationships ensure data integrity while the utility layer provides safe, consistent database access.*