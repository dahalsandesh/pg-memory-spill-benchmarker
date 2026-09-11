import time
import requests
import random
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

API_URL = "http://localhost:8000/api/results/"

def generate_mock_spill_event():
    # Simulate a window function or aggregation query
    query_names = [
        "Q1: Monthly Account Balances (Window Function)",
        "Q2: Multi-Key GAAP Rollup (HashAgg)",
        "Q3: Anomaly Detection Sort (External Merge)"
    ]
    query_name = random.choice(query_names)
    
    # 70% chance to spill under 2MB work_mem simulation
    spilled = random.random() < 0.7
    
    if spilled:
        spill_type = random.choice(["external_merge_Disk", "hash_batches"])
        execution_time_ms = random.uniform(800.0, 3500.0) # High latency due to I/O
        sort_space_used_kb = random.randint(5000, 25000) if spill_type == "external_merge_Disk" else 0
        hash_batches = random.randint(16, 64) if spill_type == "hash_batches" else 0
        temp_read_blocks = random.randint(100, 500)
        temp_written_blocks = random.randint(100, 500)
    else:
        spill_type = "none"
        execution_time_ms = random.uniform(50.0, 300.0) # Fast in-memory quicksort
        sort_space_used_kb = random.randint(500, 1900) # Under 2MB
        hash_batches = 1 # Single batch
        temp_read_blocks = 0
        temp_written_blocks = 0

    payload = {
        "query_name": query_name,
        "execution_time_ms": execution_time_ms,
        "ram_allocated_mb": 256,
        "spilled_to_disk": spilled,
        "spill_type": spill_type,
        "sort_space_used_kb": sort_space_used_kb,
        "hash_batches": hash_batches,
        "temp_read_blocks": temp_read_blocks,
        "temp_written_blocks": temp_written_blocks,
        "work_mem_kb": 2048,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return payload

def run():
    logging.info("Starting mock benchmarker to simulate Flow-Centric Pipeline degradation...")
    logging.info(f"Targeting API: {API_URL}")
    
    while True:
        payload = generate_mock_spill_event()
        try:
            res = requests.post(API_URL, json=payload, timeout=2)
            if res.status_code == 201:
                spill_msg = f"SPILLED ({payload['spill_type']})" if payload["spilled_to_disk"] else "IN-MEMORY"
                logging.info(f"[{payload['query_name']}] {payload['execution_time_ms']:.1f}ms | {spill_msg}")
            else:
                logging.warning(f"API returned {res.status_code}: {res.text}")
        except requests.RequestException as e:
            logging.error(f"Failed to post to API (is it running?): {e}")
            
        time.sleep(random.uniform(2.0, 5.0))

if __name__ == "__main__":
    run()
