from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout, get_user_model
# User = get_user_model() - Moved inside functions to avoid AppRegistryNotReady error

from django.db.models import Q, Sum
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from vendor.models import VendorProfile, Product
from .models import VendorApprovalLog, ProductApprovalLog, DeliveryAgentApprovalLog
from deliveryAgent.models import DeliveryAgentProfile
from finance.models import LedgerEntry
from rest_framework.permissions import AllowAny,IsAuthenticated
def is_mainapp_admin(user):
    return True

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin_login')
        if not is_mainapp_admin(request.user):
            return redirect('admin_login')
        return view_func(request, *args, **kwargs)
    return wrapper




from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def admin_login_view(request):
    if request.user.is_authenticated and is_mainapp_admin(request.user):
        return redirect('admin_dashboard')
    
    if request.method == "POST":
        identifier = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=identifier, password=password)

        if not user:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                matching_users = User.objects.filter(username=identifier)
                for potential_user in matching_users:
                    user = authenticate(request, username=potential_user.email, password=password)
                    if user:
                        break
            except Exception:
                pass

        if user:
            login(request, user)
            next_url = request.GET.get('next', 'admin_dashboard')
            return redirect(next_url)
        else:
            error = "Invalid credentials. Please enter your registered email or username."
            return render(request, 'mainApp/admin_login.html', {'error': error})

    return render(request, 'mainApp/admin_login.html')

def admin_logout_view(request):
    logout(request)
    return redirect('admin_login')

@admin_required
def admin_dashboard(request):    
    total_vendors = VendorProfile.objects.count()
    pending_vendors = VendorProfile.objects.filter(approval_status='pending').count()
    approved_vendors = VendorProfile.objects.filter(approval_status='approved').count()
    rejected_vendors = VendorProfile.objects.filter(approval_status='rejected').count()
    blocked_vendors = VendorProfile.objects.filter(is_blocked=True).count()
    
    total_products = Product.objects.count()
    blocked_products = Product.objects.filter(is_blocked=True).count()

    total_agents = DeliveryAgentProfile.objects.count()
    pending_agents = DeliveryAgentProfile.objects.filter(approval_status='pending').count()
    approved_agents = DeliveryAgentProfile.objects.filter(approval_status='approved').count()
    blocked_agents = DeliveryAgentProfile.objects.filter(is_blocked=True).count()

    # Financial Metrics
    from django.db.models import Sum
    from deliveryAgent.models import DeliveryCommission
    
    finance_stats = LedgerEntry.objects.aggregate(
        total_gross=Sum('gross_amount'),
        total_comm=Sum('commission_amount'),
        total_net=Sum('net_amount')
    )
    
    total_delivery_paid = DeliveryCommission.objects.aggregate(
        total=Sum('total_commission')
    )['total'] or 0

    context = {
        'total_vendors': total_vendors,
        'pending_vendors': pending_vendors,
        'approved_vendors': approved_vendors,
        'rejected_vendors': rejected_vendors,
        'blocked_vendors': blocked_vendors,
        'total_products': total_products,
        'blocked_products': blocked_products,
        'total_agents': total_agents,
        'pending_agents': pending_agents,
        'approved_agents': approved_agents,
        'blocked_agents': blocked_agents,
        
        # New Financial Metrics
        'total_platform_commission': finance_stats['total_comm'] or 0,
        'total_vendor_earnings': finance_stats['total_net'] or 0,
        'total_gross_sales': finance_stats['total_gross'] or 0,
        'total_delivery_paid': total_delivery_paid,
    }

    return render(request, 'mainApp/admin_dashboard.html', context)

@admin_required
def manage_vendor_requests(request):    
    status_filter = request.GET.get('status', 'pending')
    
    if status_filter == 'all':
        vendors = VendorProfile.objects.all().order_by('-created_at')
    else:
        vendors = VendorProfile.objects.filter(approval_status=status_filter).order_by('-created_at')

    context = {
        'vendors': vendors,
        'current_status': status_filter,
        'total': vendors.count()
    }

    return render(request, 'mainApp/manage_vendor_requests.html', context)

@admin_required
def vendor_request_detail(request, vendor_id):
    
    vendor = get_object_or_404(VendorProfile, id=vendor_id)
    approval_logs = vendor.approval_logs.all()

    context = {
        'vendor': vendor,
        'approval_logs': approval_logs
    }

    return render(request, 'mainApp/vendor_request_detail.html', context)

@admin_required
def approve_vendor(request, vendor_id):
    
    vendor = get_object_or_404(VendorProfile, id=vendor_id)

    if request.method == 'POST':
        vendor.approval_status = 'approved'
        vendor.is_blocked = False
        vendor.blocked_reason = None
        vendor.rejection_reason = None
        vendor.save()

        user = vendor.user
        user.role = 'vendor'
        user.save()

        VendorApprovalLog.objects.create(
            vendor=vendor,
            admin_user=request.user,
            action='approved',
            reason=request.POST.get('reason', '')
        )

        # Send confirmation email
        try:
            print(f"DEBUG: Attempting to send approval email to {user.email}")
            res = send_mail(
                subject='[ShopSphere] Your Vendor Account has been Approved!',
                message=f'Hello {user.username},\n\nCongratulations! Your vendor account for "{vendor.shop_name}" has been approved by the administrator. You can now login and start adding products.\n\nThank you for joining ShopSphere!',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
            print(f"DEBUG: send_mail result: {res}")
        except Exception as e:
            print(f"DEBUG: Error sending approval email: {str(e)}")
            pass

        return redirect('vendor_request_detail', vendor_id=vendor.id)

    return render(request, 'mainApp/approve_vendor.html', {
        'vendor': vendor
    })

@admin_required
def reject_vendor(request, vendor_id):
    
    vendor = get_object_or_404(VendorProfile, id=vendor_id)

    if request.method == 'POST':
        reason = request.POST.get('reason', 'No reason provided')
        vendor.approval_status = 'rejected'
        vendor.rejection_reason = reason
        vendor.save()

        VendorApprovalLog.objects.create(
            vendor=vendor,
            admin_user=request.user,
            action='rejected',
            reason=reason
        )

        # Send rejection email
        try:
            user = vendor.user
            print(f"DEBUG: Attempting to send rejection email to {user.email}")
            res = send_mail(
                subject='[ShopSphere] Vendor Account Application Update',
                message=f'Hello {user.username},\n\nWe regret to inform you that your vendor account application for "{vendor.shop_name}" has been rejected.\n\nReason: {reason}\n\nPlease contact support if you have any questions.\n\nRegards,\nShopSphere Team',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
            print(f"DEBUG: send_mail result: {res}")
        except Exception as e:
            print(f"DEBUG: Error sending rejection email: {str(e)}")
            pass

        return redirect('vendor_request_detail', vendor_id=vendor.id)

    return render(request, 'mainApp/reject_vendor.html', {
        'vendor': vendor
    })

@admin_required
def manage_vendors(request):    
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    block_filter = request.GET.get('blocked', '')

    vendors = VendorProfile.objects.all()

    if search_query:
        vendors = vendors.filter(
            Q(shop_name__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )

    if status_filter:
        vendors = vendors.filter(approval_status=status_filter)

    if block_filter == 'blocked':
        vendors = vendors.filter(is_blocked=True)
    elif block_filter == 'active':
        vendors = vendors.filter(is_blocked=False)

    vendors = vendors.order_by('-created_at')

    context = {
        'vendors': vendors,
        'search_query': search_query,
        'status_filter': status_filter,
        'block_filter': block_filter,
    }

    return render(request, 'mainApp/manage_vendors.html', context)

@admin_required
def block_vendor(request, vendor_id):    
    vendor = get_object_or_404(VendorProfile, id=vendor_id)

    if request.method == 'POST':
        reason = request.POST.get('reason', 'No reason provided')
        vendor.is_blocked = True
        vendor.blocked_reason = reason
        vendor.save()

        VendorApprovalLog.objects.create(
            vendor=vendor,
            admin_user=request.user,
            action='blocked',
            reason=reason
        )

        # Send blocking email
        try:
            user = vendor.user
            print(f"DEBUG: Attempting to send blocking email to {user.email}")
            res = send_mail(
                subject='[ShopSphere] Your Vendor Account has been Blocked',
                message=f'Hello {user.username},\n\nYour vendor account for "{vendor.shop_name}" has been blocked by the administrator.\n\nReason: {reason}\n\nYou will not be able to manage your shop or products while blocked. Please contact support for more details.\n\nRegards,\nShopSphere Team',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
            print(f"DEBUG: send_mail result: {res}")
        except Exception as e:
            print(f"DEBUG: Error sending blocking email: {str(e)}")
            pass

        vendor.products.update(is_blocked=True, blocked_reason=f"Vendor blocked: {reason}")

        return redirect('vendor_detail', vendor_id=vendor.id)

    return render(request, 'mainApp/block_vendor.html', {
        'vendor': vendor
    })

@admin_required
def unblock_vendor(request, vendor_id):    
    vendor = get_object_or_404(VendorProfile, id=vendor_id)

    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        vendor.is_blocked = False
        vendor.blocked_reason = None
        vendor.save()

        VendorApprovalLog.objects.create(
            vendor=vendor,
            admin_user=request.user,
            action='unblocked',
            reason=reason
        )

        # Send unblocking email
        try:
            user = vendor.user
            print(f"DEBUG: Attempting to send unblocking email to {user.email}")
            res = send_mail(
                subject='[ShopSphere] Your Vendor Account has been Unblocked',
                message=f'Hello {user.username},\n\nGood news! Your vendor account for "{vendor.shop_name}" has been unblocked. You can now resume your sales activities.\n\nWelcome back!\nShopSphere Team',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
            print(f"DEBUG: send_mail result: {res}")
        except Exception as e:
            print(f"DEBUG: Error sending unblocking email: {str(e)}")
            pass

        return redirect('vendor_detail', vendor_id=vendor.id)

    return render(request, 'mainApp/unblock_vendor.html', {
        'vendor': vendor
    })

@admin_required
def vendor_detail(request, vendor_id):    
    vendor = get_object_or_404(VendorProfile, id=vendor_id)
    products = vendor.products.all()
    approval_logs = vendor.approval_logs.all()

    context = {
        'vendor': vendor,
        'products': products,
        'approval_logs': approval_logs,
    }

    return render(request, 'mainApp/vendor_detail.html', context)

@admin_required
def manage_products(request):    
    search_query = request.GET.get('search', '')
    vendor_filter = request.GET.get('vendor', '')
    block_filter = request.GET.get('blocked', '')

    products = Product.objects.all().select_related('vendor')

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if vendor_filter:
        products = products.filter(vendor__id=vendor_filter)

    if block_filter == 'blocked':
        products = products.filter(is_blocked=True)
    elif block_filter == 'active':
        products = products.filter(is_blocked=False)

    products = products.order_by('-created_at')

    vendors = VendorProfile.objects.filter(approval_status='approved').order_by('shop_name')

    context = {
        'products': products,
        'vendors': vendors,
        'search_query': search_query,
        'vendor_filter': vendor_filter,
        'block_filter': block_filter,
    }

    return render(request, 'mainApp/manage_products.html', context)

@admin_required
def product_detail(request, product_id):    
    product = get_object_or_404(Product, id=product_id)
    approval_logs = product.approval_logs.all()

    context = {
        'product': product,
        'vendor': product.vendor,
        'approval_logs': approval_logs,
    }

    return render(request, 'mainApp/product_detail.html', context)

@admin_required
def block_product(request, product_id):
    
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        reason = request.POST.get('reason', 'No reason provided')
        product.is_blocked = True
        product.blocked_reason = reason
        product.save()

        ProductApprovalLog.objects.create(
            product=product,
            admin_user=request.user,
            action='blocked',
            reason=reason
        )

        return redirect('product_detail', product_id=product.id)

    return render(request, 'mainApp/block_product.html', {
        'product': product
    })

@admin_required
def unblock_product(request, product_id):    
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        product.is_blocked = False
        product.blocked_reason = None
        product.save()

        ProductApprovalLog.objects.create(
            product=product,
            admin_user=request.user,
            action='unblocked',
            reason=reason
        )

        return redirect('product_detail', product_id=product.id)

    return render(request, 'mainApp/unblock_product.html', {
        'product': product
    })

@admin_required
def manage_ledgers(request):
    vendor_id = request.GET.get('vendor')
    entry_type = request.GET.get('type')
    
    ledgers = LedgerEntry.objects.all().select_related('vendor', 'order')
    
    if vendor_id:
        ledgers = ledgers.filter(vendor_id=vendor_id)
    if entry_type:
        ledgers = ledgers.filter(entry_type=entry_type)
        
    ledgers = ledgers.order_by('-created_at')
    
    # Aggregates
    totals = ledgers.aggregate(
        gross=Sum('gross_amount'),
        comm=Sum('commission_amount'),
        net=Sum('net_amount')
    )
    
    vendors = VendorProfile.objects.filter(approval_status='approved')
    
    context = {
        'ledgers': ledgers,
        'vendors': vendors,
        'total_gross': totals['gross'] or 0,
        'total_comm': totals['comm'] or 0,
        'total_net': totals['net'] or 0,
        'selected_vendor': vendor_id,
        'selected_type': entry_type,
    }
    
    return render(request, 'mainApp/manage_ledgers.html', context)

@admin_required
def manage_delivery_requests(request):
    status_filter = request.GET.get('status', 'pending')
    
    if status_filter == 'all':
        agents = DeliveryAgentProfile.objects.all().order_by('-created_at')
    else:
        agents = DeliveryAgentProfile.objects.filter(approval_status=status_filter).order_by('-created_at')

    context = {
        'agents': agents,
        'current_status': status_filter,
        'total': agents.count()
    }
    return render(request, 'mainApp/manage_delivery_requests.html', context)

@admin_required
def delivery_request_detail(request, agent_id):
    agent = get_object_or_404(DeliveryAgentProfile, id=agent_id)
    approval_logs = DeliveryAgentApprovalLog.objects.filter(agent=agent)

    context = {
        'agent': agent,
        'approval_logs': approval_logs
    }
    return render(request, 'mainApp/delivery_request_detail.html', context)

@admin_required
def approve_delivery_agent(request, agent_id):
    agent = get_object_or_404(DeliveryAgentProfile, id=agent_id)

    if request.method == 'POST':
        agent.approval_status = 'approved'
        agent.is_blocked = False
        agent.blocked_reason = None
        agent.rejection_reason = None
        agent.approved_at = timezone.now()
        agent.save()

        user = agent.user
        user.role = 'delivery'
        user.save()

        DeliveryAgentApprovalLog.objects.create(
            agent=agent,
            admin_user=request.user,
            action='approved',
            reason=request.POST.get('reason', '')
        )

        # Send confirmation email
        try:
            print(f"DEBUG: Attempting to send agency approval email to {user.email}")
            res = send_mail(
                subject='[ShopSphere] Your Delivery Agent Account has been Approved!',
                message=f'Hello {user.username},\n\nGreat news! Your delivery agent account has been approved. You can now login to the delivery dashboard and start accepting delivery tasks.\n\nWelcome to the team!\nShopSphere',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
            print(f"DEBUG: send_mail result: {res}")
        except Exception as e:
            print(f"DEBUG: Error sending agency approval email: {str(e)}")
            pass
        return redirect('delivery_request_detail', agent_id=agent.id)

    return render(request, 'mainApp/approve_delivery_agent.html', {
        'agent': agent
    })

@admin_required
def reject_delivery_agent(request, agent_id):
    agent = get_object_or_404(DeliveryAgentProfile, id=agent_id)

    if request.method == 'POST':
        reason = request.POST.get('reason', 'No reason provided')
        agent.approval_status = 'rejected'
        agent.rejection_reason = reason
        agent.save()

        DeliveryAgentApprovalLog.objects.create(
            agent=agent,
            admin_user=request.user,
            action='rejected',
            reason=reason
        )

        # Send rejection email
        try:
            user = agent.user
            send_mail(
                subject='[ShopSphere] Delivery Agent Application Update',
                message=f'Hello {user.username},\n\nWe regret to inform you that your delivery agent account application has been rejected.\n\nReason: {reason}\n\nPlease contact support for more information.\n\nRegards,\nShopSphere Team',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass
        return redirect('delivery_request_detail', agent_id=agent.id)

    return render(request, 'mainApp/reject_delivery_agent.html', {
        'agent': agent
    })

@admin_required
def manage_delivery_agents(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    block_filter = request.GET.get('blocked', '')

    agents = DeliveryAgentProfile.objects.all()

    if search_query:
        agents = agents.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )

    if status_filter:
        agents = agents.filter(approval_status=status_filter)

    if block_filter == 'blocked':
        agents = agents.filter(is_blocked=True)
    elif block_filter == 'active':
        agents = agents.filter(is_blocked=False)

    agents = agents.order_by('-created_at')

    context = {
        'agents': agents,
        'search_query': search_query,
        'status_filter': status_filter,
        'block_filter': block_filter
    }
    return render(request, 'mainApp/manage_delivery_agents.html', context)

@admin_required
def block_delivery_agent(request, agent_id):
    agent = get_object_or_404(DeliveryAgentProfile, id=agent_id)
    if request.method == 'POST':
        reason = request.POST.get('reason', 'No reason provided')
        agent.is_blocked = True
        agent.blocked_reason = reason
        agent.save()

        DeliveryAgentApprovalLog.objects.create(
            agent=agent,
            admin_user=request.user,
            action='blocked',
            reason=reason
        )

        # Send blocking email
        try:
            user = agent.user
            send_mail(
                subject='[ShopSphere] Your Delivery Agent Account has been Blocked',
                message=f'Hello {user.username},\n\nYour delivery agent account has been blocked by the administrator.\n\nReason: {reason}\n\nYou will not be able to accept delivery tasks while blocked. Please contact support for more details.\n\nRegards,\nShopSphere Team',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass
        return redirect('manage_delivery_agents')
    return render(request, 'mainApp/block_delivery_agent.html', {'agent': agent})

@admin_required
def unblock_delivery_agent(request, agent_id):
    agent = get_object_or_404(DeliveryAgentProfile, id=agent_id)
    if request.method == 'POST':
        agent.is_blocked = False
        agent.blocked_reason = ''
        agent.save()

        DeliveryAgentApprovalLog.objects.create(
            agent=agent,
            admin_user=request.user,
            action='unblocked'
        )

        # Send unblocking email
        try:
            user = agent.user
            send_mail(
                subject='[ShopSphere] Your Delivery Agent Account has been Unblocked',
                message=f'Hello {user.username},\n\nGood news! Your delivery agent account has been unblocked. You can now resume your delivery activities.\n\nWelcome back!\nShopSphere Team',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass
        return redirect('manage_delivery_agents')
    return render(request, 'mainApp/unblock_delivery_agent.html', {'agent': agent})


@admin_required
def admin_reports(request):
    """Live analytics and reports for the admin dashboard."""
    from django.db.models import Count, Avg
    from django.utils import timezone
    from datetime import timedelta
    from user.models import Order, OrderItem
    from deliveryAgent.models import DeliveryCommission, DeliveryAssignment

    # ── Date range ──────────────────────────────────────────────────────
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    seven_days_ago = today - timedelta(days=7)

    # ── Order Stats ──────────────────────────────────────────────────────
    order_qs = Order.objects.all()
    total_orders = order_qs.count()
    orders_today = order_qs.filter(created_at__date=today).count()
    orders_this_week = order_qs.filter(created_at__date__gte=seven_days_ago).count()
    orders_this_month = order_qs.filter(created_at__date__gte=thirty_days_ago).count()

    # Status breakdown
    order_status_breakdown = list(
        order_qs.values('status')
                .annotate(count=Count('id'))
                .order_by('-count')
    )

    # Payment status breakdown
    payment_status_breakdown = list(
        order_qs.values('payment_status')
                .annotate(count=Count('id'))
                .order_by('-count')
    )

    # ── Revenue (from completed/delivered orders) ─────────────────────
    completed_orders = order_qs.filter(payment_status='completed')
    total_revenue = completed_orders.aggregate(total=Sum('total_amount'))['total'] or 0
    avg_order_value = completed_orders.aggregate(avg=Avg('total_amount'))['avg'] or 0

    # Revenue today / this week / this month
    revenue_today = completed_orders.filter(created_at__date=today).aggregate(t=Sum('total_amount'))['t'] or 0
    revenue_week = completed_orders.filter(created_at__date__gte=seven_days_ago).aggregate(t=Sum('total_amount'))['t'] or 0
    revenue_month = completed_orders.filter(created_at__date__gte=thirty_days_ago).aggregate(t=Sum('total_amount'))['t'] or 0

    # ── Daily Revenue Trend (last 30 days) ───────────────────────────
    from django.db.models.functions import TruncDate
    daily_revenue = list(
        completed_orders.filter(created_at__date__gte=thirty_days_ago)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(revenue=Sum('total_amount'), orders=Count('id'))
        .order_by('day')
    )

    # ── Finance ──────────────────────────────────────────────────────
    finance_agg = LedgerEntry.objects.aggregate(
        total_gross=Sum('gross_amount'),
        total_commission=Sum('commission_amount'),
        total_net=Sum('net_amount'),
    )
    total_platform_commission = finance_agg['total_commission'] or 0

    # ── Top Vendors by Net Earnings ──────────────────────────────────
    top_vendors = list(
        LedgerEntry.objects.filter(entry_type='REVENUE')
        .values('vendor__shop_name', 'vendor__id')
        .annotate(
            total_gross=Sum('gross_amount'),
            total_commission=Sum('commission_amount'),
            total_net=Sum('net_amount'),
            order_count=Count('order', distinct=True)
        )
        .order_by('-total_net')[:10]
    )

    # ── Most Ordered Products ─────────────────────────────────────────
    top_products = list(
        OrderItem.objects.values('product_name')
        .annotate(
            total_qty=Sum('quantity'),
            total_revenue=Sum('subtotal'),
            order_count=Count('order', distinct=True),
        )
        .order_by('-total_qty')[:10]
    )

    # ── Delivery Agent Performance ────────────────────────────────────
    total_commissions_paid = DeliveryCommission.objects.filter(status='paid').aggregate(t=Sum('total_commission'))['t'] or 0
    total_commissions_pending = DeliveryCommission.objects.filter(status__in=['pending', 'approved']).aggregate(t=Sum('total_commission'))['t'] or 0
    total_deliveries_done = DeliveryAssignment.objects.filter(status='delivered').count()
    total_deliveries_failed = DeliveryAssignment.objects.filter(status='failed').count()

    # ── Vendor Stats ──────────────────────────────────────────────────
    total_vendors = VendorProfile.objects.count()
    approved_vendors = VendorProfile.objects.filter(approval_status='approved').count()
    blocked_vendors = VendorProfile.objects.filter(is_blocked=True).count()

    # ── Product Stats ─────────────────────────────────────────────────
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_blocked=False).count()
    blocked_products = Product.objects.filter(is_blocked=True).count()

    context = {
        # Order stats
        'total_orders': total_orders,
        'orders_today': orders_today,
        'orders_this_week': orders_this_week,
        'orders_this_month': orders_this_month,
        'order_status_breakdown': order_status_breakdown,
        'payment_status_breakdown': payment_status_breakdown,

        # Revenue
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value,
        'revenue_today': revenue_today,
        'revenue_week': revenue_week,
        'revenue_month': revenue_month,
        'daily_revenue': daily_revenue,

        # Finance
        'total_platform_commission': total_platform_commission,
        'total_gross': finance_agg['total_gross'] or 0,
        'total_net': finance_agg['total_net'] or 0,

        # Vendors & products
        'total_vendors': total_vendors,
        'approved_vendors': approved_vendors,
        'blocked_vendors': blocked_vendors,
        'total_products': total_products,
        'active_products': active_products,
        'blocked_products': blocked_products,
        'top_vendors': top_vendors,

        # Products
        'top_products': top_products,

        # Delivery
        'total_commissions_paid': total_commissions_paid,
        'total_commissions_pending': total_commissions_pending,
        'total_deliveries_done': total_deliveries_done,
        'total_deliveries_failed': total_deliveries_failed,

        # Meta
        'report_date': today,
    }

    return render(request, 'mainApp/manage_reports.html', context)
@admin_required
def manage_tracking(request):
    from deliveryAgent.models import DeliveryAssignment
    
    status_filter = request.GET.get('status', 'all')
    assignments = DeliveryAssignment.objects.all().select_related('agent', 'agent__user', 'order', 'order__user')
    
    if status_filter != 'all':
        assignments = assignments.filter(status=status_filter)
        
    context = {
        'assignments': assignments,
        'current_status': status_filter,
    }
    return render(request, 'mainApp/manage_tracking.html', context)

@admin_required
def tracking_detail(request, assignment_id):
    from deliveryAgent.models import DeliveryAssignment, DeliveryTracking
    
    assignment = get_object_or_404(DeliveryAssignment.objects.select_related('agent', 'agent__user', 'order', 'order__user'), id=assignment_id)
    tracking_history = DeliveryTracking.objects.filter(delivery_assignment=assignment).order_by('-tracked_at')
    
    context = {
        'assignment': assignment,
        'tracking_history': tracking_history,
    }
    return render(request, 'mainApp/tracking_detail.html', context)
