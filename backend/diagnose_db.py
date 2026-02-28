import os
import django
import sys

try:
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    pass

# Append the current directory to sys.path to ensure absolute imports work
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ShopSphere.settings')
django.setup()

from django.contrib.auth import get_user_model
from vendor.models import VendorProfile
from deliveryAgent.models import DeliveryAgentProfile

User = get_user_model()

print("--- Database Stats ---")
print(f"Total Users: {User.objects.count()}")
print(f"  Customers: {User.objects.filter(role='customer').count()}")
print(f"  Vendors  : {User.objects.filter(role='vendor').count()}")
print(f"  Delivery : {User.objects.filter(role='delivery').count()}")
print(f"  Staff    : {User.objects.filter(is_staff=True).count()}")
print(f"  Super    : {User.objects.filter(is_superuser=True).count()}")

print("\n--- Profile Stats ---")
print(f"Total Vendor Profiles : {VendorProfile.objects.count()}")
print(f"Total Delivery Profiles  : {DeliveryAgentProfile.objects.count()}")

# List a few vendors for debugging
print("\n--- Recent Vendors ---")
for v in VendorProfile.objects.all()[:5]:
    print(f"ID: {v.id}, Shop: {v.shop_name}, User: {v.user.email}, Status: {v.approval_status}")

# List a few delivery agents
print("\n--- Recent Delivery Agents ---")
for a in DeliveryAgentProfile.objects.all()[:5]:
    print(f"ID: {a.id}, User: {a.user.email}, Status: {a.approval_status}")
