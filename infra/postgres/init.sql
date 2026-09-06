CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Minimal schema for accounts and transactions
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id),
    amount DECIMAL(15, 2) NOT NULL,
    txn_date TIMESTAMP NOT NULL
);

CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER REFERENCES transactions(id),
    old_value DECIMAL(15, 2),
    new_value DECIMAL(15, 2),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transactions_account_id ON transactions(account_id);
CREATE INDEX idx_transactions_date ON transactions(txn_date);
CREATE INDEX idx_audit_logs_txn ON audit_logs(transaction_id);
