"""Check that Neon (Postgres) and Upstash (Redis) are reachable.

Reads the two connection URLs from environment variables.
Run from the repo root:  python scripts/check_connections.py
"""
import os

# Load .env if python-dotenv is installed (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import psycopg
import redis


def check_postgres():
    url = os.environ.get("NEON_DATABASE_URL")
    if not url:
        print("Postgres: FAILED - NEON_DATABASE_URL is not set")
        return
    try:
        with psycopg.connect(url) as conn:
            conn.execute("SELECT 1")
        print("Postgres: OK")
    except Exception as error:
        # Print only the error type, never the URL (it contains the password)
        print(f"Postgres: FAILED - {type(error).__name__}")


def check_redis():
    url = os.environ.get("UPSTASH_REDIS_URL")
    if not url:
        print("Redis: FAILED - UPSTASH_REDIS_URL is not set")
        return
    try:
        client = redis.from_url(url)
        client.ping()
        print("Redis: OK")
    except Exception as error:
        print(f"Redis: FAILED - {type(error).__name__}")


if __name__ == "__main__":
    check_postgres()
    check_redis()