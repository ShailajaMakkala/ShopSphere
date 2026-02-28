import os
import django
import dotenv
import time
from django.db.models import Avg, Count

dotenv.load_dotenv(r'd:\ShopSphere_Deployed\ShopSphere\backend\.env')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ShopSphere.settings')
django.setup()

from vendor.models import Product

start = time.time()
products_qs = Product.objects.filter(
    status__in=['active', 'approved'],
    is_blocked=False
).select_related('vendor').prefetch_related('images').annotate(
    avg_rating=Avg('reviews__rating'),
    count_reviews=Count('reviews')
).order_by('-id')

product_list = list(products_qs)
end = time.time()

print(f"Fetched {len(product_list)} products in {end - start:.2f} seconds")

for p in product_list:
    print(f"Product: {p.name}, Images: {p.images.count()}")
