from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import VendorCommissionViewSet, VendorEarningsViewSet

router = DefaultRouter()
router.register(r'commission', VendorCommissionViewSet, basename='vendor-commission')
router.register(r'earnings', VendorEarningsViewSet, basename='vendor-earnings')

urlpatterns = [
    path('commission/info/', VendorCommissionViewSet.as_view({'get': 'info'}), name='vendor-commission-info'),
    path('', include(router.urls)),
]
