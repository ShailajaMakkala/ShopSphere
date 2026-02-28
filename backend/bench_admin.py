import os
import django
import dotenv
import time
from django.db.models import Prefetch

dotenv.load_dotenv(r'd:\ShopSphere_Deployed\ShopSphere\backend\.env')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ShopSphere.settings')
django.setup()

from vendor.models import Product, ProductImage

# Test current (slow) prefetch
start = time.time()
qs_slow = Product.objects.select_related('vendor').prefetch_related('images').all()
count_slow = len(list(qs_slow))
end = time.time()
print(f"Slow fetch: {count_slow} products in {end - start:.2f} seconds")

# Test optimized prefetch
start = time.time()
images_prefetch = Prefetch('images', queryset=ProductImage.objects.defer('image_data'))
qs_fast = Product.objects.select_related('vendor').prefetch_related(images_prefetch).all()
count_fast = len(list(qs_fast))
end = time.time()
print(f"Fast fetch: {count_fast} products in {end - start:.2f} seconds")
