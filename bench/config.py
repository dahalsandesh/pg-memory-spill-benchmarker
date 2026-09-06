import os

DB_USER = os.getenv("POSTGRES_USER", "benchuser")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "benchpassword")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "benchdb")

DB_DSN: str = f"dbname={DB_NAME} user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT}"

API_URL = os.getenv("METRICS_API_URL", "http://localhost:8000/api/results/")

# Seeding config
TARGET_ROWS = 2_000_000
BATCH_SIZE = 50_000
