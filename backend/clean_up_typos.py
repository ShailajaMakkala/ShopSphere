import sqlite3

def clean_up_typos():
    try:
        conn = sqlite3.connect('d:/final_shopsphere/Duplicate/ShopSphere/db.sqlite3')
        cur = conn.cursor()
        
        # Fix typo in product name
        cur.execute("UPDATE vendor_product SET name = 'Chocolate Digestive Biscuits' WHERE name = 'bisket'")
        
        # Improve generic "Good" review for headphones
        cur.execute("UPDATE user_review SET comment = 'Excellent sound quality and long battery life. The noise cancellation is impressive.' WHERE comment = 'Good' AND reviewer_name = 'Balaji'")
        
        # Improve "average" review for books
        cur.execute("UPDATE user_review SET comment = 'The book content is great, but the binding quality could be better.' WHERE comment = 'average' AND reviewer_name = 'Madhu'")

        conn.commit()
        print("Typos fixed and reviews improved.")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    clean_up_typos()
