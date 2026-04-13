#!/usr/bin/env python3
"""
migrate_acmeanvil_to_pyespdb.py
================================
Migrates all tables from MySQL AcmeAnvil -> PostgreSQL pyespdb.

Requirements:
    pip install pymysql psycopg2-binary sqlalchemy

Usage:
    python3 migrate_acmeanvil_to_pyespdb.py

Edit the CONNECTION SETTINGS section below before running.
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
    "host":     "127.0.0.1",   # or use unix_socket path (see comment below)
    "port":     3306,
    "user":     "root",
    "password": "welcome1",            # set your MySQL password if needed
    "database": "AcmeAnvil",
    "charset":  "utf8mb4",
    # If using Homebrew MySQL socket, replace host/port with:
    # "unix_socket": "/opt/homebrew/var/mysql/mysql.sock",
}

PG_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "user":     "",            # set to your Mac username (or postgres)
    "password": "",            # blank if using peer auth / Homebrew
    "dbname":   "pyespdb",
    # If using Postgres.app or socket, you can also try:
    # "host": "/tmp"
}

# ─────────────────────────────────────────────
# TRANSFER MODE
# Options: "drop_recreate" | "truncate" | "append"
# ─────────────────────────────────────────────
TRANSFER_MODE = "drop_recreate"

BATCH_SIZE = 500   # rows per INSERT batch


# ─────────────────────────────────────────────
# MySQL → PostgreSQL type mapping
# ─────────────────────────────────────────────
TYPE_MAP = {
    "tinyint":    "SMALLINT",
    "smallint":   "SMALLINT",
    "mediumint":  "INTEGER",
    "int":        "INTEGER",
    "bigint":     "BIGINT",
    "float":      "REAL",
    "double":     "DOUBLE PRECISION",
    "decimal":    "NUMERIC",
    "char":       "CHAR",
    "varchar":    "VARCHAR",
    "tinytext":   "TEXT",
    "text":       "TEXT",
    "mediumtext": "TEXT",
    "longtext":   "TEXT",
    "tinyblob":   "BYTEA",
    "blob":       "BYTEA",
    "mediumblob": "BYTEA",
    "longblob":   "BYTEA",
    "binary":     "BYTEA",
    "varbinary":  "BYTEA",
    "date":       "DATE",
    "datetime":   "TIMESTAMP",
    "timestamp":  "TIMESTAMP",
    "time":       "TIME",
    "year":       "SMALLINT",
    "boolean":    "BOOLEAN",
    "bool":       "BOOLEAN",
    "json":       "JSONB",
    "enum":       "TEXT",
    "set":        "TEXT",
    "bit":        "BOOLEAN",
}


def map_column_type(mysql_type: str, col_length, col_precision, col_scale) -> str:
    base = mysql_type.lower().split("(")[0].strip()
    pg_type = TYPE_MAP.get(base, "TEXT")

    if pg_type in ("VARCHAR", "CHAR") and col_length:
        pg_type = f"{pg_type}({col_length})"
    elif pg_type == "NUMERIC" and col_precision:
        if col_scale:
            pg_type = f"NUMERIC({col_precision},{col_scale})"
        else:
            pg_type = f"NUMERIC({col_precision})"
    return pg_type


def get_mysql_tables(mysql_cur):
    mysql_cur.execute("SHOW TABLES")
    return [row[0] for row in mysql_cur.fetchall()]


def get_mysql_columns(mysql_cur, table):
    mysql_cur.execute(f"""
        SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH,
               NUMERIC_PRECISION, NUMERIC_SCALE, IS_NULLABLE, COLUMN_KEY
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
    """, (table,))
    return mysql_cur.fetchall()


def build_create_table_sql(table, columns):
    col_defs = []
    pk_cols = []
    for col_name, data_type, char_len, num_prec, num_scale, nullable, col_key in columns:
        pg_type = map_column_type(data_type, char_len, num_prec, num_scale)
        null_clause = "NOT NULL" if nullable == "NO" else "NULL"
        col_defs.append(f'    "{col_name}" {pg_type} {null_clause}')
        if col_key == "PRI":
            pk_cols.append(f'"{col_name}"')

    if pk_cols:
        col_defs.append(f'    PRIMARY KEY ({", ".join(pk_cols)})')

    return f'CREATE TABLE "{table}" (\n' + ",\n".join(col_defs) + "\n);"


def migrate_table(mysql_cur, pg_cur, table):
    print(f"\n  Table: {table}")

    columns = get_mysql_columns(mysql_cur, table)
    col_names = [c[0] for c in columns]
    quoted_cols = ", ".join(f'"{c}"' for c in col_names)
    placeholders = ", ".join(["%s"] * len(col_names))

    # Handle transfer mode
    if TRANSFER_MODE == "drop_recreate":
        pg_cur.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
        ddl = build_create_table_sql(table, columns)
        pg_cur.execute(ddl)
        print(f"    Created table in PostgreSQL")
    elif TRANSFER_MODE == "truncate":
        pg_cur.execute(f'TRUNCATE TABLE "{table}"')
        print(f"    Truncated table")
    # append: do nothing to the table structure

    # Fetch and insert data
    mysql_cur.execute(f'SELECT {quoted_cols} FROM `{table}`')
    total = 0
    while True:
        rows = mysql_cur.fetchmany(BATCH_SIZE)
        if not rows:
            break
        # Convert rows to list of tuples (handle any special types)
        clean_rows = []
        for row in rows:
            clean_rows.append(tuple(
                str(v) if isinstance(v, (bytes, bytearray)) else v
                for v in row
            ))
        insert_sql = f'INSERT INTO "{table}" ({quoted_cols}) VALUES ({placeholders})'
        psycopg2.extras.execute_batch(pg_cur, insert_sql, clean_rows, page_size=BATCH_SIZE)
        total += len(clean_rows)

    print(f"    Migrated {total:,} rows")
    return total


def main():
    start = datetime.now()
    print("=" * 55)
    print("  AcmeAnvil (MySQL) → pyespdb (PostgreSQL) Migration")
    print(f"  Mode: {TRANSFER_MODE}")
    print(f"  Started: {start.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)

    # Connect MySQL
    try:
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)
        mysql_cur = mysql_conn.cursor()
        print("\n✓ Connected to MySQL AcmeAnvil")
    except Exception as e:
        print(f"\n✗ MySQL connection failed: {e}")
        print("  → Check MYSQL_CONFIG settings at the top of this script")
        sys.exit(1)

    # Connect PostgreSQL
    try:
        pg_conn = psycopg2.connect(**PG_CONFIG)
        pg_conn.autocommit = False
        pg_cur = pg_conn.cursor()
        print("✓ Connected to PostgreSQL pyespdb")
    except Exception as e:
        print(f"\n✗ PostgreSQL connection failed: {e}")
        print("  → Check PG_CONFIG settings at the top of this script")
        mysql_conn.close()
        sys.exit(1)

    # Get tables
    tables = get_mysql_tables(mysql_cur)
    print(f"\nFound {len(tables)} table(s) to migrate: {tables}\n")

    grand_total = 0
    failed = []

    for table in tables:
        try:
            count = migrate_table(mysql_cur, pg_cur, table)
            grand_total += count
        except Exception as e:
            print(f"    ✗ ERROR on {table}: {e}")
            pg_conn.rollback()
            failed.append((table, str(e)))
            continue

    pg_conn.commit()
    mysql_conn.close()
    pg_conn.close()

    elapsed = datetime.now() - start
    print("\n" + "=" * 55)
    print(f"  Migration complete in {elapsed.total_seconds():.1f}s")
    print(f"  Total rows migrated: {grand_total:,}")
    if failed:
        print(f"  Failed tables ({len(failed)}):")
        for t, err in failed:
            print(f"    - {t}: {err}")
    else:
        print("  All tables migrated successfully ✓")
    print("=" * 55)


if __name__ == "__main__":
    main()
