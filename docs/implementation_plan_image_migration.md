# Implementation Plan - Product Image Migration to Database

This plan outlines the migration of product images from file-based storage (`media` folder) to database-backed storage (`BinaryField`).

## User Review Required

> [!WARNING]
> Storing large amounts of binary data in the database can increase database size and potentially impact performance for very large datasets. However, this approach ensures that images are tightly coupled with their records and simplifies backups/deployments where media storage is not persisted separately.

## Proposed Changes

### Backend Implementation

#### [MODIFY] [vendor/models.py](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/Duplicate/ShopSphere/vendor/models.py)
- Update `ProductImage` model:
    - Add `image_data = models.BinaryField(null=True, blank=True)`
    - Add `image_mimetype = models.CharField(max_length=50, null=True, blank=True)`
    - Add `image_filename = models.CharField(max_length=255, null=True, blank=True)`
    - Deprecate `image` (ImageField) for future removal after migration.

#### [MODIFY] [vendor/api_views.py](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/Duplicate/ShopSphere/vendor/api_views.py)
- Implement `serve_product_image(request, image_id)` view to retrieve and serve binary data.
- Update `ProductViewSet.create` to:
    - Read uploaded files.
    - Save content into `image_data`.
    - Detect and save `image_mimetype`.
- Update `ProductViewSet.update` to handle binary storage.

#### [MODIFY] [vendor/api_urls.py](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/Duplicate/ShopSphere/vendor/api_urls.py)
- Add route for serving product images: `path('product-images/<int:image_id>/', serve_product_image, name='serve_product_image')`.

#### [MODIFY] [vendor/serializers.py](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/Duplicate/ShopSphere/vendor/serializers.py)
- Update `ProductImageSerializer` to return the dynamic URL for `image_data` instead of the file path.
- Update `ProductSerializer` methods (`get_image`, `get_image_urls`) to use the new dynamic URL.

### Migration Script

#### [NEW] [migrate_images_to_db.py](file:///c:/Users/imvis/Desktop/Project-Ecommerce/project-ecommerce/migrate_images_to_db.py)
- A standalone Django script to:
    - Iterate all `ProductImage` objects.
    - Load the image file from the `media` folder.
    - Save the binary content to the database.
    - (Optionally) delete the original file.

## Verification Plan

### Automated Tests
- Script to verify that all `ProductImage` records now have `image_data` populated.
- API tests to ensure `/vendor/api/product-images/<id>/` returns a valid image.

### Manual Verification
- Log in as a vendor.
- Add a product with 4+ images.
- Verify images appear correctly in the product list and detail views.
- Check the `media/products/` folder to ensure no new files are being created.
