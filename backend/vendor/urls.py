from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('vendor-details/', views.vendor_details_view, name='vendor_details'),
    
    # Vendor Dashboard and Approval Status
    path('vendor/', views.vendor_home_view, name='vendor_home'),
    path('approval-status/', views.approval_status_view, name='approval_status'),
    
    # Product Management
    path('products/add/', views.add_product_view, name='add_product'),
    path('products/<int:product_id>/', views.view_product_view, name='view_product'),
    path('products/<int:product_id>/edit/', views.edit_product_view, name='edit_product'),
    path('products/<int:product_id>/delete/', views.delete_product_view, name='delete_product'),

    # Invoices and Orders
    path('orders/', views.vendor_orders_view, name='vendor_orders'),
    path('orders/invoice/<str:order_number>/', views.vendor_invoice, name='vendor_invoice'),
    path('orders/commission/<str:order_number>/', views.vendor_commission_invoice, name='vendor_commission_invoice'),
    path('ledgers/', views.vendor_ledgers_view, name='vendor_ledgers'),
]