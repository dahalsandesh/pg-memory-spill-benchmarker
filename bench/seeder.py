import sys
import time
from typing import List, Tuple
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values
from faker import Faker
import config

fake = Faker()

def generate_accounts(num_accounts: int) -> List[Tuple[str, datetime]]:
    print(f"Generating {num_accounts} accounts...")
    return [(fake.company(), datetime.now()) for _ in range(num_accounts)]

def seed_database() -> None:
    conn = psycopg2.connect(config.DB_DSN)
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Check if already seeded
        cursor.execute("SELECT count(*) FROM transactions;")
        if cursor.fetchone()[0] > 0:
            print("Database already seeded. Skipping.")
            return

        print("Starting massive data seeding...")
        start_time = time.time()

        # Seed Accounts
        num_accounts = 50_000
        accounts_data = generate_accounts(num_accounts)
        execute_values(
            cursor,
            "INSERT INTO accounts (name, created_at) VALUES %s",
            accounts_data,
            page_size=10000
        )
        print(f"Inserted {num_accounts} accounts.")

        # Seed Transactions and Audit Logs
        rows_inserted = 0
        while rows_inserted < config.TARGET_ROWS:
            batch_size = min(config.BATCH_SIZE, config.TARGET_ROWS - rows_inserted)
            
            # Generate transactions
            txn_data = [
                (
                    fake.random_int(min=1, max=num_accounts),
                    round(fake.random.uniform(10.0, 5000.0), 2),
                    fake.date_time_between(start_date='-1y', end_date='now')
                )
                for _ in range(batch_size)
            ]

            cursor.execute("BEGIN;")
            # psycopg2 fetch=True requires RETURNING
            inserted_txn_ids = execute_values(
                cursor,
                "INSERT INTO transactions (account_id, amount, txn_date) VALUES %s RETURNING id",
                txn_data,
                page_size=10000,
                fetch=True
            )

            # Generate audit logs for these transactions
            audit_data = [
                (
                    txn_id[0],
                    round(fake.random.uniform(10.0, 5000.0), 2),
                    txn_data[i][1],
                    datetime.now()
                )
                for i, txn_id in enumerate(inserted_txn_ids)
            ]

            execute_values(
                cursor,
                "INSERT INTO audit_logs (transaction_id, old_value, new_value, changed_at) VALUES %s",
                audit_data,
                page_size=10000
            )
            
            cursor.execute("COMMIT;")
            
            rows_inserted += batch_size
            print(f"Progress: {rows_inserted}/{config.TARGET_ROWS} rows inserted.")

        elapsed = time.time() - start_time
        print(f"Seeding complete in {elapsed:.2f} seconds.")

    except Exception as e:
        print(f"Error seeding database: {e}")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    seed_database()
