#!/usr/bin/env python3
"""
migrate_sp_project.py
=======================
Migrates sp_project (43 rows) from MySQL AcmeAnvil -> PostgreSQL pyespdb.

Schema notes:
  - pr_id is excluded from INSERT (PG uses GENERATED ALWAYS AS IDENTITY)
  - tinyint fields (is_static_fg, is_active_fg, add_interval_fg) cast to bool
  - cat_yaxis_divisor: int -> numeric (no conversion needed)

Requirements:
    pip3 install pymysql psycopg2-binary

Usage:
    python3 migrate_sp_project.py
"""

import pymysql
import psycopg2
import psycopg2.extras
import sys
from datetime import datetime

# ─────────────────────────────────────────────
# CONNECTION SETTINGS  ← edit these
# ─────────────────────────────────────────────

MYSQL_CONFIG = {
    # Option A: TCP (default)
    "host":     "127.0.0.1",
    "port":     3306,
    "user":     "root",
    "password": "welcome1",            # set if you have a MySQL root password
    "database": "AcmeAnvil",
    "charset":  "utf8mb4",
    # Option B: Homebrew socket — comment out host/port above and uncomment:
    # "unix_socket": "/opt/homebrew/var/mysql/mysql.sock",
}

PG_CONFIG = {
    "host":     "localhost",   # or "/tmp" for Homebrew socket
    "port":     5432,
    "user":     "",            # your Mac username (e.g. "hank")
    "password": "",
    "dbname":   "pyespdb",
}

# ─────────────────────────────────────────────
# TRANSFER MODE
# "truncate"  — clear target table then insert  (default, safe to re-run)
# "append"    — insert without clearing
# ─────────────────────────────────────────────
TRANSFER_MODE = "truncate"

TABLE         = "sp_project"
BOOL_COLUMNS  = {"is_static_fg", "is_active_fg", "add_interval_fg"}

# Columns to SELECT from MySQL (all 8)
MYSQL_COLS = [
    "pr_id",           # used for ordering only, not inserted
    "pr_name",
    "pr_shortname",
    "pr_creation_date",
    "is_active_fg",
    "pr_modify_date",
    "sp_client_cl_id"
]

# Columns to INSERT into PostgreSQL (pr_id excluded — GENERATED ALWAYS AS IDENTITY)
PG_INSERT_COLS = [c for c in MYSQL_COLS if c != "pr_id"]


def to_bool(value):
    """Convert MySQL tinyint (0/1/None) to Python bool or None."""
    if value is None:
        return None
    return bool(value)


def main():
    start = datetime.now()
    print("=" * 55)
    print(f"  Migrating {TABLE}")
    print(f"  MySQL AcmeAnvil  →  PostgreSQL pyespdb")
    print(f"  Mode: {TRANSFER_MODE}")
    print(f"  Started: {start.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)

    # ── Connect MySQL ──────────────────────────────────────
    try:
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)
        mysql_cur  = mysql_conn.cursor(pymysql.cursors.DictCursor)
        print("\n✓ Connected to MySQL AcmeAnvil")
    except Exception as e:
        print(f"\n✗ MySQL connection failed: {e}")
        print("  → Check MYSQL_CONFIG at the top of this script")
        sys.exit(1)

    # ── Connect PostgreSQL ─────────────────────────────────
    try:
        pg_conn = psycopg2.connect(**PG_CONFIG)
        pg_conn.autocommit = False
        pg_cur  = pg_conn.cursor()
        print("✓ Connected to PostgreSQL pyespdb")
    except Exception as e:
        print(f"\n✗ PostgreSQL connection failed: {e}")
        print("  → Check PG_CONFIG at the top of this script")
        mysql_conn.close()
        sys.exit(1)

    try:
        # ── Fetch from MySQL ───────────────────────────────
        select_cols = ", ".join(f"`{c}`" for c in MYSQL_COLS)
        mysql_cur.execute(f"SELECT {select_cols} FROM `{TABLE}` ORDER BY pr_id")
        rows = mysql_cur.fetchall()
        print(f"\n  Fetched {len(rows):,} rows from MySQL")

        # ── Prepare target table ───────────────────────────
        if TRANSFER_MODE == "truncate":
            pg_cur.execute(f'TRUNCATE TABLE "{TABLE}" RESTART IDENTITY CASCADE')
            print(f"  Truncated PostgreSQL {TABLE} (identity reset)")

        # ── Transform & insert ─────────────────────────────
        insert_sql = (
            f'INSERT INTO "{TABLE}" '
            f'({", ".join(f"{chr(34)}{c}{chr(34)}" for c in PG_INSERT_COLS)}) '
            f'VALUES ({", ".join(["%s"] * len(PG_INSERT_COLS))})'
        )

        records = []
        for row in rows:
            record = []
            for col in PG_INSERT_COLS:
                val = row[col]
                if col in BOOL_COLUMNS:
                    val = to_bool(val)
                record.append(val)
            records.append(tuple(record))

        psycopg2.extras.execute_batch(pg_cur, insert_sql, records)
        pg_conn.commit()

        # ── Verify ────────────────────────────────────────
        pg_cur.execute(f'SELECT COUNT(*) FROM "{TABLE}"')
        pg_count = pg_cur.fetchone()[0]

        elapsed = datetime.now() - start
        print(f"\n{'=' * 55}")
        print(f"  ✓ Migration complete in {elapsed.total_seconds():.2f}s")
        print(f"  Rows in MySQL source : {len(rows):,}")
        print(f"  Rows in PG target    : {pg_count:,}")
        if len(rows) == pg_count:
            print(f"  Row counts match ✓")
        else:
            print(f"  ⚠ Row count mismatch — please investigate")
        print(f"{'=' * 55}")

    except Exception as e:
        pg_conn.rollback()
        print(f"\n✗ Migration failed: {e}")
        sys.exit(1)

    finally:
        mysql_conn.close()
        pg_conn.close()


if __name__ == "__main__":
    main()
