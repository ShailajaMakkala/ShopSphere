from django.contrib import admin
from .models import CategoryCommission, LedgerEntry, Payout, GlobalCommission

@admin.register(CategoryCommission)
class CategoryCommissionAdmin(admin.ModelAdmin):
    list_display = ('category', 'commission_type', 'percentage', 'fixed_amount', 'updated_at')

@admin.register(GlobalCommission)
class GlobalCommissionAdmin(admin.ModelAdmin):
    list_display = ('commission_type', 'percentage', 'fixed_amount', 'updated_at')

@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'entry_type', 'amount', 'is_settled', 'settlement_date', 'created_at')
    list_filter = ('entry_type', 'is_settled', 'vendor')
    readonly_fields = ('created_at',)

@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'amount', 'status', 'created_at', 'processed_at')
    list_filter = ('status',)
