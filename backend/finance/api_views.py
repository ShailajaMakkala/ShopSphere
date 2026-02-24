from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import CategoryCommission, GlobalCommission
from .serializers import CategoryCommissionSerializer, GlobalCommissionSerializer

class VendorCommissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Vendor-facing view to see commission rates.
    Read-only for transparency.
    """
    queryset = CategoryCommission.objects.all()
    serializer_class = CategoryCommissionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    @action(detail=False, methods=['get'])
    def info(self, request):
        """
        Returns a consolidated view of the platform commission structure.
        """
        from vendor.models import Product, VendorProfile
        
        global_comm = GlobalCommission.objects.first()
        
        # Return all category commissions so vendors can see full fee structure
        categories = CategoryCommission.objects.all()
        
        return Response({
            'global_rate': GlobalCommissionSerializer(global_comm).data if global_comm else None,
            'category_overrides': CategoryCommissionSerializer(categories, many=True).data
        })

class VendorEarningsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Returns the summary data for the earnings page."""
        from vendor.models import VendorProfile
        from .services import FinanceService
        from .serializers import VendorEarningsSummarySerializer
        
        try:
            vendor = VendorProfile.objects.get(user=request.user)
        except VendorProfile.DoesNotExist:
            return Response({"error": "Vendor profile not found"}, status=status.HTTP_404_NOT_FOUND)
            
        summary = FinanceService.get_vendor_earnings_summary(vendor)
        serializer = VendorEarningsSummarySerializer(summary)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Returns time-series data for charts."""
        from vendor.models import VendorProfile
        from .services import FinanceService
        
        period = request.query_params.get('period', 'weekly')
        try:
            vendor = VendorProfile.objects.get(user=request.user)
        except VendorProfile.DoesNotExist:
            return Response({"error": "Vendor profile not found"}, status=status.HTTP_404_NOT_FOUND)
            
        data = FinanceService.get_vendor_analytics(vendor, period)
        return Response(data)

    @action(detail=False, methods=['post'])
    def request_payout(self, request):
        """Allows a vendor to request a payout from their available balance."""
        from vendor.models import VendorProfile
        from .services import FinanceService
        
        try:
            vendor = VendorProfile.objects.get(user=request.user)
        except VendorProfile.DoesNotExist:
            return Response({"error": "Vendor profile not found"}, status=status.HTTP_404_NOT_FOUND)
            
        amount = request.data.get('amount')
        if not amount:
            return Response({"error": "Amount is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            payout = FinanceService.process_payout(vendor, amount)
            return Response({
                "message": "Payout requested successfully",
                "payout_id": payout.id,
                "amount": payout.amount,
                "status": payout.status
            }, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Internal server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
