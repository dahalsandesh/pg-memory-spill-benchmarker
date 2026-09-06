import psycopg2
import time
import requests
import config
from queries import QUERIES
from explain_parser import detect_spills
from datetime import datetime

def run_benchmarks():
    print("Starting benchmarks...")
    conn = psycopg2.connect(config.DB_DSN)
    conn.autocommit = True
    cursor = conn.cursor()

    # Pre-warm connection
    cursor.execute("SELECT 1;")
    
    for query_name, query_sql in QUERIES.items():
        print(f"\nExecuting {query_name}...")
        
        explain_sql = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query_sql}"
        
        start_time = time.time()
        cursor.execute(explain_sql)
        plan_json = cursor.fetchone()[0]
        execution_time_ms = (time.time() - start_time) * 1000

        spilled = detect_spills(plan_json[0]["Plan"])
        
        print(f"[{query_name}] Exec Time: {execution_time_ms:.2f}ms | Spilled: {spilled}")
        
        payload = {
            "query_name": query_name,
            "execution_time_ms": execution_time_ms,
            "ram_allocated_mb": 256,
            "spilled_to_disk": spilled,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        try:
            requests.post(config.API_URL, json=payload, timeout=2)
        except requests.RequestException:
            pass # API might not be running yet, silent pass for Phase 2

    cursor.close()
    conn.close()
    print("\nBenchmarks complete.")

if __name__ == "__main__":
    run_benchmarks()
