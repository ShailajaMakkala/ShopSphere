"""
populate_data.py - Set brands and populate images for all products
Maps products to SPECIFIC relevant images from the public folder
"""
import os, sys, mimetypes, django

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Duplicate', 'ShopSphere')
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ShopSphere.settings')
django.setup()

from vendor.models import Product, ProductImage

PUBLIC = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      'ShopSphere_Frontend', 'ShopSphere_Frontend', 'public')

def p(*parts):
    return os.path.join(PUBLIC, *parts)

# ── Per-product image lists (by keyword in product name) ─────────────────────
NAME_IMAGES = {
    'biscuit':         [p('home and grocery','image.png'), p('home and grocery','image copy 2.png'), p('home and grocery','image copy 3.png'), p('home and grocery','image copy.png')],
    'bisket':          [p('home and grocery','image.png'), p('home and grocery','image copy 2.png'), p('home and grocery','image copy 3.png'), p('home and grocery','image copy.png')],
    'headphones':      [p('Wireless Bluetooth Headphones 1.png'), p('Wireless Bluetooth Headphones 2.jpg'), p('Wireless Bluetooth Headphones 3.jpg'), p('Wireless Bluetooth Headphones 4.jpg')],
    'pods':            [p('buds.jpg'), p('Wireless Bluetooth Headphones 2.jpg'), p('Wireless Bluetooth Headphones 3.jpg'), p('Wireless Bluetooth Headphones 4.jpg')],
    'gaming console':  [p('computer.jpg'), p('keyboard.jpg'), p('mouse.jpg'), p('tv.jpg')],
    'console':         [p('computer.jpg'), p('keyboard.jpg'), p('mouse.jpg'), p('tv.jpg')],
    '4k tv':           [p('tv.jpg'), p('remote.jpg'), p('computer.jpg'), p('laptop.jpg')],
    'tv':              [p('tv.jpg'), p('remote.jpg'), p('computer.jpg'), p('laptop.jpg')],
    'sunglasses':      [p('Accessories','sunglasses1.jpg'), p('Accessories','Sunglasses2.png'), p('Accessories','sunglasses3.png'), p('Accessories','sunglasses 4.png')],
    'tennis':          [p('Sports','tennis1.jpg'), p('Sports','tennis2.png'), p('Sports','tennis3.png'), p('Sports','tennis4 (2).png')],
    'football':        [p('Sports','football1.jpg'), p('Sports','football2.png'), p('Sports','football3.png'), p('Sports','football4.png')],
    'sports kit':      [p('Sports','1.jpg'), p('Sports','2.jpg'), p('Sports','3.jpg'), p('Sports','4.jpg')],
    'kit':             [p('Sports','1.jpg'), p('Sports','2.jpg'), p('Sports','3.jpg'), p('Sports','4.jpg')],
    'accessories':     [p('Accessories','1.jpg'), p('Accessories','2.jpg'), p('Accessories','3.jpg'), p('Accessories','4.jpg')],
    'books':           [p('Books','1.jpg'), p('Books','2.jpg'), p('Books','3.jpg'), p('Books','4.jpg')],
    'book':            [p('Books','1.jpg'), p('Books','2.jpg'), p('Books','3.jpg'), p('Books','4.jpg')],
    't-shirt':         [p('Men\'s Casual Cotton T-Shirt 1.jpg'), p('Men\'s Casual Cotton T-Shirt 2.jpg'), p('Men\'s Casual Cotton T-Shirt 3.jpg'), p('Men\'s Casual Cotton T-Shirt 4.jpg')],
    'shirt':           [p('Men\'s Casual Cotton T-Shirt 1.jpg'), p('Men\'s Casual Cotton T-Shirt 2.jpg'), p('Men\'s Casual Cotton T-Shirt 3.jpg'), p('Men\'s Casual Cotton T-Shirt 4.jpg')],
    'fashion':         [p('Fashion','1.jpg'), p('Fashion','2.jpg'), p('Fashion','3.jpg'), p('Fashion','4.jpg')],
    'laptop':          [p('laptop.jpg'), p('keyboard.jpg'), p('mouse.jpg'), p('computer.jpg')],
    'keyboard':        [p('keyboard.jpg'), p('mouse.jpg'), p('laptop.jpg'), p('computer.jpg')],
}

# Category fallback
CATEGORY_IMAGES = {
    'electronics':          [p('laptop.jpg'), p('keyboard.jpg'), p('mouse.jpg'), p('computer.jpg')],
    'fashion':              [p('Fashion','1.jpg'), p('Fashion','2.jpg'), p('Fashion','3.jpg'), p('Fashion','4.jpg')],
    'sports_fitness':       [p('Sports','tennis1.jpg'), p('Sports','tennis2.png'), p('Sports','tennis3.png'), p('Sports','tennis4 (2).png')],
    'books':                [p('Books','1.jpg'), p('Books','2.jpg'), p('Books','3.jpg'), p('Books','4.jpg')],
    'home_kitchen':         [p('home and grocery','image.png'), p('home and grocery','image copy 2.png'), p('home and grocery','image copy 3.png'), p('home and grocery','image copy.png')],
    'grocery':              [p('home and grocery','image.png'), p('home and grocery','image copy 2.png'), p('home and grocery','image copy 3.png'), p('home and grocery','image copy.png')],
    'beauty_personal_care': [p('Accessories','sunglasses1.jpg'), p('Accessories','1.jpg'), p('Accessories','2.jpg'), p('Accessories','3.jpg')],
    'toys_games':           [p('Sports','football1.jpg'), p('Sports','football2.png'), p('Sports','5.jpg'), p('Sports','6.jpg')],
    'automotive':           [p('charger.jpg'), p('remote.jpg'), p('phone.jpg'), p('buds.jpg')],
    'services':             [p('watch.jpg'), p('tv.jpg'), p('buds.jpg'), p('phone.jpg')],
    'other':                [p('Accessories','1.jpg'), p('Accessories','2.jpg'), p('Accessories','3.jpg'), p('Accessories','4.jpg')],
}

CATEGORY_BRANDS = {
    'electronics':          'TechNova',
    'fashion':              'UrbanThread',
    'sports_fitness':       'ActivePulse',
    'books':                'PageTurner',
    'home_kitchen':         'HomeEssentials',
    'grocery':              'FreshMart',
    'beauty_personal_care': 'GlowUp',
    'toys_games':           'PlayWorld',
    'automotive':           'DrivePro',
    'services':             'ShopSphere',
    'other':                'ShopSphere',
}

def get_images_for_product(product):
    name_lower = product.name.lower()
    for keyword, imgs in NAME_IMAGES.items():
        if keyword in name_lower:
            return imgs
    return CATEGORY_IMAGES.get((product.category or 'other').lower(),
                                [p('laptop.jpg'), p('keyboard.jpg'), p('mouse.jpg'), p('computer.jpg')])

def read_image(path):
    if not os.path.exists(path):
        print(f"  MISSING: {path}")
        return None
    mime, _ = mimetypes.guess_type(path)
    if not mime:
        mime = 'image/jpeg'
    with open(path, 'rb') as f:
        data = f.read()
    return data, mime, os.path.basename(path)

def populate():
    products = list(Product.objects.all())
    print(f"Updating {len(products)} products...\n")

    for product in products:
        cat = (product.category or 'other').lower()

        # Always set brand
        brand = CATEGORY_BRANDS.get(cat, 'ShopSphere')
        product.brand = brand
        product.save(update_fields=['brand'])
        print(f"  Brand set: [{product.id}] {product.name[:30]} -> {brand}")

        # Delete all existing images and repopulate with correct ones
        old_count = product.images.count()
        product.images.all().delete()
        print(f"    Deleted {old_count} old images")

        image_paths = get_images_for_product(product)
        added = 0
        for path in image_paths[:4]:
            result = read_image(path)
            if result is None:
                continue
            data, mime, filename = result
            ProductImage.objects.create(
                product=product,
                image_data=bytes(data),
                image_mimetype=mime,
                image_filename=filename,
            )
            added += 1
        print(f"    Added {added} images from: {[os.path.basename(ip) for ip in image_paths[:4]]}")

    print(f"\nDone! All {len(products)} products updated.")

if __name__ == '__main__':
    populate()
