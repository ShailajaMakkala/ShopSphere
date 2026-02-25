"""
Script to transfer data from Mohana's sqlite3 (old) to our new backend sqlite3.
Run this from: project-ecommerce root folder
Usage: python transfer_data.py
"""
import sqlite3
import os

SOURCE_DB = "Duplicate/ShopSphere/db.sqlite3"
TARGET_DB = "backend/db.sqlite3"

def get_tables(conn):
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'django_migrations'")
    return [row[0] for row in cursor.fetchall()]

def get_columns(conn, table):
    cursor = conn.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cursor.fetchall()]

src = sqlite3.connect(SOURCE_DB)
tgt = sqlite3.connect(TARGET_DB)

src_tables = get_tables(src)
tgt_tables = get_tables(tgt)

print(f"\nSource DB tables: {len(src_tables)}")
print(f"Target DB tables: {len(tgt_tables)}")

# Only transfer tables that exist in BOTH databases
common_tables = [t for t in src_tables if t in tgt_tables]
print(f"Common tables to transfer: {len(common_tables)}")

success = 0
skipped = 0
errors = 0

tgt.execute("PRAGMA foreign_keys = OFF")
tgt.commit()

for table in common_tables:
    try:
        src_cols = get_columns(src, table)
        tgt_cols = get_columns(tgt, table)
        
        # Only import columns that exist in target
        shared_cols = [c for c in src_cols if c in tgt_cols]
        
        if not shared_cols:
            print(f"  SKIP {table} (no shared columns)")
            skipped += 1
            continue
        
        # Fetch data from source
        src_cursor = src.execute(f"SELECT {', '.join(shared_cols)} FROM {table}")
        rows = src_cursor.fetchall()
        
        if not rows:
            print(f"  EMPTY {table} (0 rows)")
            continue
        
        # Clear target table and insert
        tgt.execute(f"DELETE FROM {table}")
        placeholders = ', '.join(['?' for _ in shared_cols])
        cols_str = ', '.join(shared_cols)
        tgt.executemany(f"INSERT OR IGNORE INTO {table} ({cols_str}) VALUES ({placeholders})", rows)
        tgt.commit()
        print(f"  OK {table}: {len(rows)} rows transferred")
        success += 1

    except Exception as e:
        print(f"  ERROR {table}: {e}")
        tgt.rollback()
        errors += 1

tgt.execute("PRAGMA foreign_keys = ON")
tgt.commit()

src.close()
tgt.close()

print(f"\n✅ Done! Transferred: {success} tables | Skipped: {skipped} | Errors: {errors}")
