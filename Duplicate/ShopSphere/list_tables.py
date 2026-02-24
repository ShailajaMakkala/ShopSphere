import sqlite3

def list_tables():
    try:
        conn = sqlite3.connect('d:/final_shopsphere/Duplicate/ShopSphere/db.sqlite3')
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cur.fetchall()
        for t in tables:
            print(t[0])
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    list_tables()
