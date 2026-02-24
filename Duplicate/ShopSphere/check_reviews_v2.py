import sqlite3

def check_all_reviews_for_product_5():
    try:
        conn = sqlite3.connect('d:/final_shopsphere/Duplicate/ShopSphere/db.sqlite3')
        cur = conn.cursor()
        
        cur.execute("SELECT id, name, description FROM vendor_product WHERE id = 5")
        product = cur.fetchone()
        
        if product:
            print(f"Product: {product[1]} (ID: {product[0]})")
            print(f"Description: {product[2]}")
            
            # Check both columns as the table might have mismatch
            cur.execute("PRAGMA table_info(user_review)")
            cols = [c[1] for c in cur.fetchall()]
            
            p_col = 'product_id' if 'product_id' in cols else 'Product_id'
            
            cur.execute(f"SELECT rating, comment, reviewer_name FROM user_review WHERE {p_col} = 5")
            reviews = cur.fetchall()
            
            print(f"Total reviews: {len(reviews)}")
            for r, c, name in reviews:
                print(f"  [{r}*] By {name}: {c}")
        else:
            print("Product ID 5 not found.")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_all_reviews_for_product_5()
