from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import serializers
import requests
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decimal import Decimal, InvalidOperation
from django.core.paginator import Paginator

from .models import AuthUser, Cart, CartItem, Order, OrderItem, Address, Review, Payment
from .serializers import RegisterSerializer, ProductSerializer, CartSerializer, OrderSerializer, AddressSerializer, ReviewSerializer, OrderTrackingSerializer, UserSerializer
from .forms import AddressForm
import uuid
from django.db import transaction
from django.db.models import F, Q
from vendor.models import Product, ProductImage
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from finance.services import FinanceService


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def register_api(request):
    if request.method == 'GET':
        return render(request, "user_register.html")
    
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        if request.accepted_renderer.format == 'json':
            return Response({"message": "User registered successfully"}, status=201)
        return redirect('user_login')

    if request.accepted_renderer.format == 'json':
        return Response(serializer.errors, status=400)
    return render(request, "user_register.html", {"error": serializer.errors})

@api_view(['POST'])
@permission_classes([AllowAny])
def check_email_exists(request):
    email = request.data.get('email')
    if not email:
        return Response({"error": "Email is required"}, status=400)
    
    user = AuthUser.objects.filter(email=email).first()
    if user:
        role_label = {
            'delivery': 'delivery agent',
            'vendor': 'vendor',
            'customer': 'customer',
            'admin': 'administrator'
        }.get(user.role, user.role)

        # Specifically for the delivery agent onboarding request
        # We only block if the account is ALREADY a delivery agent.
        # Customers are allowed to proceed and upgrade to delivery agents.
        if user.role == 'delivery':
             return Response({
                "exists": True,
                "error": "This account is already registered as a delivery agent."
            }, status=200)

        # For any other role (customer, vendor, etc.), we don't treat it as "exists" for the
        # delivery registration flow, so they can proceed.
        return Response({"exists": False}, status=200)

    
    return Response({"exists": False}, status=200)

@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def login_api(request):
    if request.method == 'GET':
        return render(request, "user_login.html")
    
    # support both JSON API clients (username/email) and HTML form
    username_or_email = request.data.get('email') or request.data.get('username')
    password = request.data.get('password')


    auth_identifier = username_or_email
    # If user provided a username instead of an email, resolve to the underlying email
    # because USERNAME_FIELD is 'email' in our AuthUser model.
    if username_or_email and '@' not in username_or_email:
        try:
            u = AuthUser.objects.get(username=username_or_email)
            auth_identifier = u.email
        except AuthUser.DoesNotExist:
            auth_identifier = None

    # First check if user exists to provide better debug info (optional, but helps troubleshooting)
    user_exists = AuthUser.objects.filter(email=auth_identifier).exists()
    
    user = authenticate(username=auth_identifier, password=password)

    if user:
        # Pre-fetch profiles and role info in one go to reduce DB hits
        user = AuthUser.objects.select_related('vendor_profile', 'delivery_agent_profile').get(id=user.id)
        
        # Basic active check
        if not user.is_active:
            return Response({"error": "This account is inactive."}, status=403)
        
        # Check global blocked status
        if user.is_blocked:
            return Response({"error": f"Account blocked: {user.blocked_reason or 'No reason provided'}"}, status=403)

        # Role-specific approval and status checks
        if user.role == 'delivery':
            # Check if profile exists using hasattr to avoid RelatedObjectDoesNotExist exception overhead
            if hasattr(user, 'delivery_agent_profile'):
                profile = user.delivery_agent_profile
                if profile.approval_status == 'pending':
                    return Response({
                        "error": "Your delivery partner registration is still pending admin approval. Please check back later.",
                        "status": "pending_approval"
                    }, status=403)
                elif profile.approval_status == 'rejected':
                    return Response({
                        "error": f"Your registration was rejected. Reason: {profile.rejection_reason or 'Internal documentation check failed'}",
                        "status": "rejected"
                    }, status=403)
                
                if profile.is_blocked:
                    return Response({
                        "error": f"Your delivery account has been restricted. Reason: {profile.blocked_reason or 'Policy violation'}",
                        "status": "blocked"
                    }, status=403)
            else:
                return Response({"error": "Delivery profile not found for this account."}, status=404)

        elif user.role == 'vendor':
            if hasattr(user, 'vendor_profile'):
                profile = user.vendor_profile
                if profile.approval_status == 'pending':
                    return Response({
                        "error": "Your vendor account is pending admin approval. You will be notified once approved.",
                        "status": "pending_approval"
                    }, status=403)
                elif profile.approval_status == 'rejected':
                    return Response({
                        "error": f"Your vendor application was rejected. Reason: {profile.rejection_reason or 'Compliance issues'}",
                        "status": "rejected"
                    }, status=403)
                
                if profile.is_blocked:
                    return Response({
                        "error": f"Your vendor account is currently blocked. Reason: {profile.blocked_reason or 'Policy violation'}",
                        "status": "blocked"
                    }, status=403)

        login(request, user)
        # Token generation is usually fast, but we ensure claims are added efficiently
        refresh = RefreshToken.for_user(user)
        refresh['role'] = user.role
        refresh['username'] = user.username
        refresh['is_staff'] = user.is_staff
        refresh['is_superuser'] = user.is_superuser
        
        if request.accepted_renderer.format == 'json':
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "username": user.username,
                "role": user.role
            })
        else:
            return redirect('user_products')

    if user_exists:
        return Response({"error": "Incorrect password. Please try again."}, status=401)
    return Response({"error": "No account found with this email."}, status=401)
@api_view(['POST'])
@permission_classes([AllowAny])
def google_login_api(request):
    email = request.data.get('email')
    username = request.data.get('name')
    
    if not email:
        return Response({"error": "Email is required from Google"}, status=400)
    
    # Try to find the user by email
    try:
        user = AuthUser.objects.get(email=email)
    except AuthUser.DoesNotExist:
        # Create a new user if not found
        # Use name from Google as username, or part of email
        base_username = username if username else email.split('@')[0]
        final_username = base_username
        
        # Ensure username uniqueness (basic implementation)
        counter = 1
        while AuthUser.objects.filter(username=final_username).exists():
            final_username = f"{base_username}{counter}"
            counter += 1
            
        user = AuthUser.objects.create(
            email=email,
            username=final_username,
            role='customer' # Default role for Google login
        )
        user.set_unusable_password()
        user.save()

    # Basic active check
    if not user.is_active:
        return Response({"error": "This account is inactive."}, status=403)
    
    # Check global blocked status
    if user.is_blocked:
        return Response({"error": f"Account blocked: {user.blocked_reason or 'No reason provided'}"}, status=403)

    login(request, user)
    refresh = RefreshToken.for_user(user)
    # Add custom claims
    refresh['role'] = user.role
    refresh['username'] = user.username
    
    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "username": user.username,
        "role": user.role,
        "email": user.email
    })


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


# 🔹 HOME (Product Page)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def home_api(request):
    PAGE_SIZE = 50

    from django.db.models import Avg
    # Base query with annotation to avoid N+1 queries for ratings
    products_qs = Product.objects.filter(
        status__in=['active', 'approved'],
        is_blocked=False
    ).select_related('vendor').prefetch_related('images').order_by('-id')

    # Optional category filtering  (frontend may send display names like 'Home & Kitchen')
    CATEGORY_MAP = {
        'home & kitchen': 'home_kitchen',
        'home and kitchen': 'home_kitchen',
        'beauty': 'beauty_personal_care',
        'beauty & personal care': 'beauty_personal_care',
        'toys': 'toys_games',
        'toys & games': 'toys_games',
        'sports & fitness': 'sports',
    }
    category = request.GET.get('category')
    if category and category.lower() != 'all':
        normalized = CATEGORY_MAP.get(category.lower(), category)
        products_qs = products_qs.filter(category__iexact=normalized)

    # Smart search: if search is a pure integer treat it as a product-ID lookup
    search = request.GET.get('search', '').strip()
    if search:
        if search.isdigit():
            # Exact product-ID lookup
            products_qs = products_qs.filter(id=int(search))
        else:
            # Name / category / description contains
            products_qs = products_qs.filter(
                Q(name__icontains=search) |
                Q(category__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Increment search_count for found items (cap to prevent mass updates)
        try:
            products_qs.update(search_count=F('search_count') + 1)
        except Exception:
            pass

    if request.accepted_renderer.format == 'json':
        # Server-side pagination: 50 per page
        page_number = int(request.GET.get('page', 1))
        paginator = Paginator(products_qs, PAGE_SIZE)
        page_obj = paginator.get_page(page_number)

        serializer = ProductSerializer(page_obj.object_list, many=True, context={'request': request})
        return Response({
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'results': serializer.data,
        })

    # HTML fallback
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = sum(item.quantity for item in cart.items.all())
        except Cart.DoesNotExist:
            pass

    return render(request, "product_list.html", {
        "products": products_qs,
        "cart_count": cart_count,
        "user": request.user
    })

def get_product(request):
    products_qs = Product.objects.all().select_related('vendor').prefetch_related('images')
    page_number = request.GET.get('page', 1)
    paginator = Paginator(products_qs, 20)
    page_obj = paginator.get_page(page_number)
    
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = sum(item.quantity for item in cart.items.all())
        except Cart.DoesNotExist:
            pass
            
    return render(request, "product_list.html", {
        "products": page_obj, 
        "cart_count": cart_count,
        "user": request.user
    })

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Stock availability check
    if product.quantity <= 0:
        if request.accepted_renderer.format == 'json':
            return Response({"error": f"'{product.name}' is out of stock."}, status=400)
        return redirect('cart')

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not item_created:
        # Prevent adding more than available stock
        if cart_item.quantity >= product.quantity:
            if request.accepted_renderer.format == 'json':
                return Response(
                    {"error": f"Only {product.quantity} unit(s) of '{product.name}' available in stock."},
                    status=400
                )
            return redirect('cart')
        cart_item.quantity += 1
        cart_item.save()

    if request.accepted_renderer.format == 'json':
        return Response({
            "message": "Product added to cart",
            "cart_count": sum(item.quantity for item in cart.items.all())
        })

    return redirect('cart')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    if request.accepted_renderer.format == 'json':
        serializer = CartSerializer(cart)
        return Response(serializer.data)
        
    total_price = sum(item.get_total() for item in cart_items)
    
    return render(request, "cart.html", {
        "cart_items": cart_items, 
        "total_cart_price": total_price
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def checkout_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    if not cart_items:
        if request.accepted_renderer.format == 'json':
             return Response({"message": "Cart is empty"}, status=400)
        return redirect('cart')
        
    total_price = sum(item.get_total() for item in cart_items)
    items_count = sum(item.quantity for item in cart_items)
    
    if request.accepted_renderer.format == 'json':
        return Response({
            "total_price": total_price,
            "items_count": items_count,
            "cart_items": CartSerializer(cart).data
        })
    
    return render(request, "checkout.html", {
        "total_price": total_price,
        "items_count": items_count
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_payment(request):
    payment_mode = request.data.get('payment_mode')
    transaction_id = request.data.get('transaction_id') or str(uuid.uuid4())[:12]
    items_from_request = request.data.get('items')
    order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"

    if not payment_mode:
        return Response({"error": "Payment mode required"}, status=400)

    try:
        with transaction.atomic():
            # CASE 1: Items passed directly (frontend state)
            if items_from_request:
                # Compute total from the items list sent by the frontend
                total_product_amount = Decimal('0.00')
                for i in items_from_request:
                    try:
                        p = Decimal(str(i.get('price') or 0))
                        q = int(i.get('quantity') or 1)
                        total_product_amount += p * q
                    except (ValueError, TypeError, InvalidOperation):
                        continue # skip invalid items
                
                tax_amount = (total_product_amount * Decimal('0.05')).quantize(Decimal('0.01'))
                shipping_cost = Decimal('50.00') if total_product_amount > 0 else Decimal('0.00')
                grand_total = total_product_amount + tax_amount + shipping_cost
                
                # Flexible address retrieval: support 'address_id' or 'delivery_address' object/id
                raw_address_id = request.data.get('address_id')
                if not raw_address_id:
                    delivery_address_data = request.data.get('delivery_address')
                    if isinstance(delivery_address_data, dict):
                        raw_address_id = delivery_address_data.get('id')
                    elif delivery_address_data:
                        raw_address_id = delivery_address_data

                addr_id = int(raw_address_id) if raw_address_id and str(raw_address_id).isdigit() else None

                if not addr_id:
                    return Response({"error": "Please select a delivery address before placing the order."}, status=400)

                order = Order.objects.create(
                    user=request.user,
                    order_number=order_number,
                    payment_method=payment_mode,
                    delivery_address_id=addr_id,  # Safe integer or None
                    transaction_id=transaction_id,
                    subtotal=total_product_amount,
                    tax_amount=tax_amount,
                    shipping_cost=shipping_cost,
                    total_amount=grand_total,
                    payment_status='completed',
                    status='confirmed'
                )
                
                # Create Payment record
                Payment.objects.create(
                    order=order,
                    user=request.user,
                    method=payment_mode if payment_mode in dict(Payment.PAYMENT_METHOD_CHOICES) else 'cod',
                    amount=grand_total,
                    transaction_id=transaction_id,
                    status='completed',
                    completed_at=timezone.now().replace(second=0, microsecond=0)
                )
                
                for item_data in items_from_request:
                    price = Decimal(str(item_data.get('price', 0)))
                    quantity = int(item_data.get('quantity', 1))
                    
                    # Try to link product and vendor
                    product = None
                    vendor = None
                    product_id = item_data.get('id') or item_data.get('product_id')
                    
                    if product_id:
                        from vendor.models import Product
                        try:
                            product = Product.objects.get(id=product_id)
                            # Check stock
                            if product.quantity < quantity:
                                raise serializers.ValidationError(f"Insufficient stock for {product.name}")
                            
                            vendor = product.vendor
                        except Product.DoesNotExist:
                            pass
                    
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        vendor=vendor,
                        product_name=item_data.get('name'),
                        quantity=quantity,
                        product_price=price,
                        subtotal=price * quantity
                    )
                    
                    # Decrease inventory atomically
                    if product:
                        Product.objects.filter(pk=product.pk).update(quantity=F('quantity') - quantity)
                
                # Record financial entries in ledger
                FinanceService.record_order_financials(order)
                
                Cart.objects.filter(user=request.user).delete()

            # CASE 2: Use items from the database cart
            else:
                cart = Cart.objects.get(user=request.user)
                cart_items = cart.items.all()
                if not cart_items:
                    return Response({"error": "Cart is empty"}, status=400)

                total_product_amount = sum(item.get_total() for item in cart_items)
                tax_amount = (total_product_amount * Decimal('0.05')).quantize(Decimal('0.01'))
                shipping_cost = Decimal('50.00') if total_product_amount > 0 else Decimal('0.00')
                grand_total = total_product_amount + tax_amount + shipping_cost
                
                # Flexible address retrieval
                raw_address_id = request.data.get('address_id')
                if not raw_address_id:
                    delivery_address_data = request.data.get('delivery_address')
                    if isinstance(delivery_address_data, dict):
                        raw_address_id = delivery_address_data.get('id')
                    elif delivery_address_data:
                        raw_address_id = delivery_address_data

                addr_id = int(raw_address_id) if raw_address_id and str(raw_address_id).isdigit() else None

                if not addr_id:
                    return Response({"error": "Please select a delivery address before placing the order."}, status=400)

                order = Order.objects.create(
                    user=request.user,
                    order_number=order_number,
                    payment_method=payment_mode,
                    delivery_address_id=addr_id,
                    billing_address_id=addr_id, # Default billing to delivery if not separate
                    transaction_id=transaction_id,
                    subtotal=total_product_amount,
                    tax_amount=tax_amount,
                    shipping_cost=shipping_cost,
                    total_amount=grand_total,
                    payment_status='completed',
                    status='confirmed'
                )

                # Create Payment record
                Payment.objects.create(
                    order=order,
                    user=request.user,
                    method=payment_mode if payment_mode in dict(Payment.PAYMENT_METHOD_CHOICES) else 'cod',
                    amount=grand_total,
                    transaction_id=transaction_id,
                    status='completed',
                    completed_at=timezone.now().replace(second=0, microsecond=0)
                )

                for item in cart_items:
                    # Check stock
                    if item.product.quantity < item.quantity:
                        raise serializers.ValidationError(f"Insufficient stock for {item.product.name}")

                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        vendor=item.product.vendor,
                        product_name=item.product.name,
                        quantity=item.quantity,
                        product_price=item.product.price,
                        subtotal=item.get_total()
                    )
                    
                    # Decrease inventory atomically
                    Product.objects.filter(pk=item.product.pk).update(quantity=F('quantity') - item.quantity)
                
                # Record financial entries in ledger
                FinanceService.record_order_financials(order)
                
                cart.items.all().delete()

    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()   # prints full stack trace to Django console
        return Response({"error": f"Database Error: {str(e)}"}, status=500)

    # Send confirmation email
    try:
        subject = f'Order Confirmed - {order.order_number}'
        
        # Dynamically determine the frontend URL
        frontend_origin = request.headers.get('Origin') or request.headers.get('Referer', '').rstrip('/')
        if not frontend_origin or 'localhost:8000' in frontend_origin:
            frontend_origin = 'http://localhost:5173' # fallback
            
        from urllib.parse import urlparse
        parsed = urlparse(frontend_origin)
        frontend_origin = f"{parsed.scheme}://{parsed.netloc}"
        
        tracking_link = f"{frontend_origin}/track-order/{order.order_number}"
        
        message = (
            f"Dear {request.user.username},\n\n"
            f"Your order {order.order_number} has been successfully placed and confirmed!\n"
            f"Total Amount: ₹{order.total_amount}\n\n"
            f"You can track your order here: {tracking_link}\n\n"
            "Our team is already preparing your items for delivery. You can track your order status "
            "anytime in your profile section.\n\n"
            "Thank you for choosing ShopSphere!\n\n"
            "Regards,\n"
            "ShopSphere Team"
        )
        send_mail(subject, message, settings.EMAIL_HOST_USER, [request.user.email])
    except Exception as e:
        print(f"Failed to send order confirmation email: {e}")

    if request.accepted_renderer.format == 'json':
        return Response({
            "success": True,
            "message": "Order placed successfully",
            "order_number": order_number,
            "order_id": order.id
        })
    
    return redirect('my_orders')

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    if request.accepted_renderer.format == 'json':
        serializer = OrderSerializer(orders, many=True, context={'request': request})
        return Response(serializer.data)
        
    return render(request, "my_orders.html", {"orders": orders})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):
    """
    Cancel an order and restore product stock quantities.
    Only orders in 'pending' or 'confirmed' state can be cancelled.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if not order.can_be_cancelled():
        return Response(
            {"error": f"Order '{order.order_number}' cannot be cancelled. Current status: {order.status}."},
            status=400
        )

    try:
        with transaction.atomic():
            # Restore product quantities and cancel items
            for item in order.items.select_related('product').all():
                if item.product:
                    Product.objects.filter(pk=item.product.pk).update(
                        quantity=F('quantity') + item.quantity
                    )
                item.vendor_status = 'cancelled'
                item.save(update_fields=['vendor_status'])
            
            # Cancel delivery assignment if exists
            try:
                from deliveryAgent.models import DeliveryAssignment
                assignment = DeliveryAssignment.objects.filter(order=order).first()
                if assignment:
                    assignment.status = 'cancelled'
                    assignment.save(update_fields=['status'])
            except Exception:
                pass

            # Reverse financial entries
            FinanceService.cancel_order_financials(order)

            order.status = 'cancelled'
            order.save(update_fields=['status', 'updated_at'])

    except Exception as e:
        return Response({"error": f"Cancellation failed: {str(e)}"}, status=500)

    return Response({
        "success": True,
        "message": f"Order {order.order_number} has been cancelled and stock has been restored.",
        "order_number": order.order_number,
        "status": order.status,
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_tracking(request, order_number):
    try:
        order = Order.objects.prefetch_related('items', 'tracking_history').select_related(
            'delivery_address'
        ).get(order_number=order_number, user=request.user)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    # -------------------------------------------------------------------
    # Build synthetic tracking steps from order + delivery assignment
    # -------------------------------------------------------------------
    # Check delivery assignment status for more granularity if order is in 'shipping'
    assignment = None
    try:
        assignment = order.delivery_assignment
    except Exception:
        pass

    # Basic stages
    # 0: Placed
    # 1: Confirmed
    # 2: Picked Up (Assignment: picked_up)
    # 3: Out for Delivery (Assignment: in_transit / attempting_delivery)
    # 4: Delivered (Order: delivered)
    
    current_idx = 0
    if order.status == 'pending':
        current_idx = 0
    elif order.status == 'confirmed':
        current_idx = 1
    elif order.status == 'shipping':
        current_idx = 2
    elif order.status == 'out_for_delivery':
        current_idx = 3
    elif order.status == 'delivered':
        current_idx = 4
    elif order.status == 'cancelled':
        current_idx = 0 # Fallback

    STATUS_STEPS = [
        ('pending',    'Order Placed',     'Your order has been placed successfully.'),
        ('confirmed',  'Confirmed',        'Seller has confirmed your order.'),
        ('shipping',   'Picked Up',        'Package picked up by delivery agent.'),
        ('in_transit', 'Out for Delivery', 'Your package is on its way!'),
        ('delivered',  'Delivered',        'Order delivered successfully.'),
    ]

    tracking_steps = []
    for i, (status_key, label, note) in enumerate(STATUS_STEPS):
        tracking_steps.append({
            'key': status_key,
            'label': label,
            'note': note,
            'done': i <= current_idx,
            'active': i == current_idx,
        })

    # -------------------------------------------------------------------
    # Enrich with DeliveryAssignment if present
    # -------------------------------------------------------------------
    agent_info = None
    estimated_delivery = None
    if assignment:
        agent_info = {
            'name': assignment.agent.user.get_full_name() or assignment.agent.user.username,
            'phone': assignment.agent.phone_number,
            'vehicle': assignment.agent.vehicle_type,
            'vehicle_number': assignment.agent.vehicle_number or '',
        }
        estimated_delivery = str(assignment.estimated_delivery_date)

    # Delivery address summary
    addr = order.delivery_address
    delivery_address = None
    if addr:
        delivery_address = f"{addr.address_line1}, {addr.city}, {addr.state} {addr.pincode}"

    return Response({
        'order_number': order.order_number,
        'status': order.status,
        'created_at': order.created_at.isoformat(),
        'subtotal': str(order.total_amount),
        'items_count': order.items.count(),
        'current_step_index': current_idx,
        'tracking_steps': tracking_steps,
        'agent_info': agent_info,
        'estimated_delivery': estimated_delivery,
        'delivery_address': delivery_address,
    })

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def address_page(request):
    if request.method == 'POST':
        data = request.data.copy()
        # Map frontend field names to model field names
        if 'address' in data and 'address_line1' not in data:
            data['address_line1'] = data.pop('address')
        
        serializer = AddressSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "message": "Address saved successfully",
                "address": serializer.data
            }, status=201)
        return Response(serializer.errors, status=400)

    # GET — return all addresses for the user
    addresses = Address.objects.filter(user=request.user).order_by('-created_at')
    serializer = AddressSerializer(addresses, many=True)
    return Response({"addresses": serializer.data})


@api_view(['POST', 'GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def delete_address(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)
    address.delete()
    return Response({"message": "Address deleted successfully"})


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_address(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)
    
    # Map frontend field names to model field names
    data = request.data.copy()
    if 'address' in data and 'address_line1' not in data:
        data['address_line1'] = data.pop('address')
    
    serializer = AddressSerializer(address, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "Address updated successfully",
            "address": serializer.data
        })
    return Response(serializer.errors, status=400)


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    logout(request)
    return redirect('user_login')

# @login_required
# def review_product(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     user = request.user
#     if request.method == "POST":
#         rating = request.POST.get('rating')
#         if rating and rating.isdigit() and 1 <= int(rating) <= 5:
#             Review.objects.create(
#                 user=request.user,
#                 Product=product,
#                 rating=int(rating),
#                 comment=request.POST.get('comment', ''),
#                 pictures=request.FILES.get('pictures')
#             )
#             return redirect('home')
#         return render(request, 'review.html', {'product': product, 'error': 'Please provide a valid rating between 1 and 5.'})
#     return render(request, 'review.html', {'product': product})

@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user_review = None
    can_edit_review = False
    days_left = 0
    
    try:
        if request.user and request.user.is_authenticated:
            user_review = Review.objects.filter(user=request.user, Product=product).first()
            if user_review:
                time_diff = timezone.now() - user_review.created_at
                if time_diff.days < 5:
                    can_edit_review = True
                    days_left = 5 - time_diff.days
    except Exception:
        pass

    reviews = Review.objects.filter(Product=product).order_by('-created_at')
    product_data = ProductSerializer(product, context={'request': request}).data
    reviews_data = ReviewSerializer(reviews, many=True).data

    return Response({
        "product": product_data,
        "reviews": reviews_data,
        "user_review": ReviewSerializer(user_review).data if user_review else None,
        "can_edit_review": can_edit_review,
        "days_left": days_left
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "invoice_customer.html", {"order": order})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_review_api(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user_review = Review.objects.filter(user=request.user, Product=product).first()
    
    if user_review:
        time_diff = timezone.now() - user_review.created_at
        if time_diff.days >= 5:
            return Response({"error": "Review editing window (5 days) has passed"}, status=403)
        serializer = ReviewSerializer(user_review, data=request.data, partial=True)
    else:
        serializer = ReviewSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save(user=request.user, Product=product)
        return Response(serializer.data, status=201 if not user_review else 200)
    return Response(serializer.errors, status=400)

# @login_required
# def user_reviews(request):
#     reviews = Review.objects.filter(user=request.user)
#     return render(request, 'user_reviews.html', {'reviews': reviews})

# =========================================================
# PASSWORD RESET FLOW
# =========================================================
reset_tokens = {}

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def auth_page(request):
    page = request.GET.get("page", "login")

    # FORGOT PASSWORD
    if page == "forgot" and request.method == "POST":
        email = request.data.get("email") or request.POST.get("email")
        user = AuthUser.objects.filter(email=email).first()

        if user:
            token = str(uuid.uuid4())
            reset_tokens[token] = user.id

            # Dynamically determine the frontend URL from the request
            frontend_origin = request.headers.get('Origin') or request.headers.get('Referer', '').rstrip('/')
            if not frontend_origin or frontend_origin.startswith('http://localhost:8000'):
                frontend_origin = 'http://localhost:5173'  # fallback
            # Strip any trailing path from Referer (e.g. http://localhost:5173/forgotpassword -> http://localhost:5173)
            from urllib.parse import urlparse
            parsed = urlparse(frontend_origin)
            frontend_origin = f"{parsed.scheme}://{parsed.netloc}"

            link = f"{frontend_origin}/reset-password?token={token}"

            send_mail(
                "Password Reset Request",
                f"Click this link to reset password:\n{link}",
                settings.EMAIL_HOST_USER,
                [email]
            )

            return Response({"message": "Mail sent successfully ✅"}, status=200)
        else:
            return Response({"message": "Email not registered ❌"}, status=404)

    # RESET PASSWORD
    if page == "reset" and request.method == "POST":
        token = request.GET.get("token")

        if token in reset_tokens:
            p1 = request.data.get("password1") or request.POST.get("password1")
            p2 = request.data.get("password2") or request.POST.get("password2")

            if p1 == p2:
                user = AuthUser.objects.get(id=reset_tokens[token])
                user.set_password(p1)
                user.save()
                del reset_tokens[token]

                return Response({"message": "Password changed successfully ✅"}, status=200)

            return Response({"message": "Passwords do not match ❌"}, status=400)

    return render(request, "auth.html", {"page": page})


@api_view(['GET'])
@permission_classes([AllowAny])
def reverse_geocode(request):
    """
    Proxy to Nominatim API to avoid CORS issues on frontend.
    """
    lat = request.query_params.get('lat')
    lon = request.query_params.get('lon')

    if not lat or not lon:
        return Response({"error": "Latitude and Longitude are required"}, status=400)

    # Nominatim requires format=json and a proper User-Agent
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
    headers = {
        'User-Agent': 'ShopSphere-Project-Ecommerce/1.0'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        return Response(response.json(), status=response.status_code)
    except Exception as e:
        return Response({"error": f"Geocoding failed: {str(e)}"}, status=500)

@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def get_trending_products(request):
    # Trending considers search count and ratings
    trending = Product.objects.filter(
        status__in=['active', 'approved'],
        is_blocked=False,
        average_rating__gt=3
    ).order_by('-search_count', '-total_reviews', '-average_rating')[:12]
    
    serializer = ProductSerializer(trending, many=True, context={'request': request})
    data = serializer.data
    # Ensure average_rating is never None
    for item in data:
        if item.get('average_rating') is None:
            item['average_rating'] = 0.0
    return Response(data)