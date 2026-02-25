from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    VendorRequestViewSet, VendorManagementViewSet, ProductManagementViewSet,
    DeliveryRequestViewSet, DeliveryAgentManagementViewSet, DashboardView,
    CommissionSettingsViewSet, ReportsView,
    UserManagementView, UserBlockToggleView,
    TriggerAssignmentView, UnassignedOrdersView,
    AdminOrderTrackingViewSet, AdminOrderViewSet, DeletionRequestViewSet,
    AdminLoginView, WhoAmIView, ContactQueryViewSet
    AdminLoginView, WhoAmIView, ReturnManagementViewSet

)

router = DefaultRouter()
router.register(r'vendor-requests', VendorRequestViewSet, basename='vendor_request')
router.register(r'vendors', VendorManagementViewSet, basename='vendor_management')
router.register(r'products', ProductManagementViewSet, basename='product_management')
router.register(r'delivery-requests', DeliveryRequestViewSet, basename='delivery_request')
router.register(r'delivery-agents', DeliveryAgentManagementViewSet, basename='delivery_agent')
router.register(r'commission-settings', CommissionSettingsViewSet, basename='commission_settings')
router.register(r'tracking', AdminOrderTrackingViewSet, basename='order_tracking')
router.register(r'orders', AdminOrderViewSet, basename='admin_orders')
router.register(r'deletion-requests', DeletionRequestViewSet, basename='deletion_requests')
router.register(r'contact-queries', ContactQueryViewSet, basename='contact_queries')
router.register(r'order-returns', ReturnManagementViewSet, basename='order_returns')



urlpatterns = [
    # Dashboard
    path('dashboard/', DashboardView.as_view(), name='admin_dashboard_api'),
    path('reports/', ReportsView.as_view(), name='admin_reports_api'),

    # User management
    path('users/', UserManagementView.as_view(), name='admin_users_list'),
    path('users/<int:pk>/toggle-block/', UserBlockToggleView.as_view(), name='admin_user_toggle_block'),

    # Delivery assignment management
    path('trigger-assignment/<int:order_id>/', TriggerAssignmentView.as_view(), name='trigger_assignment'),
    path('unassigned-orders/', UnassignedOrdersView.as_view(), name='unassigned_orders'),

    # Dedicated Admin Login (enforces is_staff/is_superuser)
    path('admin-login/', AdminLoginView.as_view(), name='admin_login_api'),

    # Debug / whoami
    path('whoami/', WhoAmIView.as_view(), name='whoami'),

    # Explicit global commission endpoint (router auto-generates global_ but frontend expects global)
    path('commission-settings/global/', CommissionSettingsViewSet.as_view({'get': 'global_', 'post': 'global_'}), name='commission_settings_global'),

    # Router endpoints
    path('', include(router.urls)),
]
