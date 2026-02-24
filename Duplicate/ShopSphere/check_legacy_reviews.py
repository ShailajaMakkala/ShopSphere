import sqlite3

def check_legacy_reviews():
    try:
        conn = sqlite3.connect('d:/final_shopsphere/Duplicate/ShopSphere/db.sqlite3')
        cur = conn.cursor()
        
        cur.execute("SELECT name FROM sqlite_master WHERE name='user_productreview'")
        if not cur.fetchone():
            print("Table user_productreview does not exist.")
            return

        cur.execute("""
            SELECT p.name, r.comment 
            FROM user_productreview r
            JOIN vendor_product p ON r.product_id = p.id
        """)
        reviews = cur.fetchall()
        print(f"Total legacy reviews: {len(reviews)}")
        for p_name, comment in reviews:
            print(f"Product: {p_name} | Review: {comment}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_legacy_reviews()
