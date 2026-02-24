import os
import django
import sys

# Setup Django
sys.path.append(r'c:\Users\sdash\OneDrive\Desktop\Ecommerce\project-ecommerce\Duplicate\ShopSphere')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ShopSphere.settings')
django.setup()

from vendor.models import Product, ProductImage
from django.core.files import File

def update_products():
    print("Starting product update...")
    
    # Base paths
    PUBLIC_DIR = r'c:\Users\sdash\OneDrive\Desktop\Ecommerce\project-ecommerce\ShopSphere_Frontend\ShopSphere_Frontend\public'
    BOOKS_DIR = os.path.join(PUBLIC_DIR, 'Books')
    ACCESSORIES_DIR = os.path.join(PUBLIC_DIR, 'Accessories')
    GROCERY_DIR = os.path.join(PUBLIC_DIR, 'home and grocery')

    # Image maps
    book_images = [os.path.join(BOOKS_DIR, f"{i}.jpg") for i in range(1, 11)]
    sunglass_images = [
        os.path.join(ACCESSORIES_DIR, "sunglasses1.jpg"),
        os.path.join(ACCESSORIES_DIR, "Sunglasses2.png"),
        os.path.join(ACCESSORIES_DIR, "sunglasses3.png"),
        os.path.join(ACCESSORIES_DIR, "sunglasses 4.png")
    ]
    biscuit_images = [
        os.path.join(GROCERY_DIR, "image.png"),
        os.path.join(GROCERY_DIR, "image copy.png"),
        os.path.join(GROCERY_DIR, "image copy 2.png"),
        os.path.join(GROCERY_DIR, "image copy 3.png")
    ]

    products = Product.objects.all()
    for p in products:
        name_lower = p.name.lower()
        category = p.category
        
        # ── Assign Brands ───────────────────────────
        if not p.brand:
            if category == 'electronics':
                p.brand = "ShopSphere Elite"
            elif category == 'fashion':
                p.brand = "TrendSetter"
            elif category == 'home_kitchen':
                p.brand = "HomeGlow"
            elif category == 'grocery':
                p.brand = "FreshChoice"
            elif category == 'books':
                p.brand = "ScholarPress"
            else:
                p.brand = "ShopSphere"
            
            p.save()
            print(f"Assigned brand to {p.name}: {p.brand}")

        # ── Fix Images ──────────────────────────────
        images_to_add = []
        if 'book' in name_lower or category == 'books':
            images_to_add = book_images[:4]
            print(f"Found book: {p.name}. Updating images...")
        elif 'sunglass' in name_lower:
            images_to_add = sunglass_images
            print(f"Found sunglasses: {p.name}. Updating images...")
        elif 'bisket' in name_lower or 'biscuit' in name_lower or 'parle' in name_lower:
            images_to_add = biscuit_images
            print(f"Found biscuit: {p.name}. Updating images...")
        
        if images_to_add:
            # Clear existing images
            p.images.all().delete()
            
            for img_path in images_to_add:
                if os.path.exists(img_path):
                    with open(img_path, 'rb') as f:
                        content = f.read()
                        ext = os.path.splitext(img_path)[1][1:].lower()
                        mimetype = f"image/{ext}"
                        if ext == 'png': mimetype = 'image/png'
                        elif ext in ['jpg', 'jpeg']: mimetype = 'image/jpeg'
                        
                        ProductImage.objects.create(
                            product=p,
                            image_data=content,
                            image_mimetype=mimetype,
                            image_filename=os.path.basename(img_path)
                        )
            print(f"Updated images for {p.name}")

if __name__ == "__main__":
    update_products()
