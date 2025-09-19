# Database Schema

This document provides a comprehensive overview of the Budget Planner's SQLite database schema, including table structures, relationships, and design rationale.

## 📊 Schema Overview

The Budget Planner uses a **normalized relational database design** with clear entity relationships and referential integrity constraints. The schema supports:

- **Multi-account management** with balance tracking
- **Transaction categorization** with flexible budget periods
- **Counterparty management** for transaction parties
- **Historical data tracking** for balance changes
- **Extensible transaction types** for different operation types

## 🗃️ Database Tables

### Core Entities

#### `tbl_Account` - Account Management

Stores information about user's financial accounts (bank accounts, cash, etc.).

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

**Field Descriptions**:
- `i8_AccountID`: Unique identifier for each account
- `i8_WidgetPosition`: Position of account widget on homepage (unique)
- `str_AccountName`: User-defined name for the account
- `str_AccountNumber`: Account number or identifier (e.g., IBAN)
- `real_AccountBalance`: Current account balance
- `real_AccountDifference`: Change from previous balance
- `str_RecordDate`: Date of record creation
- `str_ChangeDate`: Date of last balance update

**Design Decisions**:
- **Widget Position**: Enables consistent GUI layout across sessions
- **Balance Caching**: Stores calculated balance for performance
- **Difference Tracking**: Shows balance changes for user awareness

#### `tbl_Transaction` - Financial Transactions

Central table storing all financial transactions across accounts.

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

**Field Descriptions**:
- `i8_TransactionID`: Unique transaction identifier
- `i8_AccountID`: Reference to associated account (required)
- `str_Date`: Transaction date (YYYY-MM-DD format)
- `str_Bookingdate`: Bank booking date (YYYY-MM-DD format)
- `i8_TransactionTypeID`: Type of transaction (transfer, payment, etc.)
- `real_Amount`: Transaction amount (positive for credits, negative for debits)
- `str_Purpose`: Transaction description/purpose
- `i8_CounterpartyID`: Reference to transaction counterparty (optional)
- `i8_CategoryID`: Budget category assignment (defaults to "Other")
- `str_UserComments`: User-added notes or comments
- `str_DisplayedName`: Custom display name for transaction

**Foreign Key Behaviors**:
- **Account Deletion**: Cascade delete (removes all account transactions)
- **Category Deletion**: Set to default category (prevents orphaned transactions)
- **Counterparty Deletion**: Set to NULL (preserves transaction)
- **Transaction Type Deletion**: Set to NULL (preserves transaction)

#### `tbl_Category` - Budget Categories

Defines categories for transaction classification and budget management.

```sql
CREATE TABLE tbl_Category (
    i8_CategoryID INTEGER PRIMARY KEY AUTOINCREMENT,
    str_CategoryName TEXT UNIQUE NOT NULL,
    real_Budget REAL DEFAULT 0.0,
    i8_BudgetPeriodID INTEGER DEFAULT 3,
    FOREIGN KEY (i8_BudgetPeriodID) REFERENCES tbl_BudgetPeriod(i8_BudgetPeriodID)
);
```

**Field Descriptions**:
- `i8_CategoryID`: Unique category identifier
- `str_CategoryName`: Category name (must be unique)
- `real_Budget`: Budget amount for this category
- `i8_BudgetPeriodID`: Budget period (daily, weekly, monthly, yearly)

**Default Categories**:
- **Sonstiges** (Other): Default category for unclassified transactions
- **Spareinlagen** (Savings): For savings-related transactions

#### `tbl_Counterparty` - Transaction Counterparties

Stores information about entities involved in transactions (merchants, people, etc.).

```sql
CREATE TABLE tbl_Counterparty (
    i8_CounterpartyID INTEGER PRIMARY KEY AUTOINCREMENT,
    str_CounterpartyName TEXT UNIQUE NOT NULL,
    str_CounterpartyNumber TEXT UNIQUE NOT NULL
);
```

**Field Descriptions**:
- `i8_CounterpartyID`: Unique counterparty identifier
- `str_CounterpartyName`: Name of the counterparty
- `str_CounterpartyNumber`: Account number or identifier of counterparty

**Use Cases**:
- **Merchant Tracking**: Identify recurring transaction sources
- **Budget Analysis**: Analyze spending by counterparty
- **Report Generation**: Group transactions by business/person

### Supporting Tables

#### `tbl_BudgetPeriod` - Budget Time Periods

Defines the time periods for budget calculations.

```sql
CREATE TABLE tbl_BudgetPeriod (
    i8_BudgetPeriodID INTEGER PRIMARY KEY,
    str_Name TEXT UNIQUE
);
```

**Predefined Periods**:
- `1`: daily
- `2`: weekly  
- `3`: monthly (default)
- `4`: yearly

#### `tbl_TransactionTyp` - Transaction Types

Classifies transactions by their operational type.

```sql
CREATE TABLE tbl_TransactionTyp (
    i8_TransactionTypID INTEGER PRIMARY KEY AUTOINCREMENT,
    str_TransactionTypName TEXT NOT NULL,
    str_TransactionTypNumber TEXT NOT NULL
);
```

**Default Types**:
- **Manuelle Transaktion** (Manual Transaction): For user-entered transactions

#### `tbl_AccountHistory` - Balance History

Tracks historical balance changes for accounts.

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

**Purpose**:
- **Balance Tracking**: Maintains history of account balance changes
- **Audit Trail**: Provides accountability for balance modifications
- **Trend Analysis**: Enables historical balance trend visualization

## 🔗 Entity Relationships

### Primary Relationships

```
Account (1) ←→ (*) Transaction
    ↓
AccountHistory (*)

Transaction (*) ←→ (1) Category
Transaction (*) ←→ (1) Counterparty [optional]
Transaction (*) ←→ (1) TransactionTyp [optional]

Category (1) ←→ (1) BudgetPeriod
```

### Relationship Details

#### Account ↔ Transaction (One-to-Many)
- **Cardinality**: One account can have many transactions
- **Integrity**: Cascade delete ensures transaction cleanup when account is deleted
- **Business Rule**: Every transaction must belong to an account

#### Transaction ↔ Category (Many-to-One)
- **Cardinality**: Many transactions can share one category
- **Default Behavior**: Unassigned transactions default to "Other" category
- **Business Rule**: Category deletion doesn't delete transactions (sets to default)

#### Transaction ↔ Counterparty (Many-to-One, Optional)
- **Cardinality**: Many transactions can involve the same counterparty
- **Optional**: Transactions can exist without a counterparty
- **Business Rule**: Counterparty deletion preserves transactions (sets to NULL)

#### Account ↔ AccountHistory (One-to-Many)
- **Cardinality**: One account has many historical records
- **Integrity**: Cascade delete removes history with account
- **Business Rule**: Balance changes are automatically recorded

## 📈 Database Indexes

Strategic indexes optimize common query patterns:

### Transaction Table Indexes

```sql
-- Account and date filtering (most common query pattern)
CREATE INDEX idx_transaction_account_date 
ON tbl_Transaction(i8_AccountID, str_Date);

-- Category-based budget queries
CREATE INDEX idx_transaction_category 
ON tbl_Transaction(i8_AccountID, i8_CategoryID, str_Date);

-- Counterparty transaction lookup
CREATE INDEX idx_transaction_counterparty_date 
ON tbl_Transaction(i8_CounterpartyID, str_Date);

-- Combined account-counterparty queries
CREATE INDEX idx_transaction_account_counterparty_date 
ON tbl_Transaction(i8_AccountID, i8_CounterpartyID, str_Date);
```

### Account Table Indexes

```sql
-- Widget position lookup for GUI
CREATE INDEX idx_account_widget_position 
ON tbl_Account(i8_WidgetPosition);
```

### Account History Indexes

```sql
-- Account history queries
CREATE INDEX idx_accounthistory_account 
ON tbl_AccountHistory(i8_AccountID);
```

### Category Indexes

```sql
-- Budget period grouping
CREATE INDEX idx_category_budgetperiod 
ON tbl_Category(i8_BudgetPeriodID);
```

## 💡 Design Rationale

### Normalization Level

The schema uses **Third Normal Form (3NF)** to balance:
- **Data Integrity**: Minimize redundancy and update anomalies
- **Query Performance**: Reasonable join complexity for common operations
- **Maintenance**: Clear relationships and constraints

### Data Types

#### Numeric Types
- **INTEGER**: Used for IDs and whole numbers
- **REAL**: Used for monetary amounts and calculations
- **TEXT**: Used for all string data (SQLite's preferred string type)

#### Date Storage
- **TEXT Format**: Dates stored as "YYYY-MM-DD" strings
- **Rationale**: SQLite's date functions work well with ISO format
- **Benefits**: Human-readable, sortable, internationally standard

#### Monetary Values
- **REAL Type**: Sufficient precision for typical financial calculations
- **Alternative Considered**: INTEGER (storing cents) for exact arithmetic
- **Decision**: REAL chosen for simplicity in German locale with Euro cents

### Constraint Strategy

#### Primary Keys
- **AUTOINCREMENT**: Ensures unique, sequential IDs
- **Benefits**: Simple foreign key references, consistent ordering

#### Foreign Keys
- **Strict Enforcement**: All relationships enforced at database level
- **Cascade Rules**: Logical data cleanup when parent records deleted
- **NULL Handling**: Optional relationships allow NULL values

#### Unique Constraints
- **Business Logic**: Prevents duplicate accounts, categories, counterparties
- **Data Quality**: Ensures consistent data entry

### Performance Considerations

#### Index Strategy
- **Covering Indexes**: Include frequently queried columns
- **Composite Indexes**: Support multi-column WHERE clauses
- **Selective Indexing**: Only index frequently queried columns

#### Query Optimization
- **Date Range Queries**: Optimized with account+date composite indexes
- **Category Reporting**: Efficient budget calculation queries
- **Balance Updates**: Fast account lookup by widget position

## 🔧 Database Operations

### Common Query Patterns

#### Account Balance Calculation
```sql
SELECT SUM(real_Amount) as balance 
FROM tbl_Transaction 
WHERE i8_AccountID = ? 
  AND str_Date <= ?;
```

#### Category Budget Analysis
```sql
SELECT c.str_CategoryName, 
       c.real_Budget,
       SUM(t.real_Amount) as spent
FROM tbl_Category c
LEFT JOIN tbl_Transaction t ON c.i8_CategoryID = t.i8_CategoryID
WHERE t.str_Date BETWEEN ? AND ?
GROUP BY c.i8_CategoryID;
```

#### Account Widget Data
```sql
SELECT i8_AccountID, i8_WidgetPosition, str_AccountName, 
       str_AccountNumber, real_AccountBalance, real_AccountDifference,
       str_RecordDate, str_ChangeDate
FROM tbl_Account 
ORDER BY i8_WidgetPosition;
```

### Data Maintenance

#### Balance Updates
When transactions are added/modified:
1. **Recalculate Account Balance**: Sum all transactions for account
2. **Update Account Record**: Store new balance and difference
3. **Record History**: Add entry to AccountHistory table

#### Category Budget Tracking
- **Real-time Calculation**: Budget vs. actual spending
- **Period-based Queries**: Spending within specific time periods
- **Percentage Calculations**: Budget utilization percentages

## 🚀 Future Enhancements

### Planned Schema Extensions

#### Multi-Currency Support
```sql
-- Future table for currency support
CREATE TABLE tbl_Currency (
    i8_CurrencyID INTEGER PRIMARY KEY,
    str_CurrencyCode TEXT UNIQUE NOT NULL,  -- EUR, USD, etc.
    str_Symbol TEXT,                        -- €, $, etc.
    real_ExchangeRate REAL DEFAULT 1.0
);

-- Add currency support to accounts
ALTER TABLE tbl_Account 
ADD COLUMN i8_CurrencyID INTEGER DEFAULT 1;
```

#### User Management
```sql
-- Future multi-user support
CREATE TABLE tbl_User (
    i8_UserID INTEGER PRIMARY KEY,
    str_Username TEXT UNIQUE NOT NULL,
    str_HashedPassword TEXT,
    str_Email TEXT,
    str_CreatedDate TEXT
);

-- Add user association to accounts
ALTER TABLE tbl_Account 
ADD COLUMN i8_UserID INTEGER;
```

#### Enhanced Categorization
```sql
-- Future subcategory support
ALTER TABLE tbl_Category 
ADD COLUMN i8_ParentCategoryID INTEGER;

-- Category hierarchy
CREATE INDEX idx_category_parent 
ON tbl_Category(i8_ParentCategoryID);
```

### Migration Strategy

The database schema is designed for forward compatibility:
- **Additive Changes**: New columns with DEFAULT values
- **Migration Scripts**: Automated schema update procedures
- **Version Tracking**: Schema version management
- **Backward Compatibility**: Graceful handling of older database versions

---

This database schema provides a solid foundation for the Budget Planner application while maintaining flexibility for future enhancements and scalability requirements.