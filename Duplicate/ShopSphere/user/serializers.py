from rest_framework import serializers
from .models import (AuthUser, Cart, CartItem, Order, OrderItem, Address, 
                     UserWallet, WalletTransaction, OrderReturn, Refund, 
                     TwoFactorAuth, Notification, Dispute, Coupon, CouponUsage, Review)
from vendor.models import Product, ProductImage


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = AuthUser.objects.create_user(**validated_data)
        return user


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'uploaded_at']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    vendor_name = serializers.CharField(source='vendor.shop_name', read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'price', 
            'quantity', 'images', 'status', 'is_blocked', 'created_at', 
            'vendor_name', 'average_rating', 'review_count'
        ]

    def get_average_rating(self, obj):
        from django.db.models import Avg
        from .models import Review
        avg = Review.objects.filter(Product=obj).aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0

    def get_review_count(self, obj):
        from .models import Review
        return Review.objects.filter(Product=obj).count()



class AddressSerializer(serializers.ModelSerializer):
    # Expose address_line1 as 'address' for frontend compatibility
    address = serializers.CharField(source='address_line1', read_only=True)

    class Meta:
        model = Address
        fields = ['id', 'user', 'name', 'phone', 'email', 'address_line1', 'address_line2',
                  'city', 'state', 'pincode', 'country', 'is_default', 'created_at', 'address']
        read_only_fields = ['user']


class OrderItemSerializer(serializers.ModelSerializer):
    user_review = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'vendor', 'product_name', 'product_price', 'quantity', 'subtotal', 'vendor_status', 'user_review']

    def get_product(self, obj):
        if obj.product_id:
            return obj.product_id
        # Fallback: Fix on the fly if product is missing but name exists
        from vendor.models import Product
        p = Product.objects.filter(name=obj.product_name).first()
        if p:
            # Optionally update the object to avoid future lookups
            obj.product = p
            obj.save()
            return p.id
        return None

    def get_user_review(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
            
        product_id = obj.product_id
        if not product_id:
            from vendor.models import Product
            p = Product.objects.filter(name=obj.product_name).first()
            product_id = p.id if p else None
            
        if product_id:
            from .models import Review
            review = Review.objects.filter(user=request.user, Product_id=product_id).first()
            if review:
                return ReviewSerializer(review, context=self.context).data
        return None


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'payment_method', 'payment_status', 'total_amount', 
                  'status', 'delivery_address', 'created_at', 'items']


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.get_total()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_cart_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_cart_price']

    def get_total_cart_price(self, obj):
        return obj.get_total()


# ===============================================
#          WALLET & PAYMENT SERIALIZERS
# ===============================================

class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = '__all__'


class UserWalletSerializer(serializers.ModelSerializer):
    transactions = WalletTransactionSerializer(many=True, read_only=True)
    
    class Meta:
        model = UserWallet
        fields = ['id', 'balance', 'total_credited', 'total_debited', 'transactions', 'created_at']


# ===============================================
#          RETURN & REFUND SERIALIZERS
# ===============================================

class OrderReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderReturn
        fields = '__all__'


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = '__all__'


# ===============================================
#          TWO-FACTOR AUTH SERIALIZER
# ===============================================

class TwoFactorAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwoFactorAuth
        fields = ['is_enabled', 'method', 'otp_verified_at']
        extra_kwargs = {'secret_key': {'write_only': True}}


# ===============================================
#          NOTIFICATION SERIALIZER
# ===============================================

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'message', 'is_read', 'created_at', 'read_at']


# ===============================================
#          DISPUTE SERIALIZER
# ===============================================

class DisputeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispute
        fields = '__all__'


# ===============================================
#          COUPON SERIALIZERS
# ===============================================

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'coupon_type', 'discount_value', 'min_purchase_amount',
                  'valid_from', 'valid_till', 'is_active']


class CouponUsageSerializer(serializers.ModelSerializer):
    coupon = CouponSerializer(read_only=True)
    
    class Meta:
        model = CouponUsage
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    product_id = serializers.IntegerField(source='Product.id', read_only=True)
    can_edit_review = serializers.SerializerMethodField()
    days_left = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['id', 'user', 'username', 'Product', 'product_id', 'reviewer_name', 'rating', 'comment', 'pictures', 'created_at', 'can_edit_review', 'days_left']
        read_only_fields = ['user', 'Product']

    def get_username(self, obj):
        if obj.user:
            return obj.user.username
        return obj.reviewer_name or "Anonymous"

    def get_can_edit_review(self, obj):
        from django.utils import timezone
        from django.conf import settings
        now = timezone.now()
        
        # If USE_TZ is False, timezone.now() might still be aware if not configured otherwise.
        # Ensure comparison is safe.
        if not settings.USE_TZ and timezone.is_aware(now):
            now = timezone.make_naive(now)
            
        created_at = obj.created_at
        if timezone.is_aware(created_at):
            created_at = timezone.make_naive(created_at)
            
        time_diff = now - created_at
        return time_diff.days < 5

    def get_days_left(self, obj):
        from django.utils import timezone
        from django.conf import settings
        now = timezone.now()
        
        if not settings.USE_TZ and timezone.is_aware(now):
            now = timezone.make_naive(now)
            
        created_at = obj.created_at
        if timezone.is_aware(created_at):
            created_at = timezone.make_naive(created_at)
            
        time_diff = now - created_at
        left = 5 - time_diff.days
        return max(0, left)

