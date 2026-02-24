from rest_framework import serializers
from django.urls import reverse
from django.contrib.auth import get_user_model
from user.models import OrderItem
from .models import VendorProfile, Product, ProductImage

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for login"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class VendorProfileSerializer(serializers.ModelSerializer):
    """Serializer for VendorProfile model"""
    user = UserSerializer(read_only=True)
    approval_status_display = serializers.CharField(source='get_approval_status_display', read_only=True)
    business_type_display = serializers.CharField(source='get_business_type_display', read_only=True)
    id_type_display = serializers.CharField(source='get_id_type_display', read_only=True)
    
    class Meta:
        model = VendorProfile
        fields = [
            'id', 'user', 'shop_name', 'shop_description', 'address',
            'contact_name', 'contact_email', 'contact_phone',
            'business_type', 'business_type_display', 'id_type', 'id_type_display',
            'id_number', 'id_proof_file', 'approval_status', 'approval_status_display',
            'rejection_reason', 'is_blocked', 'blocked_reason',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'approval_status', 'rejection_reason',
            'is_blocked', 'blocked_reason', 'created_at', 'updated_at'
        ]


class VendorRegistrationSerializer(serializers.Serializer):
    """Serializer for vendor shop details submission"""
    shop_name = serializers.CharField(max_length=100)
    shop_description = serializers.CharField()
    address = serializers.CharField()
    business_type = serializers.ChoiceField(choices=['retail', 'wholesale', 'manufacturer', 'service'])
    id_type = serializers.ChoiceField(choices=['gst', 'pan'])
    id_number = serializers.CharField(max_length=50)
    id_proof_file = serializers.FileField()




class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for ProductImage model"""
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'url', 'uploaded_at']

    def get_url(self, obj):
        request = self.context.get('request')
        # Use our new serve_product_image endpoint
        # The URL structure is /vendor/api/product-images/<id>/
        # But we can use reverse for robustness
        path = reverse('serve_product_image', kwargs={'image_id': obj.id})
        if request:
            return request.build_absolute_uri(path)
        return path


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    vendor_name = serializers.CharField(source='vendor.shop_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()
    image_urls = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'vendor', 'vendor_name', 'name', 'brand', 'description', 'category', 
            'category_display', 'price', 'quantity', 'images', 'image', 'image_urls', 'status', 
            'status_display', 'is_blocked', 'blocked_reason', 'created_at', 'updated_at'
        ]

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
        read_only_fields = [
            'id', 'vendor', 'is_blocked', 'blocked_reason', 'created_at', 'updated_at'
        ]


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating products"""
    class Meta:
        model = Product
        fields = ['name', 'brand', 'description', 'category', 'price', 'quantity', 'status']


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for product list view"""
    vendor_name = serializers.CharField(source='vendor.shop_name', read_only=True)
    
    images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'brand', 'description', 'category', 'vendor_name', 'price', 'quantity',
            'status', 'is_blocked', 'images', 'created_at'
        ]


class OrderAddressSerializer(serializers.ModelSerializer):
    """Serializer for address in order view"""
    class Meta:
        from user.models import Address
        model = Address
        fields = ['name', 'phone', 'email', 'address_line1', 'address_line2', 'city', 'state', 'pincode', 'country']


class VendorOrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem objects for vendor view"""
    order_id = serializers.CharField(source='order.order_number', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    product = serializers.CharField(source='product_name', read_only=True)
    price = serializers.DecimalField(source='product_price', max_digits=10, decimal_places=2, read_only=True)
    status = serializers.CharField(source='vendor_status', read_only=True)
    date = serializers.DateTimeField(source='order.created_at', read_only=True, format="%d/%m/%Y")
    payment_method = serializers.CharField(source='order.payment_method', read_only=True)
    customer_address = serializers.SerializerMethodField()
    customer_billing_address = OrderAddressSerializer(source='order.billing_address', read_only=True)

    def get_customer_address(self, obj):
        # Prefer the explicit delivery address linked to the order
        address = obj.order.delivery_address
        
        # Fallback for missing delivery address (same as invoice logic)
        if not address:
            from user.models import Address
            address = Address.objects.filter(user=obj.order.user, is_default=True).first() or \
                      Address.objects.filter(user=obj.order.user).first()
            
        if address:
            return OrderAddressSerializer(address).data
        return None

    order_subtotal = serializers.DecimalField(source='order.subtotal', max_digits=12, decimal_places=2, read_only=True)
    order_tax = serializers.DecimalField(source='order.tax_amount', max_digits=12, decimal_places=2, read_only=True)
    order_shipping = serializers.DecimalField(source='order.shipping_cost', max_digits=12, decimal_places=2, read_only=True)
    order_total = serializers.DecimalField(source='order.total_amount', max_digits=12, decimal_places=2, read_only=True)
    
    net_earning = serializers.SerializerMethodField()

    class Meta:
        from user.models import OrderItem
        model = OrderItem
        fields = ['id', 'order_id', 'order_number', 'product', 'quantity', 'price', 'status', 'date', 
                  'payment_method', 'customer_address', 'customer_billing_address', 'order_subtotal', 'order_tax', 
                  'order_shipping', 'order_total', 'commission_rate', 'commission_amount', 'net_earning']

    def get_net_earning(self, obj):
        total = obj.product_price * obj.quantity
        return total - obj.commission_amount


class VendorOrderItemStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for vendor to update order item status"""
    class Meta:
        from user.models import OrderItem
        model = OrderItem
        fields = ['vendor_status']