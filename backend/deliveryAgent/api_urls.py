from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    DeliveryAgentDashboardView, DeliveryAssignmentViewSet,
    DeliveryTrackingViewSet, DeliveryEarningsViewSet,
    DeliveryPaymentViewSet, DeliveryDailyStatsViewSet,
    DeliveryFeedbackViewSet, DeliveryAgentProfileViewSet,
    UpdateOrderStatusView,
)

# Create router for viewsets
router = DefaultRouter()
router.register(r'assignments', DeliveryAssignmentViewSet, basename='delivery-assignment')
router.register(r'tracking', DeliveryTrackingViewSet, basename='delivery-tracking')
router.register(r'earnings', DeliveryEarningsViewSet, basename='delivery-earnings')
router.register(r'payments', DeliveryPaymentViewSet, basename='delivery-payment')
router.register(r'daily-stats', DeliveryDailyStatsViewSet, basename='delivery-stats')
router.register(r'feedback', DeliveryFeedbackViewSet, basename='delivery-feedback')
router.register(r'profiles', DeliveryAgentProfileViewSet, basename='delivery-profile')

urlpatterns = [
    # Dashboard
    path('dashboard/', DeliveryAgentDashboardView.as_view(), name='delivery_dashboard'),
    
    # Custom registration path for easier access
    path('register/', DeliveryAgentProfileViewSet.as_view({'post': 'register'}), name='delivery_register'),

    # Update order status (pickup / in_transit / failed)
    path('assignments/<int:pk>/update-status/', UpdateOrderStatusView.as_view(), name='update_order_status'),
    
    # Routed endpoints
    path('', include(router.urls)),
]

