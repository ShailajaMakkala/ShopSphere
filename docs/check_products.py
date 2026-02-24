"""
check_products.py - Quick check of products in the DB
"""
import os, sys, django

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Duplicate', 'ShopSphere')
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ShopSphere.settings')
django.setup()

from vendor.models import Product

lines = ["ID | Name | Category | Brand | Images", "-" * 70]
for p in Product.objects.all():
    lines.append(f"{p.id} | {p.name[:30]} | {p.category} | {p.brand} | {p.images.count()}")

with open("product_report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Written to product_report.txt")
