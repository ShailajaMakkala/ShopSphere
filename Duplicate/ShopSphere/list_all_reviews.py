import sqlite3

def list_all_reviews():
    try:
        conn = sqlite3.connect('d:/final_shopsphere/Duplicate/ShopSphere/db.sqlite3')
        cur = conn.cursor()
        
        cur.execute("PRAGMA table_info(user_review)")
        cols = [c[1] for c in cur.fetchall()]
        p_col = 'product_id' if 'product_id' in cols else 'Product_id'
        
        cur.execute(f"""
            SELECT p.name, p.category, r.comment, r.reviewer_name 
            FROM user_review r
            JOIN vendor_product p ON r.{p_col} = p.id
        """)
        reviews = cur.fetchall()
        
        for p_name, cat, comment, reviewer in reviews:
            print(f"Product: {p_name} ({cat}) | Review: {comment} | By: {reviewer}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    list_all_reviews()
