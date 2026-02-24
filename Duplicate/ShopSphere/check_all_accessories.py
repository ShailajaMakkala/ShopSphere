import sqlite3

def check_all_accessory_products():
    try:
        conn = sqlite3.connect('d:/final_shopsphere/Duplicate/ShopSphere/db.sqlite3')
        cur = conn.cursor()
        
        cur.execute("SELECT id, name, description FROM vendor_product WHERE name LIKE '%accessory%' OR description LIKE '%accessory%'")
        products = cur.fetchall()
        
        for p_id, p_name, p_desc in products:
            print(f"ID: {p_id} | Name: {p_name}")
            cur.execute("PRAGMA table_info(user_review)")
            cols = [c[1] for c in cur.fetchall()]
            p_col = 'product_id' if 'product_id' in cols else 'Product_id'
            
            cur.execute(f"SELECT rating, comment FROM user_review WHERE {p_col} = ?", (p_id,))
            reviews = cur.fetchall()
            for r, c in reviews:
                print(f"  [{r}*] {c}")
                
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_all_accessory_products()
