import sqlite3

def find_accessory_mentions():
    try:
        conn = sqlite3.connect('d:/final_shopsphere/Duplicate/ShopSphere/db.sqlite3')
        cur = conn.cursor()
        
        cur.execute("SELECT id, name FROM vendor_product")
        products = {p[0]: p[1] for p in cur.fetchall()}
        
        cur.execute("PRAGMA table_info(user_review)")
        cols = [c[1] for c in cur.fetchall()]
        p_col = 'product_id' if 'product_id' in cols else 'Product_id'
        
        cur.execute(f"SELECT {p_col}, comment FROM user_review")
        reviews = cur.fetchall()
        
        for p_id, comment in reviews:
            if 'accessor' in comment.lower():
                p_name = products.get(p_id, "Unknown")
                print(f"Product: {p_name} | Review: {comment}")
                
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    find_accessory_mentions()
