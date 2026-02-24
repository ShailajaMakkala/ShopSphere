import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ShopSphere.settings')
# Add the project directory to sys.path
import sys
sys.path.append(r'd:\e-commerce\Duplicate\ShopSphere')
django.setup()

from vendor.models import VendorProfile

vendors = VendorProfile.objects.all()
print(f"Total Vendors: {vendors.count()}")
for v in vendors:
    print(f"ID: {v.id}, Shop: {v.shop_name}, Email: {v.user.email}, Status: {v.approval_status}, Blocked: {v.is_blocked}")
