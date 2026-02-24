from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as drf_views
from .api_views import (
    RegisterView, LoginView, VendorDetailsView, VendorDashboardView,
    VendorProfileDetailView, ProductViewSet, ApprovalStatusView, UserProfileView,
    VendorOrderListView, VendorOrderItemUpdateView, serve_product_image,
    VendorInvoiceAPIView, VendorCommissionInvoiceAPIView
)
from vendor import views as vendor_views


router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    # Image serving
    path('product-images/<int:image_id>/', serve_product_image, name='serve_product_image'),
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='api_register'),
    path('login/', LoginView.as_view(), name='api_login'),
    
    # Vendor endpoints
    path('profile/', VendorProfileDetailView.as_view(), name='api_vendor_profile'),
    path('details/', VendorDetailsView.as_view(), name='api_vendor_details'),
    path('dashboard/', VendorDashboardView.as_view(), name='api_vendor_dashboard'),
    path('approval-status/', ApprovalStatusView.as_view(), name='api_approval_status'),
    
    # User endpoints
    path('user/profile/', UserProfileView.as_view(), name='user_profile'),
    
    path('orders/', VendorOrderListView.as_view(), name='api_vendor_orders'),
    path('orders/<int:pk>/update-status/', VendorOrderItemUpdateView.as_view(), name='api_vendor_order_update'),
    path('orders/invoice/<str:order_number>/', VendorInvoiceAPIView.as_view(), name='api_vendor_invoice'),
    path('orders/commission/<str:order_number>/', VendorCommissionInvoiceAPIView.as_view(), name='api_vendor_commission_invoice'),
    
    # Products
    path('', include(router.urls)),

    # Account Management
    path('request_deletion/', vendor_views.vendor_request_deletion, name='api_vendor_request_deletion'),
    path('logout/', vendor_views.vendor_logout, name='api_vendor_logout'),
]

