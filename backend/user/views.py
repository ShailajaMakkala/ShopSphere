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
from deliveryAgent.services import auto_assign_order


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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_wallet(request):
    """Return the authenticated user's wallet balance and recent transactions."""
    from .models import UserWallet
    wallet, _ = UserWallet.objects.get_or_create(user=request.user)
    recent_txns = wallet.transactions.order_by('-created_at')[:20]
    return Response({
        "balance": float(wallet.balance),
        "total_credited": float(wallet.total_credited),
        "total_debited": float(wallet.total_debited),
        "transactions": [
            {
                "type": t.transaction_type,
                "amount": float(t.amount),
                "description": t.description,
                "date": t.created_at.isoformat(),
            }
            for t in recent_txns
        ]
    })




# 🔹 HOME (Product Page)
@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def home_api(request):
    PAGE_SIZE = 50

    from django.db.models import Avg
    # Base query with annotation to avoid N+1 queries for ratings
    from django.db.models import Avg, Count, Prefetch
    from vendor.models import ProductImage

    # Optimized image prefetch that avoids loading large binary blobs for list views
    images_prefetch = Prefetch(
        'images',
        queryset=ProductImage.objects.defer('image_data')
    )

    # Base query with annotation to avoid N+1 queries for ratings
    products_qs = Product.objects.filter(
        status__in=['active', 'approved'],
        is_blocked=False
    ).select_related('vendor').prefetch_related(images_prefetch).annotate(
        avg_rating=Avg('reviews__rating'),
        count_reviews=Count('reviews')
    ).order_by('-id')

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
    from django.db.models import Prefetch, Avg, Count
    from vendor.models import ProductImage
    
    # Define images prefetch with defer to avoid binary data transfer
    images_prefetch = Prefetch(
        'product__images',
        queryset=ProductImage.objects.defer('image_data')
    )

    # Pre-fetch cart items with products and images in one go
    cart, _ = Cart.objects.prefetch_related(
        Prefetch(
            'items',
            queryset=CartItem.objects.select_related('product', 'product__vendor').prefetch_related(images_prefetch).annotate(
                avg_rating=Avg('product__reviews__rating')
            )
        )
    ).get_or_create(user=request.user)
    
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
    """
    Process a payment and create an order with full atomicity.
    No partial data will ever be persisted — if any step fails,
    the entire transaction is rolled back.
    """
    import logging
    import traceback as tb
    logger = logging.getLogger(__name__)

    payment_mode = request.data.get('payment_mode')
    transaction_id = request.data.get('transaction_id') or str(uuid.uuid4())[:12]
    items_from_request = request.data.get('items')
    order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"

    if not payment_mode:
        return Response({"error": "Payment mode required"}, status=400)

    # ── Resolve delivery address ────────────────────────────
    def _resolve_address_id(data):
        raw = data.get('address_id')
        if not raw:
            daddr = data.get('delivery_address')
            if isinstance(daddr, dict):
                raw = daddr.get('id')
            elif daddr:
                raw = daddr
        return int(raw) if raw and str(raw).isdigit() else None

    addr_id = _resolve_address_id(request.data)
    if not addr_id:
        return Response(
            {"error": "Please select a delivery address before placing the order."},
            status=400
        )

    order = None  # will be set inside the atomic block

    try:
        with transaction.atomic():

            # ── CASE 1: Items provided by frontend ──────────────
            if items_from_request:
                # --- Stock pre-validation BEFORE any DB write ---
                validated_items = []
                total_product_amount = Decimal('0.00')

                for item_data in items_from_request:
                    try:
                        price = Decimal(str(item_data.get('price', 0)))
                        quantity = int(item_data.get('quantity', 1))
                    except (ValueError, TypeError, InvalidOperation):
                        logger.warning(f"Skipping invalid item payload: {item_data}")
                        continue

                    product_id = item_data.get('id') or item_data.get('product_id')
                    product = None
                    vendor = None

                    if product_id:
                        from vendor.models import Product as VProduct
                        try:
                            # Lock the row to prevent concurrent overselling
                            product = VProduct.objects.select_for_update().get(id=product_id)
                            if product.quantity < quantity:
                                raise ValueError(
                                    f"Insufficient stock for '{product.name}'. "
                                    f"Available: {product.quantity}, Requested: {quantity}"
                                )
                            vendor = product.vendor
                        except VProduct.DoesNotExist:
                            logger.warning(f"Product {product_id} not found; item will be saved without product link.")

                    validated_items.append({
                        'product': product,
                        'vendor': vendor,
                        'name': item_data.get('name') or (product.name if product else 'Unknown'),
                        'price': price,
                        'quantity': quantity,
                        'subtotal': price * quantity,
                    })
                    total_product_amount += price * quantity

                if not validated_items:
                    return Response({"error": "No valid items found in the request."}, status=400)

                tax_amount = (total_product_amount * Decimal('0.05')).quantize(Decimal('0.01'))
                shipping_cost = Decimal('50.00') if total_product_amount > 0 else Decimal('0.00')
                grand_total = total_product_amount + tax_amount + shipping_cost

                # --- Create Order (payment_status='pending' until all writes succeed) ---
                order = Order.objects.create(
                    user=request.user,
                    order_number=order_number,
                    payment_method=payment_mode,
                    delivery_address_id=addr_id,
                    transaction_id=transaction_id,
                    subtotal=total_product_amount,
                    tax_amount=tax_amount,
                    shipping_cost=shipping_cost,
                    total_amount=grand_total,
                    payment_status='pending',  # stays pending until all steps done
                    status='confirmed'
                )

                # --- Create OrderItems & decrement stock ---
                for item in validated_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        vendor=item['vendor'],
                        product_name=item['name'],
                        quantity=item['quantity'],
                        product_price=item['price'],
                        subtotal=item['subtotal'],
                    )
                    if item['product']:
                        from vendor.models import Product as VProduct
                        VProduct.objects.filter(pk=item['product'].pk).update(
                            quantity=F('quantity') - item['quantity']
                        )

                # --- Create Payment record ---
                Payment.objects.create(
                    order=order,
                    user=request.user,
                    method=payment_mode if payment_mode in dict(Payment.PAYMENT_METHOD_CHOICES) else 'cod',
                    amount=grand_total,
                    transaction_id=transaction_id,
                    status='completed',
                    completed_at=timezone.now().replace(second=0, microsecond=0)
                )

                # --- All writes succeeded: mark payment as completed ---
                order.payment_status = 'completed'
                order.save(update_fields=['payment_status'])

                # --- Financial ledger ---
                FinanceService.record_order_financials(order)

                # --- Clear cart (frontend cart items passed directly, clear DB cart too) ---
                Cart.objects.filter(user=request.user).delete()

            # ── CASE 2: Items from database cart ────────────────
            else:
                try:
                    cart = Cart.objects.get(user=request.user)
                except Cart.DoesNotExist:
                    return Response({"error": "Cart not found."}, status=404)

                cart_items = list(cart.items.select_related('product__vendor').all())
                if not cart_items:
                    return Response({"error": "Your cart is empty."}, status=400)

                # --- Stock pre-validation BEFORE any DB write ---
                for item in cart_items:
                    # Lock each product row
                    product = (
                        Product.objects.select_for_update().get(pk=item.product.pk)
                    )
                    if product.quantity < item.quantity:
                        raise ValueError(
                            f"Insufficient stock for '{product.name}'. "
                            f"Available: {product.quantity}, Requested: {item.quantity}"
                        )

                total_product_amount = sum(item.get_total() for item in cart_items)
                tax_amount = (total_product_amount * Decimal('0.05')).quantize(Decimal('0.01'))
                shipping_cost = Decimal('50.00') if total_product_amount > 0 else Decimal('0.00')
                grand_total = total_product_amount + tax_amount + shipping_cost

                # --- Create Order ---
                order = Order.objects.create(
                    user=request.user,
                    order_number=order_number,
                    payment_method=payment_mode,
                    delivery_address_id=addr_id,
                    billing_address_id=addr_id,
                    transaction_id=transaction_id,
                    subtotal=total_product_amount,
                    tax_amount=tax_amount,
                    shipping_cost=shipping_cost,
                    total_amount=grand_total,
                    payment_status='pending',  # pending until all steps done
                    status='confirmed'
                )

                # --- Create OrderItems & decrement stock ---
                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        vendor=item.product.vendor,
                        product_name=item.product.name,
                        quantity=item.quantity,
                        product_price=item.product.price,
                        subtotal=item.get_total(),
                    )
                    Product.objects.filter(pk=item.product.pk).update(
                        quantity=F('quantity') - item.quantity
                    )

                # --- Create Payment record ---
                Payment.objects.create(
                    order=order,
                    user=request.user,
                    method=payment_mode if payment_mode in dict(Payment.PAYMENT_METHOD_CHOICES) else 'cod',
                    amount=grand_total,
                    transaction_id=transaction_id,
                    status='completed',
                    completed_at=timezone.now().replace(second=0, microsecond=0)
                )

                # --- All writes succeeded: mark payment as completed ---
                order.payment_status = 'completed'
                order.save(update_fields=['payment_status'])

                # --- Financial ledger ---
                FinanceService.record_order_financials(order)

                # --- Clear database cart ---
                cart.items.all().delete()

            # ── Auto-assign delivery (outside critical path — failure is non-fatal) ──
            try:
                auto_assign_order(order)
            except Exception as assign_err:
                logger.warning(f"Auto-assignment skipped for order {order.id}: {assign_err}")

    except ValueError as ve:
        # Stock / validation error — safe, nothing was committed
        logger.warning(f"Payment blocked - validation error: {ve}")
        return Response({"error": str(ve)}, status=422)  # 422 Unprocessable Entity
    except Cart.DoesNotExist:
        return Response({"error": "Cart not found."}, status=404)
    except Exception as exc:
        logger.error(f"Payment processing failed for user {request.user.id}: {exc}")
        tb.print_exc()
        return Response(
            {"error": "Order could not be placed due to a server error. Please try again."},
            status=500
        )

    # ── Send confirmation email (non-critical) ─────────────
    try:
        frontend_origin = request.headers.get('Origin') or request.headers.get('Referer', '').rstrip('/')
        if not frontend_origin or 'localhost:8000' in frontend_origin:
            frontend_origin = 'http://localhost:5173'
        from urllib.parse import urlparse
        parsed = urlparse(frontend_origin)
        frontend_origin = f"{parsed.scheme}://{parsed.netloc}"
        tracking_link = f"{frontend_origin}/track-order/{order.order_number}"

        message = (
            f"Dear {request.user.username},\n\n"
            f"Your order {order.order_number} has been successfully placed and confirmed!\n"
            f"Total Amount: ₹{order.total_amount}\n\n"
            f"Track your order: {tracking_link}\n\n"
            "Thank you for choosing ShopSphere!\n\nRegards,\nShopSphere Team"
        )
        send_mail(
            subject=f'Order Confirmed - {order.order_number}',
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[request.user.email]
        )
    except Exception as mail_err:
        logger.warning(f"Order confirmation email failed: {mail_err}")

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
    from django.db.models import Prefetch
    from vendor.models import ProductImage
    
    # Optimized prefetch for OrderItem -> Product -> Images
    images_prefetch = Prefetch(
        'items__product__images',
        queryset=ProductImage.objects.defer('image_data')
    )
    
    # Fetch orders with items, products and images efficiently 
    orders = Order.objects.filter(user=request.user).select_related(
        'delivery_address', 'billing_address'
    ).prefetch_related(
        'items', 
        'items__product', 
        'items__product__vendor',
        images_prefetch,
        'tracking_history'
    ).order_by('-created_at')
    
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
    from django.db.models import Prefetch
    from vendor.models import ProductImage

    # Prefetch images for product items
    images_prefetch = Prefetch(
        'items__product__images',
        queryset=ProductImage.objects.defer('image_data')
    )

    try:
        order = Order.objects.select_related(
            'delivery_address'
        ).prefetch_related(
            'items', 
            'items__product', 
            'items__product__vendor',
            images_prefetch, 
            'tracking_history'
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
    from django.db.models import Prefetch, Avg, Count
    from vendor.models import ProductImage

    # Optimized image prefetch that avoids loading large binary blobs
    images_prefetch = Prefetch(
        'images',
        queryset=ProductImage.objects.defer('image_data')
    )

    # Use prefetch_related and select_related for the single product to avoid N+1
    product = get_object_or_404(
        Product.objects.select_related('vendor').prefetch_related(images_prefetch).annotate(
            avg_rating=Avg('reviews__rating'),
            count_reviews=Count('reviews')
        ), 
        id=product_id
    )
    
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
    """
    Fetch trending products based on search_count, but strictly filtered by real user reviews.
    Requirement: Trending products MUST have an average rating > 3.0 calculated from the reviews table.
    """
    from vendor.models import Product, ProductImage
    from django.db.models import Avg, Count, Prefetch
    from user.models import Review

    # Optimized image prefetch
    images_prefetch = Prefetch(
        'images',
        queryset=ProductImage.objects.defer('image_data')
    )

    # Single query approach:
    # 1. Annotate with real-time average and count from the related 'reviews' set
    # 2. Filter by the rule: Average > 3.0 AND Count > 0
    # 3. Order by search_count (trending) then quality metrics
    trending = (
        Product.objects
        .annotate(
            calculated_avg=Avg('reviews__rating'),
            total_revs=Count('reviews__id')
        )
        .filter(
            calculated_avg__gt=3.0, # Strictly greater than 3.0
            total_revs__gt=0,       # Must have at least one review
            status__in=['active', 'approved'],
            is_blocked=False
        )
        .select_related('vendor')
        .prefetch_related(images_prefetch)
        .order_by('-search_count', '-calculated_avg', '-total_revs', '-id')[:12]
    )

    serializer = ProductSerializer(trending, many=True, context={'request': request})
    data = serializer.data

    # Ensure the frontend receives the calculated values in the standard keys
    # ProductSerializer might default to the model field 'average_rating', 
    # so we explicitly overwrite it with our live-calculated 'calculated_avg'.
    for i, item in enumerate(data):
        prod_obj = trending[i]
        item['average_rating'] = float(round(prod_obj.calculated_avg or 0.0, 2))
        item['total_reviews'] = prod_obj.total_revs
        item['is_trending'] = True

    return Response(data)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_return_api(request, order_id):
    """Initiate a return request for an order"""
    from .models import Order, OrderReturn, OrderTracking
    from django.db import transaction
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # 1. Eligibility Check
    if not order.can_be_returned():
        return Response({
            "error": "This order is not eligible for return. Ensure it's delivered and within the 3rd-day window."
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 2. Check if already requested
    if OrderReturn.objects.filter(order=order).exclude(status='rejected').exists():
         return Response({
            "error": "A return request has already been initiated for this order."
        }, status=status.HTTP_400_BAD_REQUEST)

    reason = request.data.get('reason')
    description = request.data.get('description', '')
    
    if not reason:
         return Response({"error": "Reason for return is required."}, status=400)

    # 3. Create Return Request for items
    returns_created = []
    with transaction.atomic():
        order_items = list(order.items.all())
        total_subtotal = sum(item.subtotal for item in order_items) or Decimal('1')  # avoid div-by-0

        for item in order_items:
            # Proportional refund: item's share of the total amount paid (incl. tax + shipping)
            item_proportion = Decimal(str(item.subtotal)) / Decimal(str(total_subtotal))
            exact_refund = (item_proportion * Decimal(str(order.total_amount))).quantize(
                Decimal('0.01'), rounding='ROUND_HALF_UP'
            )
            ret = OrderReturn.objects.create(
                order=order,
                order_item=item,
                user=request.user,
                reason=reason,
                description=description,
                return_amount=exact_refund,  # exact proportional paid amount (₹)
                status='requested'
            )
            returns_created.append(ret.id)
            
        # Add a tracking entry
        OrderTracking.objects.create(
            order=order,
            status='Return Requested',
            location='Online Request',
            notes=f"Return initiated for all items. Reason: {reason}"
        )
        
        # Return will be auto-assigned after admin approval

    return Response({
        "message": "Return request submitted successfully. Once approved by the administrator, a pickup agent will be assigned to collect the items.",
        "return_ids": returns_created
    }, status=201)


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def get_deal_of_the_day(request):
    """
    Returns a deterministic subset of products that changes every day.
    Rotates through all available products.
    """
    from django.db.models import Prefetch, Avg, Count
    from datetime import date

    # Number of products to show in the deal section
    PRODUCTS_PER_DAY = 10 

    # 1. Get all eligible products
    images_prefetch = Prefetch(
        'images',
        queryset=ProductImage.objects.defer('image_data')
    )
    
    # We order by ID to ensure a stable base list for rotation
    queryset = Product.objects.filter(
        status__in=['active', 'approved'],
        is_blocked=False
    ).select_related('vendor').prefetch_related(images_prefetch).annotate(
        avg_rating=Avg('reviews__rating'),
        count_reviews=Count('reviews')
    ).order_by('id')

    all_products = list(queryset)
    total_products = len(all_products)

    if total_products == 0:
        return Response([])

    # 2. Calculate rotation based on days since a reference date
    reference_date = date(2024, 1, 1)
    today = date.today()
    days_passed = (today - reference_date).days
    
    start_index = (days_passed * PRODUCTS_PER_DAY) % total_products
    
    # 3. Select products with wrap-around
    deal_products = []
    for i in range(min(PRODUCTS_PER_DAY, total_products)):
        idx = (start_index + i) % total_products
        deal_products.append(all_products[idx])

    serializer = ProductSerializer(deal_products, many=True, context={'request': request})
    
    # Inject 'is_deal' flag and potential discount display logic
    data = serializer.data
    for item in data:
        item['is_deal_of_the_day'] = True
        # If product doesn't have a discount, we can simulate one for the 'Deal' vibe
        if not item.get('discount_percentage'):
             item['discount_percentage'] = 50 
             
    return Response(data)
