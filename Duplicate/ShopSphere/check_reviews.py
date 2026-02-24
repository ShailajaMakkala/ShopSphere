import sqlite3

def check_accessories_reviews():
    try:
        conn = sqlite3.connect('d:/final_shopsphere/Duplicate/ShopSphere/db.sqlite3')
        cur = conn.cursor()
        
        # Search for products that might be "accessories"
        cur.execute("SELECT id, name, description FROM vendor_product WHERE name LIKE '%accessory%' OR name LIKE '%accessories%' OR name LIKE '%bag%' OR name LIKE '%watch%' OR name LIKE '%belt%'")
        products = cur.fetchall()
        
        if not products:
            print("No accessory-like products found.")
            return

        print(f"Checking reviews for {len(products)} products:")
        for p_id, p_name, p_desc in products:
            print(f"\nProduct: {p_name} (ID: {p_id})")
            cur.execute("SELECT rating, comment FROM user_review WHERE product_id = ?", (p_id,))
            # Try both product_id and Product_id as seen in the insert script
            reviews = cur.fetchall()
            if not reviews:
                cur.execute("SELECT rating, comment FROM user_review WHERE Product_id = ?", (p_id,))
                reviews = cur.fetchall()
            
            if not reviews:
                print("  No reviews found.")
            else:
                for rating, comment in reviews:
                    print(f"  [{rating}*] {comment}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_accessories_reviews()
