import sqlite3

def check_product_images(p_id):
    try:
        conn = sqlite3.connect('d:/final_shopsphere/Duplicate/ShopSphere/db.sqlite3')
        cur = conn.cursor()
        
        cur.execute("SELECT image_filename FROM vendor_productimage WHERE product_id = ?", (p_id,))
        images = cur.fetchall()
        print(f"Images for product {p_id}:")
        for img in images:
            print(f"  {img[0]}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_product_images(5)
