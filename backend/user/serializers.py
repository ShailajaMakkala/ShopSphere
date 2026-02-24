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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthUser
        fields = ['id', 'username', 'email', 'phone', 'gender', 'role', 'profile_image']
        read_only_fields = ['id', 'email', 'role']

    def validate_phone(self, value):
        if value:
            if not value.isdigit():
                raise serializers.ValidationError("Phone number must contain only digits.")
            if len(value) != 10:
                raise serializers.ValidationError("Phone number must be exactly 10 digits.")
        return value

    def validate_username(self, value):
        import re
        # Allow letters and single spaces between words. No digits, no special chars, no double spaces.
        if not re.match(r'^[a-zA-Z]+( [a-zA-Z]+)*$', value):
            raise serializers.ValidationError("Name should only contain letters and single spaces. No digits or special characters allowed.")
        if len(value) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters long.")
        return value


from django.urls import reverse

class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'uploaded_at']

    def get_image(self, obj):
        request = self.context.get('request')
        path = reverse('serve_product_image', kwargs={'image_id': obj.id})
        if request:
            return request.build_absolute_uri(path)
        return path


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    vendor_name = serializers.CharField(source='vendor.shop_name', read_only=True)
    image = serializers.SerializerMethodField()
    image_urls = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'brand', 'description', 'category', 'price', 
            'quantity', 'images', 'image', 'image_urls', 'status', 
            'is_blocked', 'created_at', 'vendor_name', 'average_rating', 'total_reviews'
        ]

    def get_average_rating(self, obj):
        # Use annotated values if available to avoid N+1 queries
        rating = getattr(obj, 'average_rating', None)
        if rating is None:
            rating = getattr(obj, 'avg_rating', None)
            
        if rating is not None:
            return round(float(rating), 1)
            
        # Fallback to calculation if not annotated (rare)
        from django.db.models import Avg
        avg = obj.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(float(avg or 0.0), 1)


    def get_image(self, obj):
        request = self.context.get('request')
        first_image = obj.images.first()
        if first_image:
            path = reverse('serve_product_image', kwargs={'image_id': first_image.id})
            if request:
                return request.build_absolute_uri(path)
            return path
        return None

    def get_image_urls(self, obj):
        request = self.context.get('request')
        urls = []
        for img in obj.images.all():
            path = reverse('serve_product_image', kwargs={'image_id': img.id})
            if request:
                urls.append(request.build_absolute_uri(path))
            else:
                urls.append(path)
        return urls


class AddressSerializer(serializers.ModelSerializer):
    # Expose address_line1 as 'address' for frontend compatibility
    address = serializers.CharField(source='address_line1', read_only=True)

    class Meta:
        model = Address
        fields = ['id', 'user', 'name', 'phone', 'email', 'address_line1', 'address_line2',
                  'city', 'state', 'pincode', 'country', 'latitude', 'longitude', 'is_default', 'created_at', 'address']
        read_only_fields = ['user']


class OrderItemSerializer(serializers.ModelSerializer):
    product_image = serializers.SerializerMethodField()
    user_review = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'vendor', 'product_name', 'product_price', 'quantity', 'subtotal', 'vendor_status', 'product_image', 'user_review']

    def get_product_image(self, obj):
        request = self.context.get('request')
        if not obj.product:
            return None
            
        first_image = obj.product.images.first()
        if first_image:
            path = reverse('serve_product_image', kwargs={'image_id': first_image.id})
            if request:
                return request.build_absolute_uri(path)
            return path
        return None

    def get_user_review(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated or not obj.product:
            return None
            
        from .models import Review
        from django.utils import timezone
        
        review = Review.objects.filter(user=request.user, Product=obj.product).first()
        if review:
            # Check if it's within 5 days for editing
            time_diff = timezone.now() - review.created_at
            can_edit = time_diff.days < 5
            
            return {
                'id': review.id,
                'rating': review.rating,
                'comment': review.comment,
                'reviewer_name': review.reviewer_name,
                'created_at': review.created_at,
                'can_edit_review': can_edit,
                'pictures': review.pictures.url if review.pictures else None
            }
        return None


class OrderTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import OrderTracking
        model = OrderTracking
        fields = ['status', 'location', 'timestamp', 'notes']
    
    timestamp = serializers.DateTimeField(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    delivery_address = AddressSerializer(read_only=True)
    billing_address = AddressSerializer(read_only=True)
    tracking_history = OrderTrackingSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'payment_method', 'payment_status', 'transaction_id',
                  'subtotal', 'tax_amount', 'shipping_cost', 'total_amount', 
                  'status', 'delivery_address', 'billing_address', 'created_at', 'items', 'tracking_history']


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


        #  WALLET & PAYMENT SERIALIZERS

class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = '__all__'


class UserWalletSerializer(serializers.ModelSerializer):
    transactions = WalletTransactionSerializer(many=True, read_only=True)
    
    class Meta:
        model = UserWallet
        fields = ['id', 'balance', 'total_credited', 'total_debited', 'transactions', 'created_at']


#          RETURN & REFUND SERIALIZERS

class OrderReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderReturn
        fields = '__all__'


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = '__all__'


        #  TWO-FACTOR AUTH SERIALIZER

class TwoFactorAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = TwoFactorAuth
        fields = ['is_enabled', 'method', 'otp_verified_at']
        extra_kwargs = {'secret_key': {'write_only': True}}


        #  NOTIFICATION SERIALIZER

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'message', 'is_read', 'created_at', 'read_at']


        #  DISPUTE SERIALIZER

class DisputeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispute
        fields = '__all__'


        #  COUPON SERIALIZERS

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

    class Meta:
        model = Review
        fields = ['id', 'user', 'username', 'Product', 'product_id', 'reviewer_name', 'rating', 'comment', 'pictures', 'created_at', 'updated_at']
        read_only_fields = ['user', 'Product']

    def get_username(self, obj):
        if obj.user:
            return obj.user.username
        return obj.reviewer_name or "Anonymous"
