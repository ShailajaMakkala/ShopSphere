from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError


class VendorProfile(models.Model):
    """Vendor Profile Model for vendor registration and management"""
    
    BUSINESS_CHOICES = [
        ('retail', 'Retail'),
        ('wholesale', 'Wholesale'),
        ('manufacturer', 'Manufacturer'),
        ('service', 'Service'),
    ]

    ID_PROOF_CHOICES = [
        ('gst', 'GST'),
        ('pan', 'PAN'),
    ]
    
    APPROVAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendor_profile')
    shop_name = models.CharField(max_length=100)
    shop_description = models.TextField()
    address = models.TextField() 
    business_type = models.CharField(max_length=20, choices=BUSINESS_CHOICES)
    
    # Independent Contact Information
    contact_name = models.CharField(max_length=100, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=15, blank=True, null=True)
    
    # Legacy fields
    id_type = models.CharField(max_length=10, choices=ID_PROOF_CHOICES, blank=True, null=True)
    id_number = models.CharField(max_length=50, blank=True, null=True)
    id_proof_file = models.FileField(upload_to='vendor_docs/', blank=True, null=True)
    
    # GST / PAN fields
    gst_number = models.CharField(max_length=15, blank=True, null=True)
    pan_number = models.CharField(max_length=10, blank=True, null=True)
    pan_name = models.CharField(max_length=100, blank=True, null=True)
    pan_card_file = models.FileField(upload_to='pan_cards/', blank=True, null=True)
    
    # Additional documents uploaded during registration
    additional_documents = models.FileField(upload_to='vendor_additional_docs/', blank=True, null=True)
    selfie_with_id = models.ImageField(upload_to='vendor_selfies/', blank=True, null=True)
    
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_blocked = models.BooleanField(default=False)
    blocked_reason = models.TextField(blank=True, null=True)
    
    # Account Deletion Request
    is_deletion_requested = models.BooleanField(default=False)
    deletion_reason = models.TextField(blank=True, null=True)
    deletion_requested_at = models.DateTimeField(null=True, blank=True)
    
    # Bank Details
    bank_holder_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account_number = models.CharField(max_length=20, blank=True, null=True)
    bank_ifsc_code = models.CharField(max_length=11, blank=True, null=True)
    
    # Shipping Preferences
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.shop_name} ({self.user.username})"
    
    @property
    def is_approved(self):
        return self.approval_status == 'approved'


# ===============================================
#               PRODUCT MODEL
# ===============================================

class Product(models.Model):
    """Product Model for vendor products"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('fashion', 'Fashion'),
        ('home_kitchen', 'Home & Kitchen'),
        ('beauty_personal_care', 'Beauty & Personal Care'),
        ('sports_fitness', 'Sports & Fitness'),
        ('toys_games', 'Toys & Games'),
        ('automotive', 'Automotive'),
        ('grocery', 'Grocery'),
        ('books', 'Books'),
        ('services', 'Services'),
        ('other', 'Other'),
    ]

    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='products')
    brand = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    search_count = models.IntegerField(default=0, db_index=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_reviews = models.IntegerField(default=0)
    is_blocked = models.BooleanField(default=False)
    blocked_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.vendor.shop_name}"

    def clean(self):
        # Enforce minimum 4 images
        if self.pk and self.images.count() < 4:
            raise ValidationError("Product must have at least 4 images.")


# ===============================================
#          PRODUCT IMAGE MODEL (NEW)
# ===============================================

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image_data = models.BinaryField(null=True, blank=True)
    image_mimetype = models.CharField(max_length=50, null=True, blank=True)
    image_filename = models.CharField(max_length=255, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"