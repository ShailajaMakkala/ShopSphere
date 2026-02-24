import sqlite3

def check_mismatched_reviews():
    try:
        conn = sqlite3.connect('d:/final_shopsphere/Duplicate/ShopSphere/db.sqlite3')
        cur = conn.cursor()
        
        # Get category of all products
        cur.execute("SELECT id, name, category FROM vendor_product")
        products = {p[0]: {'name': p[1], 'category': p[2]} for p in products_all} if (products_all := cur.fetchall()) else {}
        
        # Check reviews
        cur.execute("PRAGMA table_info(user_review)")
        cols = [c[1] for c in cur.fetchall()]
        p_col = 'product_id' if 'product_id' in cols else 'Product_id'
        
        cur.execute(f"SELECT {p_col}, comment, reviewer_name FROM user_review")
        reviews = cur.fetchall()
        
        print(f"Total reviews in DB: {len(reviews)}")
        
        # Suspicious keywords that might mismatch categories
        suspicious = ['laptop', 'phone', 'shoe', 'cookie', 'food', 'book', 'toy', 'car']
        
        mismatches = []
        for p_id, comment, reviewer in reviews:
            if p_id not in products: continue
            
            p = products[p_id]
            comment_lower = comment.lower()
            
            # Simple check: if product is fashion but comment mentions laptop/car/food
            if p['category'] == 'fashion':
                if any(k in comment_lower for k in ['laptop', 'phone', 'battery', 'screen', 'cpu']):
                    mismatches.append((p['name'], comment, reviewer))
            
            # If product is electronics but comment mentions "delicious" or "fit"
            if p['category'] == 'electronics':
                if any(k in comment_lower for k in ['delicious', 'tasty', 'yummy', 'fit', 'size']):
                    mismatches.append((p['name'], comment, reviewer))

        if mismatches:
            print(f"Found {len(mismatches)} potentially irrelevant reviews:")
            for p_name, comment, reviewer in mismatches:
                print(f"  Product: {p_name} | Review: {comment} | By: {reviewer}")
        else:
            print("No obvious mismatches found based on simple keyword search.")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_mismatched_reviews()
