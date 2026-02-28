import psycopg2
import os

env_path = r"d:\ShopSphere_Deployed\ShopSphere\backend\.env"
database_url = None
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('DATABASE_URL='):
                database_url = line.split('=', 1)[1].strip().strip('"').strip("'")

if not database_url:
    database_url = "postgresql://neondb_owner:npg_oYXqCt4J7bOZ@ep-lucky-snow-aijl7u7m-pooler.c-4.us-east-1.aws.neon.tech/ShopSphere_database?sslmode=require&channel_binding=require"

print(f"Connecting to: {database_url}")
try:
    conn = psycopg2.connect(database_url)
    cur = conn.cursor()
    
    print("\n--- VENDORS (vendor_vendorprofile) ---")
    cur.execute('SELECT id, shop_name, approval_status, is_blocked FROM "vendor_vendorprofile"')
    vendors = cur.fetchall()
    for v in vendors:
        print(f"ID: {v[0]}, Shop: {v[1]}, Status: {v[2]}, Blocked: {v[3]}")
    
    print("\n--- DELIVERY AGENTS (deliveryAgent_deliveryagentprofile) ---")
    cur.execute('SELECT id, phone_number, approval_status, is_blocked FROM "deliveryAgent_deliveryagentprofile"')
    agents = cur.fetchall()
    for a in agents:
        print(f"ID: {a[0]}, Phone: {a[1]}, Status: {a[2]}, Blocked: {a[3]}")
        
    print("\n--- USERS (user_user) ---")
    cur.execute('SELECT id, email, username, role, is_staff, is_superuser FROM "user_user"')
    users = cur.fetchall()
    for u in users:
        print(f"ID: {u[0]}, Email: {u[1]}, Role: {u[3]}, Staff: {u[4]}, Super: {u[5]}")

    cur.close()
    conn.close()
except Exception as e:
    print(f"Connection error: {e}")
