import sqlite3

def improve_reviews():
    try:
        conn = sqlite3.connect('d:/final_shopsphere/Duplicate/ShopSphere/db.sqlite3')
        cur = conn.cursor()
        
        # 1. Update "Accessories" review
        cur.execute("UPDATE user_review SET comment = 'High-quality accessories that add a touch of elegance to any outfit. Highly recommended!' WHERE comment = 'gppd'")
        
        # 2. Update "Manual Test" review
        cur.execute("UPDATE user_review SET comment = 'Very comfortable and breathable cotton fabric. Fits perfectly.' WHERE comment = 'Manual Test'")
        
        # 3. Update "bisket" (grocery) review
        cur.execute("UPDATE user_review SET comment = 'Fresh and crunchy biscuits, great with tea!' WHERE comment = 'good' AND reviewer_name = 'Lakshan'")
        
        # 4. Update product name "Accessories" to something better
        cur.execute("UPDATE vendor_product SET name = 'Premium Leather Accessories' WHERE name = 'Accessories'")
        
        conn.commit()
        print("Reviews improved successfully.")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    improve_reviews()
