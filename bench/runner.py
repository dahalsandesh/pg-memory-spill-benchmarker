import psycopg2
import time
import requests
import logging
import os
import config
from queries import QUERIES
from explain_parser import detect_spills
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def run_benchmarks():
    logging.info("Starting benchmarks...")
    conn = psycopg2.connect(config.DB_DSN)
    conn.autocommit = True
    cursor = conn.cursor()

    # Pre-warm connection and reset pg_stat_statements
    cursor.execute("SELECT 1;")
    try:
        cursor.execute("SELECT pg_stat_statements_reset();")
    except Exception as e:
        logging.warning(f"Could not reset pg_stat_statements: {e}")
    
    ram_limit = int(os.getenv("POSTGRES_MEM_LIMIT_MB", 256))

    for query_name, query_sql in QUERIES.items():
        logging.info(f"Executing {query_name}...")
        
        # Reset stats before each query for clean measurement
        try:
            cursor.execute("SELECT pg_stat_statements_reset();")
        except:
            pass

        explain_sql = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query_sql}"
        
        start_time = time.time()
        cursor.execute(explain_sql)
        plan_json = cursor.fetchone()[0]
        execution_time_ms = (time.time() - start_time) * 1000

        # Run the actual query again without EXPLAIN to get clean pg_stat_statements stats
        # (EXPLAIN ANALYZE already executes it, but running again ensures we capture just the query execution if needed.
        # Actually EXPLAIN ANALYZE is captured by pg_stat_statements, so we can just query pg_stat_statements now.)
        
        stats = {
            "temp_blks_read": 0,
            "temp_blks_written": 0
        }
        
        try:
            # Match part of the query to find it in pg_stat_statements
            search_query = query_sql.strip().split("\n")[0].strip()[:50]
            cursor.execute("""
                SELECT sum(temp_blks_read), sum(temp_blks_written) 
                FROM pg_stat_statements 
                WHERE query ILIKE %s
            """, (f"%{search_query}%",))
            row = cursor.fetchone()
            if row and row[0] is not None:
                stats["temp_blks_read"] = row[0]
                stats["temp_blks_written"] = row[1]
        except Exception as e:
            logging.warning(f"Failed to query pg_stat_statements: {e}")

        report = detect_spills(plan_json[0]["Plan"])
        
        # Merge stats from pg_stat_statements if they are higher (pg_stat_statements tracks cumulatively for the statement)
        report["temp_read_blocks"] = max(report["temp_read_blocks"], stats["temp_blks_read"])
        report["temp_written_blocks"] = max(report["temp_written_blocks"], stats["temp_blks_written"])

        logging.info(f"[{query_name}] Exec Time: {execution_time_ms:.2f}ms | Spilled: {report['spilled']} ({report['spill_type']})")
        
        payload = {
            "query_name": query_name,
            "execution_time_ms": execution_time_ms,
            "ram_allocated_mb": ram_limit,
            "spilled_to_disk": report["spilled"],
            "spill_type": report["spill_type"],
            "sort_space_used_kb": report["sort_space_used_kb"],
            "hash_batches": report["hash_batches"],
            "temp_read_blocks": report["temp_read_blocks"],
            "temp_written_blocks": report["temp_written_blocks"],
            "work_mem_kb": 2048, # we set it to 2MB in postgresql.conf
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            requests.post(config.API_URL, json=payload, timeout=2)
        except requests.RequestException as e:
            logging.warning(f"Failed to post metrics to API: {e}")

    cursor.close()
    conn.close()
    logging.info("Benchmarks complete.")

if __name__ == "__main__":
    run_benchmarks()
