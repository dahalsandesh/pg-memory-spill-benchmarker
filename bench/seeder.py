import sys
import time
import logging
import psycopg2
from faker import Faker
import config
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def seed_database() -> None:
    conn = psycopg2.connect(config.DB_DSN)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Check if already seeded
        cursor.execute("SELECT count(*) FROM transactions;")
        if cursor.fetchone()[0] > 0:
            logging.info("Database already seeded. Skipping.")
            return

        logging.info("Starting data seeding via PostgreSQL generate_series...")
        start_time = time.time()

        # Seed Accounts using pure SQL and generate_series
        # Generates 50,000 accounts with GAAP types
        account_sql = """
            INSERT INTO accounts (account_number, name, account_type, gaap_code, is_debit_normal)
            SELECT
                LPAD(i::text, 6, '0') as account_number,
                'Account ' || i as name,
                CASE (i % 5)
                    WHEN 0 THEN 'ASSET'
                    WHEN 1 THEN 'LIABILITY'
                    WHEN 2 THEN 'EQUITY'
                    WHEN 3 THEN 'REVENUE'
                    ELSE 'EXPENSE'
                END as account_type,
                ((i % 5) + 1) * 1000 as gaap_code,
                (i % 5) IN (0, 4) as is_debit_normal
            FROM generate_series(1, 50000) as i;
        """
        cursor.execute(account_sql)
        logging.info("Inserted 50,000 accounts.")

        # Seed Transactions using generate_series (2,000,000 rows)
        target_rows = config.TARGET_ROWS
        logging.info(f"Generating {target_rows} transactions...")
        
        txn_sql = f"""
            INSERT INTO transactions (debit_account_id, credit_account_id, amount, description, reference_id, txn_date)
            SELECT
                (random() * 49999 + 1)::int as debit_account_id,
                (random() * 49999 + 1)::int as credit_account_id,
                round((random() * 5000 + 10)::numeric, 2) as amount,
                'Auto-generated transaction ' || i,
                'REF-' || LPAD(i::text, 8, '0'),
                NOW() - (random() * interval '365 days')
            FROM generate_series(1, {target_rows}) as i;
        """
        cursor.execute(txn_sql)
        logging.info(f"Inserted {target_rows} transactions.")

        # Seed Audit Logs (2,000,000 rows matching transactions)
        logging.info("Generating audit logs...")
        audit_sql = """
            INSERT INTO audit_logs (transaction_id, changed_by, change_reason, old_value, new_value, changed_at)
            SELECT
                id as transaction_id,
                'system_seeder' as changed_by,
                'Initial transaction creation' as change_reason,
                0.00 as old_value,
                amount as new_value,
                txn_date + interval '1 second'
            FROM transactions;
        """
        cursor.execute(audit_sql)
        logging.info(f"Inserted {target_rows} audit logs.")

        elapsed = time.time() - start_time
        logging.info(f"Seeding complete in {elapsed:.2f} seconds.")

    except Exception as e:
        logging.error(f"Error seeding database: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed_database()
