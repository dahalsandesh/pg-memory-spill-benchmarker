CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- US-GAAP Accounts Schema
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    account_number VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    account_type VARCHAR(50) NOT NULL CHECK (account_type IN ('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE')),
    gaap_code VARCHAR(20),
    currency VARCHAR(3) DEFAULT 'USD',
    is_debit_normal BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transaction Ledger
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    debit_account_id INTEGER REFERENCES accounts(id),
    credit_account_id INTEGER REFERENCES accounts(id),
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    description TEXT,
    reference_id VARCHAR(100),
    txn_date TIMESTAMP NOT NULL,
    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit Tracking
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER REFERENCES transactions(id),
    changed_by VARCHAR(100),
    change_reason TEXT,
    old_value DECIMAL(15, 2),
    new_value DECIMAL(15, 2),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes designed to force Sort spills on Window functions (instead of index-only scans)
CREATE INDEX idx_transactions_account_id ON transactions(debit_account_id);
CREATE INDEX idx_transactions_date ON transactions(txn_date);
CREATE INDEX idx_audit_logs_txn ON audit_logs(transaction_id);

-- Composite indexes to stress test multi-key sorts and aggregations
CREATE INDEX idx_txn_date_amount ON transactions(txn_date, amount);
CREATE INDEX idx_audit_composite ON audit_logs(transaction_id, changed_at, new_value);
