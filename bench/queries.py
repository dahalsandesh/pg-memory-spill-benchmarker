from typing import Dict

QUERIES: Dict[str, str] = {
    "Q1_running_balance": """
        SELECT debit_account_id, txn_date, amount,
               SUM(amount) OVER (PARTITION BY debit_account_id ORDER BY txn_date) as running_balance
        FROM transactions
    """,
    
    "Q2_hash_join_audit": """
        SELECT t.debit_account_id, SUM(a.new_value - a.old_value) as variance
        FROM transactions t
        JOIN audit_logs a ON t.id = a.transaction_id
        GROUP BY t.debit_account_id
        HAVING SUM(a.new_value - a.old_value) > 1000
    """,
    
    "Q3_complex_window_rank": """
        SELECT id, debit_account_id, amount, txn_date,
               RANK() OVER (ORDER BY amount DESC, txn_date ASC) as amount_rank
        FROM transactions
    """,

    "Q4_multi_join_variance": """
        SELECT acc.account_number, acc.account_type, SUM(t.amount) as total_txn, SUM(a.new_value) as total_audit
        FROM accounts acc
        JOIN transactions t ON acc.id = t.debit_account_id
        JOIN audit_logs a ON t.id = a.transaction_id
        GROUP BY acc.account_number, acc.account_type
        ORDER BY total_txn DESC
    """
}
