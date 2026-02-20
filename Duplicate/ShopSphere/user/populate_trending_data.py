import os
import django
import random
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ShopSphere.settings')
django.setup()

from vendor.models import Product, VendorProfile, ProductImage, Category
from user.models import AuthUser, ProductReview


def populate_trending():
    print("Populating trending products...")
    
    # Get or create a vendor
    vendor_user, _ = AuthUser.objects.get_or_create(
        email="trending@vendor.com",
        defaults={"username": "trending_vendor", "role": "user"}
    )
    if not vendor_user.password:
        vendor_user.set_password("trending123")
        vendor_user.save()
        
    vendor_profile, _ = VendorProfile.objects.get_or_create(
        user=vendor_user,
        defaults={
            "shop_name": "Trending Trends",
            "shop_description": "We sell the most trending items.",
            "address": "123 Trend St",
            "business_type": "retail",
            "approval_status": "approved"
        }
    )
    
    # Get or create a category
    category, _ = Category.objects.get_or_create(
        slug="electronics",
        defaults={"name": "Electronics"}
    )
    
    # Create some trending products
    trending_items = [
        {"name": "Ultra Smart 4K TV", "price": 1200.00, "description": "Crisp visuals for every room."},
        {"name": "Wireless Noise Cancelling Pods", "price": 150.00, "description": "Pure sound, no distractions."},
        {"name": "Next-Gen Gaming Console", "price": 499.00, "description": "Step into the future of gaming."},
    ]
    
    users = AuthUser.objects.filter(role='user')[:5]
    if users.count() < 3:
        # Create some dummy users if needed
        for i in range(3):
            u, _ = AuthUser.objects.get_or_create(
                email=f"user{i}@example.com",
                defaults={"username": f"user{i}"}
            )
            if not u.password:
                u.set_password("pass123")
                u.save()
        users = AuthUser.objects.filter(role='user')[:5]

    for item in trending_items:
        product, created = Product.objects.get_or_create(
            name=item["name"],
            vendor=vendor_profile,
            defaults={
                "description": item["description"],
                "price": Decimal(str(item["price"])),
                "quantity": 100,
                "category": category,
            }
        )
        
        # Add a few images (placeholder/empty) so the loop works
        if product.images.count() < 4:
            for i in range(4):
                ProductImage.objects.create(
                    product=product,
                    image_name=f"trending_{i}.jpg",
                    image_mimetype="image/jpeg",
                    image_data=b"" # Empty binary for testing
                )
        
        # Add high-rated reviews
        for user in users:
            ProductReview.objects.update_or_create(
                product=product,
                user=user,
                defaults={
                    "rating": random.randint(4, 5),
                    "comment": "Mind-blowing product!"
                }
            )
            
    print("Trending products populated successfully!")

if __name__ == "__main__":
    populate_trending()