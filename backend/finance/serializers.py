from rest_framework import serializers
from .models import CategoryCommission, GlobalCommission, LedgerEntry

class GlobalCommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalCommission
        fields = ['id', 'commission_type', 'percentage', 'fixed_amount', 'updated_at']

class CategoryCommissionSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    class Meta:
        model = CategoryCommission
        fields = ['id', 'category', 'category_display', 'commission_type', 'percentage', 'fixed_amount']

class LedgerEntrySerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(source='created_at', format="%d %b %Y")
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = LedgerEntry
        fields = ['id', 'amount', 'entry_type', 'description', 'date', 'is_settled', 'gross_amount', 'commission_amount', 'net_amount', 'order_number']

class VendorEarningsSummarySerializer(serializers.Serializer):
    available_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    uncleared_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    lifetime_earnings = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_orders = serializers.IntegerField()
    pending_payouts = serializers.DecimalField(max_digits=12, decimal_places=2)
    recent_activities = LedgerEntrySerializer(many=True)
    total_gross = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_commission = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_net = serializers.DecimalField(max_digits=12, decimal_places=2)
