from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.permissions import BasePermission

class IsStaffOrSuperuser(BasePermission):
    """
    Allows access to users who are staff (is_staff=True) OR superusers (is_superuser=True).
    DRF's built-in IsAdminUser only checks is_staff, which can leave out superusers
    whose is_staff flag was not explicitly set.
    """
    message = "You must be an admin/staff user to access this endpoint."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_staff or request.user.is_superuser)
        )

from django.contrib.auth import get_user_model

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
# User = get_user_model() - Moved inside functions to avoid AppRegistryNotReady error

from django.db.models import Q
from finance.models import GlobalCommission, CategoryCommission
from vendor.models import VendorProfile, Product
from .models import VendorApprovalLog, ProductApprovalLog, DeliveryAgentApprovalLog
from deliveryAgent.models import DeliveryAgentProfile, DeliveryAssignment
from deliveryAgent.serializers import DeliveryAssignmentDetailSerializer, DeliveryAssignmentListSerializer
from .serializers import (
    VendorApprovalLogSerializer, ProductApprovalLogSerializer,
    AdminVendorDetailSerializer, AdminProductDetailSerializer,
    AdminVendorListSerializer, AdminProductListSerializer,
    ApproveVendorSerializer, RejectVendorSerializer,
    BlockVendorSerializer, UnblockVendorSerializer,
    BlockProductSerializer, UnblockProductSerializer,
    AdminDeliveryAgentDetailSerializer, AdminDeliveryAgentListSerializer,
    ApproveDeliveryAgentSerializer, RejectDeliveryAgentSerializer,
    BlockDeliveryAgentSerializer, UnblockDeliveryAgentSerializer,
    AdminOrderListSerializer, AdminOrderDetailSerializer
)
from user.models import Order


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class AdminLoginRequiredMixin:
    """Ensure user is admin (staff or superuser)"""
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]

class VendorRequestViewSet(AdminLoginRequiredMixin, viewsets.ModelViewSet):
    """Manage vendor approval requests"""
    queryset = VendorProfile.objects.filter(approval_status='pending')
    serializer_class = AdminVendorDetailSerializer
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]
    
    def list(self, request, *args, **kwargs):
        queryset = VendorProfile.objects.filter(approval_status='pending')
        
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(shop_name__icontains=search) |
                Q(user__email__icontains=search)
            )
        
        serializer = AdminVendorDetailSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        vendor = self.get_object()
        
        if vendor.approval_status != 'pending':
            return Response({
                'error': 'Only pending vendors can be approved'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ApproveVendorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        vendor.approval_status = 'approved'
        vendor.save()
        
        VendorApprovalLog.objects.create(
            vendor=vendor,
            admin_user=request.user,
            action='approved',
            reason=serializer.validated_data.get('reason', '')
        )
        
        # Send confirmation email
        try:
            user = vendor.user
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
        
        return Response({
            'message': 'Vendor approved successfully',
            'vendor': AdminVendorDetailSerializer(vendor).data
        })
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        vendor = self.get_object()
        
        if vendor.approval_status != 'pending':
            return Response({
                'error': 'Only pending vendors can be rejected'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = RejectVendorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        vendor.approval_status = 'rejected'
        vendor.rejection_reason = serializer.validated_data['reason']
        vendor.save()
        
        VendorApprovalLog.objects.create(
            vendor=vendor,
            admin_user=request.user,
            action='rejected',
            reason=serializer.validated_data['reason']
        )
        
        # Send rejection email
        try:
            user = vendor.user
            print(f"DEBUG: Attempting to send rejection email to {user.email}")
            res = send_mail(
                subject='[ShopSphere] Vendor Account Application Update',
                message=f'Hello {user.username},\n\nWe regret to inform you that your vendor account application for "{vendor.shop_name}" has been rejected.\n\nReason: {serializer.validated_data["reason"]}\n\nPlease contact support if you have any questions.\n\nRegards,\nShopSphere Team',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
            print(f"DEBUG: send_mail result: {res}")
        except Exception as e:
            print(f"DEBUG: Error sending rejection email: {str(e)}")
            pass
        
        return Response({
            'message': 'Vendor rejected successfully',
            'vendor': AdminVendorDetailSerializer(vendor).data
        })

class VendorManagementViewSet(AdminLoginRequiredMixin, viewsets.ModelViewSet):
    queryset = VendorProfile.objects.all()
    serializer_class = AdminVendorListSerializer
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]
    
    def list(self, request, *args, **kwargs):
        queryset = VendorProfile.objects.all()
        
        status_filter = request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(approval_status=status_filter)
        
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(shop_name__icontains=search) |
                Q(user__email__icontains=search) |
                Q(user__username__icontains=search)
            )
        
        blocked_filter = request.query_params.get('blocked', None)
        if blocked_filter == 'true':
            queryset = queryset.filter(is_blocked=True)
        elif blocked_filter == 'false':
            queryset = queryset.filter(is_blocked=False)
        
        serializer = AdminVendorListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        vendor = self.get_object()
        serializer = AdminVendorDetailSerializer(vendor, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def detail(self, request, pk=None):
        vendor = self.get_object()
        serializer = AdminVendorDetailSerializer(vendor, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        vendor = self.get_object()
        
        serializer = BlockVendorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        vendor.is_blocked = True
        vendor.blocked_reason = serializer.validated_data['reason']
        vendor.save()
        
        Product.objects.filter(vendor=vendor).update(is_blocked=True)
        
        VendorApprovalLog.objects.create(
            vendor=vendor,
            admin_user=request.user,
            action='blocked',
            reason=serializer.validated_data['reason']
        )
        
        # Send blocking email
        try:
            user = vendor.user
            print(f"DEBUG: Attempting to send blocking email to {user.email}")
            res = send_mail(
                subject='[ShopSphere] Your Vendor Account has been Blocked',
                message=f'Hello {user.username},\n\nYour vendor account for "{vendor.shop_name}" has been blocked by the administrator.\n\nReason: {serializer.validated_data["reason"]}\n\nYou will not be able to manage your shop or products while blocked. Please contact support for more details.\n\nRegards,\nShopSphere Team',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
            print(f"DEBUG: send_mail result: {res}")
        except Exception as e:
            print(f"DEBUG: Error sending blocking email: {str(e)}")
            pass
        
        return Response({
            'message': 'Vendor blocked successfully',
            'vendor': AdminVendorDetailSerializer(vendor, context={'request': request}).data
        })
    
    @action(detail=True, methods=['post'])
    def unblock(self, request, pk=None):
        vendor = self.get_object()
        
        serializer = UnblockVendorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        vendor.is_blocked = False
        vendor.blocked_reason = ''
        vendor.save()
        
        VendorApprovalLog.objects.create(
            vendor=vendor,
            admin_user=request.user,
            action='unblocked',
            reason=serializer.validated_data.get('reason', '')
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
        
        return Response({
            'message': 'Vendor unblocked successfully',
            'vendor': AdminVendorDetailSerializer(vendor, context={'request': request}).data
        })

class ProductManagementViewSet(AdminLoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Product.objects.select_related('vendor').prefetch_related('images').all()
    serializer_class = AdminProductListSerializer
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]
    pagination_class = None  # We handle pagination manually below

    def list(self, request, *args, **kwargs):
        from django.core.paginator import Paginator
        PAGE_SIZE = 50

        queryset = Product.objects.select_related('vendor').prefetch_related('images').all()

        # Status filter
        status_filter = request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Blocked filter
        blocked_filter = request.query_params.get('blocked', None)
        if blocked_filter == 'true':
            queryset = queryset.filter(is_blocked=True)
        elif blocked_filter == 'false':
            queryset = queryset.filter(is_blocked=False)

        # Smart search: pure integer → exact product-ID; otherwise name / vendor name contains
        search = (request.query_params.get('search', '') or '').strip()
        if search:
            if search.isdigit():
                queryset = queryset.filter(id=int(search))
            else:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(vendor__shop_name__icontains=search)
                )

        # Vendor filter
        vendor_id = request.query_params.get('vendor_id', None)
        if vendor_id:
            queryset = queryset.filter(vendor_id=vendor_id)

        queryset = queryset.order_by('-created_at')

        # Server-side pagination
        page_number = int(request.query_params.get('page', 1))
        paginator = Paginator(queryset, PAGE_SIZE)
        page_obj = paginator.get_page(page_number)

        serializer = AdminProductListSerializer(page_obj.object_list, many=True, context={'request': request})
        return Response({
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'results': serializer.data,
        })
    
    @action(detail=True, methods=['get'])
    def detail(self, request, pk=None):
        product = self.get_object()
        serializer = AdminProductDetailSerializer(product, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        product = self.get_object()
        
        serializer = BlockProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product.is_blocked = True
        product.blocked_reason = serializer.validated_data['reason']
        product.save()
        
        ProductApprovalLog.objects.create(
            product=product,
            admin_user=request.user,
            action='blocked',
            reason=serializer.validated_data['reason']
        )
        
        return Response({
            'message': 'Product blocked successfully',
            'product': AdminProductDetailSerializer(product, context={'request': request}).data
        })
    
    @action(detail=True, methods=['post'])
    def unblock(self, request, pk=None):
        product = self.get_object()
        
        serializer = UnblockProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product.is_blocked = False
        product.blocked_reason = ''
        product.save()
        
        ProductApprovalLog.objects.create(
            product=product,
            admin_user=request.user,
            action='unblocked',
            reason=serializer.validated_data.get('reason', '')
        )
        
        return Response({
            'message': 'Product unblocked successfully',
            'product': AdminProductDetailSerializer(product, context={'request': request}).data
        })

class DeliveryRequestViewSet(AdminLoginRequiredMixin, viewsets.ModelViewSet):
    """Manage delivery agent approval requests"""
    queryset = DeliveryAgentProfile.objects.filter(approval_status='pending')
    serializer_class = AdminDeliveryAgentDetailSerializer
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]

    def get_object(self):
        """
        Override to look up by pk across ALL agents (not just pending).
        The queryset filter is only for the list view — approve/reject actions
        must be able to find any agent by ID regardless of current status.
        """
        pk = self.kwargs.get('pk')
        try:
            agent = DeliveryAgentProfile.objects.get(pk=pk)
        except DeliveryAgentProfile.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound(detail=f"Delivery agent with ID {pk} not found.")
        self.check_object_permissions(self.request, agent)
        return agent

    def list(self, request, *args, **kwargs):
        queryset = DeliveryAgentProfile.objects.filter(approval_status='pending')
        
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(user__email__icontains=search) |
                Q(phone_number__icontains=search)
            )
        
        serializer = AdminDeliveryAgentDetailSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        agent = self.get_object()
        
        if agent.approval_status != 'pending':
            return Response({'error': 'Only pending agents can be approved'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ApproveDeliveryAgentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        agent.approval_status = 'approved'
        agent.approved_at = timezone.now()
        agent.save()
        
        DeliveryAgentApprovalLog.objects.create(
            agent=agent,
            admin_user=request.user,
            action='approved',
            reason=serializer.validated_data.get('reason', '')
        )
        
        # Send confirmation email
        try:
            user = agent.user
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
        
        return Response({
            'message': 'Delivery agent approved successfully',
            'agent': AdminDeliveryAgentDetailSerializer(agent, context={'request': request}).data
        })
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        agent = self.get_object()
        
        if agent.approval_status != 'pending':
            return Response({'error': 'Only pending agents can be rejected'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = RejectDeliveryAgentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        agent.approval_status = 'rejected'
        agent.rejection_reason = serializer.validated_data['reason']
        agent.save()
        
        DeliveryAgentApprovalLog.objects.create(
            agent=agent,
            admin_user=request.user,
            action='rejected',
            reason=serializer.validated_data['reason']
        )
        
        # Send rejection email
        try:
            user = agent.user
            print(f"DEBUG: Attempting to send agent rejection email to {user.email}")
            res = send_mail(
                subject='[ShopSphere] Delivery Agent Application Update',
                message=f'Hello {user.username},\n\nWe regret to inform you that your delivery agent account application has been rejected.\n\nReason: {serializer.validated_data["reason"]}\n\nPlease contact support for more information.\n\nRegards,\nShopSphere Team',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
            print(f"DEBUG: send_mail result: {res}")
        except Exception as e:
            print(f"DEBUG: Error sending agent rejection email: {str(e)}")
            pass
        
        return Response({
            'message': 'Delivery agent rejected successfully',
            'agent': AdminDeliveryAgentDetailSerializer(agent, context={'request': request}).data
        })

class DeliveryAgentManagementViewSet(AdminLoginRequiredMixin, viewsets.ModelViewSet):
    queryset = DeliveryAgentProfile.objects.all()
    serializer_class = AdminDeliveryAgentListSerializer
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]
    
    def list(self, request, *args, **kwargs):
        queryset = DeliveryAgentProfile.objects.all()
        
        status_filter = request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(approval_status=status_filter)
        
        blocked_filter = request.query_params.get('blocked', None)
        if blocked_filter == 'true':
            queryset = queryset.filter(is_blocked=True)
        
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(user__email__icontains=search) |
                Q(phone_number__icontains=search)
            )
        
        serializer = AdminDeliveryAgentListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        agent = self.get_object()
        serializer = AdminDeliveryAgentDetailSerializer(agent, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        agent = self.get_object()
        serializer = BlockDeliveryAgentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        agent.is_blocked = True
        agent.blocked_reason = serializer.validated_data['reason']
        agent.save()
        
        DeliveryAgentApprovalLog.objects.create(
            agent=agent,
            admin_user=request.user,
            action='blocked',
            reason=serializer.validated_data['reason']
        )
        
        # Send blocking email
        try:
            user = agent.user
            print(f"DEBUG: Attempting to send agent blocking email to {user.email}")
            res = send_mail(
                subject='[ShopSphere] Your Delivery Agent Account has been Blocked',
                message=f'Hello {user.username},\n\nYour delivery agent account has been blocked by the administrator.\n\nReason: {serializer.validated_data["reason"]}\n\nYou will not be able to accept delivery tasks while blocked. Please contact support for more details.\n\nRegards,\nShopSphere Team',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
            print(f"DEBUG: send_mail result: {res}")
        except Exception as e:
            print(f"DEBUG: Error sending agent blocking email: {str(e)}")
            pass
        
        return Response({
            'message': 'Agent blocked successfully',
            'agent': AdminDeliveryAgentDetailSerializer(agent, context={'request': request}).data
        })
    
    @action(detail=True, methods=['post'])
    def unblock(self, request, pk=None):
        agent = self.get_object()
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
            print(f"DEBUG: Attempting to send agent unblocking email to {user.email}")
            res = send_mail(
                subject='[ShopSphere] Your Delivery Agent Account has been Unblocked',
                message=f'Hello {user.username},\n\nGood news! Your delivery agent account has been unblocked. You can now resume your delivery activities.\n\nWelcome back!\nShopSphere Team',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )
            print(f"DEBUG: send_mail result: {res}")
        except Exception as e:
            print(f"DEBUG: Error sending agent unblocking email: {str(e)}")
            pass
        
        return Response({
            'message': 'Agent unblocked successfully',
            'agent': AdminDeliveryAgentDetailSerializer(agent, context={'request': request}).data
        })

from django.utils import timezone


class DashboardView(AdminLoginRequiredMixin, generics.GenericAPIView):
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]
    
    def get(self, request):
        from django.db.models import Sum
        from user.models import Order
        
        total_vendors = VendorProfile.objects.count()
        pending_vendors = VendorProfile.objects.filter(approval_status='pending').count()
        approved_vendors = VendorProfile.objects.filter(approval_status='approved').count()
        blocked_vendors = VendorProfile.objects.filter(is_blocked=True).count()
        
        total_products = Product.objects.count()
        active_products = Product.objects.filter(status='active').count()
        inactive_products = Product.objects.filter(status='inactive').count()
        blocked_products = Product.objects.filter(is_blocked=True).count()
        
        total_agents = DeliveryAgentProfile.objects.count()
        pending_agents = DeliveryAgentProfile.objects.filter(approval_status='pending').count()
        approved_agents = DeliveryAgentProfile.objects.filter(approval_status='approved').count()
        blocked_agents = DeliveryAgentProfile.objects.filter(is_blocked=True).count()

        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        delivered_orders = Order.objects.filter(status='delivered').count()
        cancelled_orders = Order.objects.filter(status='cancelled').count()
        
        # User/Customer stats
        User = get_user_model()
        total_customers = User.objects.filter(role='customer').count()
        active_customers = User.objects.filter(role='customer', is_blocked=False).count()
        blocked_customers = User.objects.filter(role='customer', is_blocked=True).count()

        # Deletion requests count
        deletion_requests = VendorProfile.objects.filter(is_deletion_requested=True).count() + \
                           DeliveryAgentProfile.objects.filter(is_deletion_requested=True).count()
        
        # Basic revenue for dashboard quick-view
        revenue_summary = Order.objects.filter(payment_status='completed').aggregate(
            total=Sum('total_amount'),
        )
        
        return Response({
            'vendors': {
                'total': total_vendors,
                'pending': pending_vendors,
                'approved': approved_vendors,
                'blocked': blocked_vendors
            },
            'products': {
                'total': total_products,
                'active': active_products,
                'inactive': inactive_products,
                'blocked': blocked_products
            },
            'agents': {
                'total': total_agents,
                'pending': pending_agents,
                'approved': approved_agents,
                'blocked': blocked_agents
            },
            'customers': {
                'total': total_customers,
                'active': active_customers,
                'blocked': blocked_customers
            },
            'orders': {
                'total': total_orders,
                'pending': pending_orders,
                'delivered': delivered_orders,
                'cancelled': cancelled_orders
            },
            'deletion_requests': deletion_requests,
            'total_revenue': float(revenue_summary['total'] or 0)
        })




# ═══════════════════ REPORTS API ═══════════════════


from rest_framework.views import APIView

class ReportsView(APIView):
    """
    GET /superAdmin/api/reports/
    Returns live platform analytics for the React admin dashboard.
    Requires superuser / staff privileges.
    """
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]

    def get(self, request):
        from django.db.models import Count, Avg, Sum
        from django.db.models.functions import TruncDate
        from django.utils import timezone
        from datetime import timedelta
        from user.models import Order, OrderItem
        from deliveryAgent.models import DeliveryCommission, DeliveryAssignment, DeliveryAgentProfile
        from finance.models import LedgerEntry

        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        seven_days_ago = today - timedelta(days=7)

        # ── Orders ───────────────────────────────
        order_qs = Order.objects.all()
        completed_qs = order_qs.filter(payment_status='completed')

        order_status_breakdown = list(
            order_qs.values('status').annotate(count=Count('id')).order_by('-count')
        )
        payment_status_breakdown = list(
            order_qs.values('payment_status').annotate(count=Count('id')).order_by('-count')
        )

        # ── Revenue ───────────────────────────────
        total_revenue = float(completed_qs.aggregate(t=Sum('total_amount'))['t'] or 0)
        avg_order_value = float(completed_qs.aggregate(a=Avg('total_amount'))['a'] or 0)
        revenue_today = float(completed_qs.filter(created_at__date=today).aggregate(t=Sum('total_amount'))['t'] or 0)
        revenue_week = float(completed_qs.filter(created_at__date__gte=seven_days_ago).aggregate(t=Sum('total_amount'))['t'] or 0)
        revenue_month = float(completed_qs.filter(created_at__date__gte=thirty_days_ago).aggregate(t=Sum('total_amount'))['t'] or 0)

        # ── Daily trend ───────────────────────────
        daily_revenue = list(
            completed_qs.filter(created_at__date__gte=thirty_days_ago)
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(revenue=Sum('total_amount'), orders=Count('id'))
            .order_by('day')
        )
        for d in daily_revenue:
            d['day'] = d['day'].strftime('%d %b')
            d['revenue'] = float(d['revenue'])

        # ── Finance ───────────────────────────────
        finance_agg = LedgerEntry.objects.aggregate(
            total_gross=Sum('gross_amount'),
            total_commission=Sum('commission_amount'),
            total_net=Sum('net_amount'),
        )

        # ── Top Vendors ───────────────────────────
        top_vendors = list(
            LedgerEntry.objects.filter(entry_type='REVENUE')
            .values('vendor__shop_name')
            .annotate(
                total_gross=Sum('gross_amount'),
                total_commission=Sum('commission_amount'),
                total_net=Sum('net_amount'),
                order_count=Count('order', distinct=True)
            )
            .order_by('-total_net')[:10]
        )
        for v in top_vendors:
            for k in ['total_gross', 'total_commission', 'total_net']:
                v[k] = float(v[k] or 0)

        # ── Top Products ──────────────────────────
        top_products = list(
            OrderItem.objects.values('product_name')
            .annotate(
                total_qty=Sum('quantity'),
                total_revenue=Sum('subtotal'),
                order_count=Count('order', distinct=True),
            )
            .order_by('-total_qty')[:10]
        )
        for p in top_products:
            p['total_revenue'] = float(p['total_revenue'] or 0)

        # ── Delivery ──────────────────────────────
        total_commissions_paid = float(DeliveryCommission.objects.filter(status='paid').aggregate(t=Sum('total_commission'))['t'] or 0)
        total_commissions_pending = float(DeliveryCommission.objects.filter(status__in=['pending', 'approved']).aggregate(t=Sum('total_commission'))['t'] or 0)
        total_deliveries_done = DeliveryAssignment.objects.filter(status='delivered').count()
        total_deliveries_failed = DeliveryAssignment.objects.filter(status='failed').count()

        # ── Vendors & Products ────────────────────
        total_vendors = VendorProfile.objects.count()
        approved_vendors = VendorProfile.objects.filter(approval_status='approved').count()
        blocked_vendors = VendorProfile.objects.filter(is_blocked=True).count()
        total_products = Product.objects.count()
        active_products = Product.objects.filter(is_blocked=False).count()
        blocked_products = Product.objects.filter(is_blocked=True).count()
        total_agents = DeliveryAgentProfile.objects.count()
        approved_agents = DeliveryAgentProfile.objects.filter(approval_status='approved').count()

        # ── User Growth ───────────────────────────
        User = get_user_model()
        total_users = User.objects.filter(role='customer').count()
        new_users_today = User.objects.filter(role='customer', date_joined__date=today).count()
        new_users_week = User.objects.filter(role='customer', date_joined__date__gte=seven_days_ago).count()
        
        user_growth = list(
            User.objects.filter(role='customer', date_joined__date__gte=thirty_days_ago)
            .annotate(day=TruncDate('date_joined'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )
        for u in user_growth:
            u['day'] = u['day'].strftime('%d %b')

        return Response({
            # Orders
            'total_orders': order_qs.count(),
            'orders_today': order_qs.filter(created_at__date=today).count(),
            'orders_this_week': order_qs.filter(created_at__date__gte=seven_days_ago).count(),
            'orders_this_month': order_qs.filter(created_at__date__gte=thirty_days_ago).count(),
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
            'total_gross': float(finance_agg['total_gross'] or 0),
            'total_platform_commission': float(finance_agg['total_commission'] or 0),
            'total_net': float(finance_agg['total_net'] or 0),

            # Vendors & Products
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
            'total_delivery_commissions_paid': total_commissions_paid,
            'total_delivery_commissions_pending': total_commissions_pending,
            'total_deliveries_done': total_deliveries_done,
            'total_deliveries_failed': total_deliveries_failed,
            'total_agents': total_agents,
            'approved_agents': approved_agents,
            
            # User Growth (New)
            'total_customers': total_users,
            'new_users_today': new_users_today,
            'new_users_week': new_users_week,
            'user_growth': user_growth,

            # Meta
            'report_date': str(today),
        })


class UserManagementView(APIView):
    """
    GET /superAdmin/api/users/  — Customers only, with live risk scores.
    Risk score 0-100 derived from:
      - Cancellation rate  → up to 40 pts
      - Return rate        → up to 30 pts
      - Failed payments    → up to 30 pts
    """
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]

    def get(self, request):
        from django.db.models import Count, Q
        from user.models import Order, OrderReturn
        User = get_user_model()

        # Customers only
        qs = User.objects.filter(
            is_superuser=False, is_staff=False, role='customer'
        ).order_by('-date_joined')

        # Optional search
        search = request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(email__icontains=search) | Q(username__icontains=search)
            )

        # Optional status filter
        status_filter = request.query_params.get('status', '').strip().upper()
        if status_filter == 'BLOCKED':
            qs = qs.filter(is_blocked=True)
        elif status_filter == 'ACTIVE':
            qs = qs.filter(is_blocked=False)

        # Aggregate stats bases on full customer set (before search/status filters)
        base_customers = User.objects.filter(
            is_superuser=False, is_staff=False, role='customer'
        )
        total = base_customers.count()
        active_count = base_customers.filter(is_blocked=False).count()
        blocked_count = base_customers.filter(is_blocked=True).count()

        # Pre-fetch order stats per user for efficient risk scoring
        order_stats = {
            row['user_id']: row
            for row in Order.objects.values('user_id').annotate(
                total=Count('id'),
                cancelled=Count('id', filter=Q(status='cancelled')),
                failed_payments=Count('id', filter=Q(payment_status='failed')),
            )
        }
        # Pre-fetch return counts per user
        return_counts = {
            row['user_id']: row['returns']
            for row in OrderReturn.objects.values('user_id').annotate(returns=Count('id'))
        }

        users = []
        for u in qs:
            stats = order_stats.get(u.id, {})
            total_orders = stats.get('total', 0)
            cancelled = stats.get('cancelled', 0)
            failed_pay = stats.get('failed_payments', 0)
            returns = return_counts.get(u.id, 0)

            # ── Risk score ────────────────────────────────────────────────
            # 1. Cancellation rate → 0-40 pts
            cancel_rate = (cancelled / total_orders) if total_orders else 0
            cancel_score = round(cancel_rate * 40)

            # 2. Return rate → 0-30 pts
            return_rate = (returns / total_orders) if total_orders else 0
            return_score = round(return_rate * 30)

            # 3. Failed payments → 0-30 pts (10 pts each, capped at 30)
            payment_score = min(failed_pay * 10, 30)

            risk_score = min(cancel_score + return_score + payment_score, 100)
            # ─────────────────────────────────────────────────────────────

            users.append({
                'id': u.id,
                'name': u.username or u.email.split('@')[0],
                'email': u.email,
                'role': u.role,
                'status': 'BLOCKED' if u.is_blocked else 'ACTIVE',
                'blocked_reason': u.blocked_reason or '',
                'joinDate': u.date_joined.strftime('%Y-%m-%d'),
                'is_active': u.is_active,
                # Order activity
                'total_orders': total_orders,
                'cancelled_orders': cancelled,
                'return_requests': returns,
                'failed_payments': failed_pay,
                # Risk
                'riskScore': risk_score,
            })

        return Response({
            'users': users,
            'total': total,
            'active': active_count,
            'blocked': blocked_count,
        })


class UserBlockToggleView(APIView):
    """
    POST /superAdmin/api/users/{id}/toggle-block/
    Body: { "action": "BLOCK"|"UNBLOCK", "reason": "optional" }
    """
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]

    def post(self, request, pk):
        User = get_user_model()
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if user.is_superuser or user.is_staff:
            return Response({'error': 'Cannot modify admin accounts'}, status=status.HTTP_400_BAD_REQUEST)

        action = request.data.get('action', '').upper()
        reason = request.data.get('reason', '')

        if action == 'BLOCK':
            user.is_blocked = True
            user.blocked_reason = reason or 'Blocked by superadmin'
            user.save()
            return Response({
                'message': f'{user.email} has been blocked.',
                'status': 'BLOCKED',
            })
        elif action == 'UNBLOCK':
            user.is_blocked = False
            user.blocked_reason = ''
            user.save()
            return Response({
                'message': f'{user.email} access has been restored.',
                'status': 'ACTIVE',
            })
        else:
            return Response({'error': 'Invalid action. Use BLOCK or UNBLOCK.'}, status=status.HTTP_400_BAD_REQUEST)


# ===============================================
#     ADMIN: Trigger Auto-Assignment for an Order
# ===============================================

class TriggerAssignmentView(APIView):
    """
    POST /superAdmin/api/trigger-assignment/{order_id}/
    Manually trigger auto-assignment for a specific order.
    """
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]

    def post(self, request, order_id):
        from user.models import Order
        from deliveryAgent.services import auto_assign_order

        try:
            order = Order.objects.select_related('delivery_address').get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if already assigned
        if hasattr(order, 'delivery_assignment'):
            assignment = order.delivery_assignment
            return Response({
                'message': f'Order #{order_id} is already assigned to {assignment.agent.user.username}.',
                'agent': assignment.agent.user.username,
                'status': assignment.status,
            }, status=status.HTTP_200_OK)

        try:
            assignment = auto_assign_order(order)

            if assignment:
                return Response({
                    'message': f'Order #{order_id} assigned to {assignment.agent.user.username}',
                    'assignment_id': assignment.id,
                    'agent': assignment.agent.user.username,
                    'delivery_city': assignment.delivery_city,
                    'estimated_date': str(assignment.estimated_delivery_date),
                    'delivery_fee': str(assignment.delivery_fee),
                })
            else:
                return Response({
                    'message': 'No available agents found for this order.',
                    'order_id': order_id,
                    'delivery_city': order.delivery_address.city if order.delivery_address else 'Unknown',
                }, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': f"Assignment Logic Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UnassignedOrdersView(APIView):
    """
    GET /superAdmin/api/unassigned-orders/
    Lists all paid orders that have no DeliveryAssignment yet,
    so admin can manually trigger assignment.
    """
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]

    def get(self, request):
        from deliveryAgent.services import get_unassigned_confirmed_orders

        qs = get_unassigned_confirmed_orders()
        orders = []
        for o in qs:
            addr = o.delivery_address
            orders.append({
                'id': o.id,
                'order_number': o.order_number,
                'status': o.status,
                'payment_status': o.payment_status,
                'total_amount': float(o.total_amount),
                'created_at': o.created_at.strftime('%Y-%m-%d %H:%M'),
                'delivery_city': addr.city if addr else '—',
                'delivery_state': addr.state if addr else '—',
                'customer': o.user.email,
            })
        return Response({'orders': orders, 'count': len(orders)})


class AdminOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin-only viewset to manage all orders.
    """
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]
    queryset = Order.objects.all().select_related('user', 'delivery_address')
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return AdminOrderListSerializer
        return AdminOrderDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset().exclude(status__in=['pending', 'confirmed'])
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(order_number__icontains=search) |
                Q(user__email__icontains=search)
            )
        return queryset


class AdminOrderTrackingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin-only viewset to monitor all delivery assignments and their tracking history.
    """
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]
    
    queryset = DeliveryAssignment.objects.all().select_related('agent', 'agent__user', 'order', 'order__user')
    serializer_class = DeliveryAssignmentDetailSerializer
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return DeliveryAssignmentListSerializer
        return self.serializer_class

        return queryset

class DeletionRequestViewSet(AdminLoginRequiredMixin, viewsets.ViewSet):
    """Manage account deletion requests from vendors and delivery agents"""
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]

    @action(detail=False, methods=['get'])
    def list_requests(self, request):
        """List all pending deletion requests"""
        from vendor.models import VendorProfile
        from deliveryAgent.models import DeliveryAgentProfile
        
        vendor_requests = VendorProfile.objects.filter(is_deletion_requested=True)
        agent_requests = DeliveryAgentProfile.objects.filter(is_deletion_requested=True)
        
        data = []
        for v in vendor_requests:
            data.append({
                'type': 'vendor',
                'id': v.id,
                'name': v.shop_name,
                'email': v.user.email,
                'reason': v.deletion_reason,
                'requested_at': v.deletion_requested_at
            })
        for a in agent_requests:
            data.append({
                'type': 'delivery_agent',
                'id': a.id,
                'name': a.user.get_full_name() or a.user.username,
                'email': a.user.email,
                'reason': a.deletion_reason,
                'requested_at': a.deletion_requested_at
            })
            
        return Response(data)

    @action(detail=False, methods=['post'])
    def process_request(self, request):
        """Approve or deny a deletion request"""
        from vendor.models import VendorProfile
        from deliveryAgent.models import DeliveryAgentProfile
        
        target_type = request.data.get('type') # 'vendor' or 'delivery_agent'
        target_id = request.data.get('id')
        action = request.data.get('action') # 'approve' or 'deny'
        
        if target_type == 'vendor':
            profile = get_object_or_404(VendorProfile, id=target_id)
        elif target_type == 'delivery_agent':
            profile = get_object_or_404(DeliveryAgentProfile, id=target_id)
        else:
            return Response({'error': 'Invalid target type'}, status=400)
            
        if action == 'approve':
            user = profile.user
            user.is_active = False 
            user.save()
            profile.is_deletion_requested = False
            profile.save()
            return Response({'message': 'Account deactivated successfully.'})
            
        elif action == 'deny':
            profile.is_deletion_requested = False
            profile.deletion_reason = None
            profile.save()
            return Response({'message': 'Deletion request denied.'})
            
        return Response({'error': 'Invalid action'}, status=400)


class CommissionSettingsViewSet(AdminLoginRequiredMixin, viewsets.ViewSet):
    """Manage global and category commission settings"""
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]

    def list(self, request):
        """GET /superAdmin/api/commission-settings/ - List all category commissions"""
        commissions = CategoryCommission.objects.all()
        data = []
        for c in commissions:
            data.append({
                'id': c.id,
                'category': c.category,
                'category_display': c.get_category_display(),
                'commission_type': c.commission_type,
                'percentage': float(c.percentage),
                'fixed_amount': float(c.fixed_amount),
                'updated_at': c.updated_at,
            })
        return Response(data)

    def create(self, request):
        """POST /superAdmin/api/commission-settings/ - Create a category commission"""
        category = request.data.get('category')
        percentage = request.data.get('percentage', 0)
        commission_type = request.data.get('commission_type', 'percentage')

        if not category:
            return Response({'error': 'Category is required.'}, status=400)

        if CategoryCommission.objects.filter(category=category).exists():
            return Response({'error': 'A commission rule for this category already exists.'}, status=400)

        obj = CategoryCommission.objects.create(
            category=category,
            percentage=percentage,
            commission_type=commission_type
        )
        return Response({
            'id': obj.id,
            'category': obj.category,
            'category_display': obj.get_category_display(),
            'commission_type': obj.commission_type,
            'percentage': float(obj.percentage),
            'fixed_amount': float(obj.fixed_amount),
        }, status=201)

    def destroy(self, request, pk=None):
        """DELETE /superAdmin/api/commission-settings/{id}/ - Delete a category commission"""
        obj = get_object_or_404(CategoryCommission, pk=pk)
        obj.delete()
        return Response({'message': 'Category commission removed.'}, status=204)

    @action(detail=False, methods=['get', 'post'])
    def global_(self, request):
        """GET/POST /superAdmin/api/commission-settings/global/ - Get or update global commission"""
        if request.method == 'GET':
            obj = GlobalCommission.objects.first()
            if not obj:
                obj = GlobalCommission.objects.create(percentage=10.00, commission_type='percentage')
            return Response({
                'id': obj.id,
                'commission_type': obj.commission_type,
                'percentage': float(obj.percentage),
                'fixed_amount': float(obj.fixed_amount),
                'updated_at': obj.updated_at,
            })
        else:
            percentage = request.data.get('percentage')
            commission_type = request.data.get('commission_type', 'percentage')

            if percentage is None:
                return Response({'error': 'Percentage is required.'}, status=400)

            obj, _ = GlobalCommission.objects.get_or_create(pk=1)
            obj.percentage = percentage
            obj.commission_type = commission_type
            obj.save()
            return Response({
                'id': obj.id,
                'commission_type': obj.commission_type,
                'percentage': float(obj.percentage),
                'fixed_amount': float(obj.fixed_amount),
                'updated_at': obj.updated_at,
            })


# ═══════════════════ DEDICATED ADMIN LOGIN ═══════════════════

from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

class AdminLoginView(APIView):
    """
    POST /superAdmin/api/admin-login/
    Dedicated login for admin panel — only allows is_staff or is_superuser accounts.
    Accepts: { "username": "...", "password": "..." }   (username OR email)
    Returns: { "access": "...", "refresh": "...", "username": "...", "email": "..." }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username_or_email = request.data.get('username') or request.data.get('email', '')
        password = request.data.get('password', '')

        if not username_or_email or not password:
            return Response({'error': 'Username/email and password are required.'}, status=400)

        User = get_user_model()

        # Resolve username → email (our AUTH backend uses email as USERNAME_FIELD)
        auth_email = username_or_email.strip().lower()
        if '@' not in auth_email:
            try:
                # Case-insensitive resolution
                user_obj = User.objects.filter(username__iexact=username_or_email.strip()).first()
                if user_obj:
                    auth_email = user_obj.email
                else:
                    # Fallback to authenticating with what they provided (might fail)
                    pass
            except Exception:
                pass

        user = authenticate(username=auth_email, password=password)

        if user is None:
            # Check if account exists to give better feedback
            if User.objects.filter(email=auth_email).exists():
                return Response({'error': 'Incorrect password.'}, status=401)
            return Response({'error': 'No administrator account found with this email/username.'}, status=401)

        if not user.is_active:
            return Response({'error': 'This account is inactive.'}, status=403)

        if not (user.is_staff or user.is_superuser):
            return Response({
                'error': 'Access denied. This login is for admin/staff accounts only.'
            }, status=403)

        refresh = RefreshToken.for_user(user)
        refresh['is_staff'] = user.is_staff
        refresh['is_superuser'] = user.is_superuser
        refresh['role'] = 'ADMIN' # Explicitly set role for frontend compatibility
        refresh['username'] = user.username

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        })


# ═══════════════════ DEBUG / WHOAMI ═══════════════════

class WhoAmIView(APIView):
    """
    GET /superAdmin/api/whoami/
    Returns information about the currently authenticated user.
    Used for debugging 403 issues.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'is_staff': u.is_staff,
            'is_superuser': u.is_superuser,
            'is_active': u.is_active,
            'role': getattr(u, 'role', 'N/A'),
            'is_admin_eligible': u.is_staff or u.is_superuser,
        })
