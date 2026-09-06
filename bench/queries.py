from typing import Dict

QUERIES: Dict[str, str] = {
    "Q1_running_balance": """
        SELECT account_id, txn_date, amount,
               SUM(amount) OVER (PARTITION BY account_id ORDER BY txn_date) as running_balance
        FROM transactions
    """,
    
    "Q2_hash_join_audit": """
        SELECT t.account_id, SUM(a.new_value - a.old_value) as variance
        FROM transactions t
        JOIN audit_logs a ON t.id = a.transaction_id
        GROUP BY t.account_id
        HAVING SUM(a.new_value - a.old_value) > 1000
    """,
    
    "Q3_complex_window_rank": """
        WITH account_stats AS (
            SELECT account_id, 
                   COUNT(id) as txn_count, 
                   SUM(amount) as total_amount
            FROM transactions
            GROUP BY account_id
        )
        SELECT account_id, txn_count, total_amount,
               RANK() OVER (ORDER BY total_amount DESC) as amount_rank
        FROM account_stats
    """
}
