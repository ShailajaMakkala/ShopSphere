from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

class CategoryCommission(models.Model):
    """
    Global commission settings per category.
    """
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

    COMMISSION_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed'),
        ('hybrid', 'Hybrid'),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, unique=True)
    commission_type = models.CharField(max_length=20, choices=COMMISSION_TYPES, default='percentage')
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00) # e.g. 10.00 for 10%
    fixed_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_category_display()} - {self.commission_type}"


class GlobalCommission(models.Model):
    """
    System-wide default commission settings.
    """
    COMMISSION_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed'),
    ]

    commission_type = models.CharField(max_length=20, choices=COMMISSION_TYPES, default='percentage')
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    fixed_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Global Commission"

    def __str__(self):
        return f"Global Commission: {self.percentage if self.commission_type == 'percentage' else self.fixed_amount}"


class LedgerEntry(models.Model):
    """
    Double-entry inspired ledger. 
    Tracks every movement of money. 
    Immutable: entries should never be updated, only reversed by new entries.
    """
    ENTRY_TYPES = [
        ('REVENUE', 'Order Revenue'),
        ('COMMISSION', 'Platform Commission'),
        ('REFUND', 'Customer Refund'),
        ('PAYOUT', 'Vendor Payout'),
        ('CANCELLATION', 'Order Cancellation'),
    ]

    vendor = models.ForeignKey('vendor.VendorProfile', on_delete=models.CASCADE, related_name='finance_ledger_entries')
    order = models.ForeignKey('user.Order', on_delete=models.SET_NULL, null=True, blank=True)
    order_item = models.ForeignKey('user.OrderItem', on_delete=models.SET_NULL, null=True, blank=True)
    
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0) # Kept for Payouts/General
    
    # Unified Order Entry Fields
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    commission_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES)
    description = models.TextField(blank=True)
    
    # Settlement logic
    is_settled = models.BooleanField(default=False)
    settlement_date = models.DateTimeField(null=True, blank=True) # When funds become available (T+7)
    
    # Audit and Idempotency
    reference_id = models.CharField(max_length=100, unique=True) # For preventing duplicate entries
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['vendor', 'is_settled']),
            models.Index(fields=['settlement_date']),
            models.Index(fields=['reference_id']),
        ]

    def __str__(self):
        return f"{self.vendor.shop_name} - {self.entry_type} - {self.amount}"


class Payout(models.Model):
    """
    Tracks payout executions to vendors.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    vendor = models.ForeignKey('vendor.VendorProfile', on_delete=models.CASCADE, related_name='payout_history')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    bank_details_snapshot = models.JSONField(help_text="Snapshot of bank details at time of payout")
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payout {self.id} for {self.vendor.shop_name}"
