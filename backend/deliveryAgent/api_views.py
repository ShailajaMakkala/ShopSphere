from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.db import transaction, models
from django.db.models import Q, Sum, Avg, Count

from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    DeliveryAgentProfile, DeliveryAssignment, DeliveryTracking,
    DeliveryCommission, DeliveryPayment, DeliveryDailyStats, DeliveryFeedback
)
from .serializers import (
    DeliveryAgentProfileListSerializer, DeliveryAgentProfileDetailSerializer,
    DeliveryAgentProfileCreateSerializer, DeliveryAgentDashboardSerializer,
    DeliveryAssignmentListSerializer, DeliveryAssignmentDetailSerializer,
    DeliveryAssignmentCreateSerializer, DeliveryTrackingSerializer,
    DeliveryCommissionSerializer, DeliveryPaymentSerializer,
    DeliveryDailyStatsSerializer, DeliveryFeedbackSerializer
)
from user.models import Order

User = get_user_model()


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ===============================================
#     DELIVERY AGENT PROFILE VIEWSET
# ===============================================

class DeliveryAgentProfileViewSet(viewsets.ViewSet):
    """Delivery agent profile management"""
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Register a new delivery agent"""
        serializer = DeliveryAgentProfileCreateSerializer(data=request.data, context={'email': request.data.get('email')})
        if serializer.is_valid():
            agent = serializer.save()
            return Response({
                'message': 'Registration successful. Wait for Admin approval.',
                'agent_id': agent.id
            }, status=status.HTTP_201_CREATED)
        
        # Format errors for frontend
        error_msg = next(iter(serializer.errors.values()))[0] if serializer.errors else "Registration failed"
        if isinstance(error_msg, list):
            error_msg = error_msg[0]
            
        return Response({'error': str(error_msg)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def get_agent(self, request):
        """Get current delivery agent profile"""
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            serializer = DeliveryAgentProfileDetailSerializer(agent)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DeliveryAgentProfile.DoesNotExist:
            return Response({'error': 'Delivery agent profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update agent profile"""
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            
            allowed_fields = ['phone_number', 'address', 'city', 'state', 'postal_code',
                            'vehicle_type', 'vehicle_number', 'service_cities', 
                            'service_pincodes', 'preferred_delivery_radius', 
                            'working_hours_start', 'working_hours_end', 'latitude', 'longitude']
            
            for field in allowed_fields:
                if field in request.data:
                    setattr(agent, field, request.data[field])
            
            agent.save()
            serializer = DeliveryAgentProfileDetailSerializer(agent)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DeliveryAgentProfile.DoesNotExist:
            return Response({'error': 'Agent profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def update_availability(self, request):
        """Update agent availability status"""
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            status_choice = request.data.get('status')
            
            if status_choice not in dict(DeliveryAgentProfile.AVAILABILITY_CHOICES):
                return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
            
            agent.availability_status = status_choice
            agent.last_online = timezone.now()
            agent.save()
            
            return Response({
                'message': 'Status updated',
                'status': agent.availability_status
            }, status=status.HTTP_200_OK)
        except DeliveryAgentProfile.DoesNotExist:
            return Response({'error': 'Agent profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def request_deletion(self, request):
        """Delivery agent requests account deletion"""
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            reason = request.data.get('reason', 'No reason provided')
            
            agent.is_deletion_requested = True
            agent.deletion_reason = reason
            agent.deletion_requested_at = timezone.now()
            agent.save()
            
            return Response({
                'success': True, 
                'message': 'Account deletion request submitted. Admin will review it shortly.'
            })
        except DeliveryAgentProfile.DoesNotExist:
            return Response({'error': 'Delivery agent profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# ===============================================
#    DELIVERY ASSIGNMENT VIEWSET
# ===============================================

class DeliveryAssignmentViewSet(viewsets.ViewSet):
    """Delivery assignment management for agents"""
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def list(self, request):
        """Get all assigned deliveries for agent"""
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            
            status_filter = request.query_params.get('status')
            queryset = DeliveryAssignment.objects.filter(agent=agent).order_by('-assigned_at')
            
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            serializer = DeliveryAssignmentListSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DeliveryAgentProfile.DoesNotExist:
            return Response({'error': 'Agent profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def retrieve(self, request, pk=None):
        """Get detailed delivery assignment"""
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            assignment = DeliveryAssignment.objects.get(id=pk, agent=agent)
            serializer = DeliveryAssignmentDetailSerializer(assignment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DeliveryAgentProfile.DoesNotExist:
            return Response({'error': 'Agent profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except DeliveryAssignment.DoesNotExist:
            return Response({'error': 'Delivery assignment not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a delivery assignment"""
        is_admin = request.user.is_superuser or request.user.is_staff
        try:
            if is_admin:
                assignment = DeliveryAssignment.objects.get(id=pk)
            else:
                agent = DeliveryAgentProfile.objects.get(user=request.user)
                assignment = DeliveryAssignment.objects.get(id=pk, agent=agent)
            
            if assignment.status != 'assigned':
                return Response({'error': 'Only assigned deliveries can be accepted'}, status=status.HTTP_400_BAD_REQUEST)
            
            assignment.accept_delivery()
            serializer = DeliveryAssignmentDetailSerializer(assignment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (DeliveryAgentProfile.DoesNotExist, DeliveryAssignment.DoesNotExist):
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject/Deny a delivery assignment"""
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            assignment = DeliveryAssignment.objects.get(id=pk, agent=agent)
            
            if assignment.status != 'assigned':
                return Response({'error': 'Only newly assigned tasks can be rejected'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Revert order status if necessary
            order = assignment.order
            if order.status == 'out_for_delivery':
                order.status = 'shipping' # Back to 'In Transit / Shipping'
                order.save(update_fields=['status'])
            
            # Delete the assignment so it can be reassigned
            assignment.delete()
            
            return Response({'message': 'Assignment rejected successfully'}, status=status.HTTP_200_OK)
        except (DeliveryAgentProfile.DoesNotExist, DeliveryAssignment.DoesNotExist):
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start delivery (picked up from vendor)"""
        is_admin = request.user.is_superuser or request.user.is_staff
        try:
            if is_admin:
                assignment = DeliveryAssignment.objects.get(id=pk)
            else:
                agent = DeliveryAgentProfile.objects.get(user=request.user)
                assignment = DeliveryAssignment.objects.get(id=pk, agent=agent)
            
            if assignment.status != 'accepted':
                return Response({'error': 'Delivery must be accepted first'}, status=status.HTTP_400_BAD_REQUEST)
            
            assignment.start_delivery()
            serializer = DeliveryAssignmentDetailSerializer(assignment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (DeliveryAgentProfile.DoesNotExist, DeliveryAssignment.DoesNotExist):
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def in_transit(self, request, pk=None):
        """Mark delivery as in transit"""
        is_admin = request.user.is_superuser or request.user.is_staff
        try:
            if is_admin:
                assignment = DeliveryAssignment.objects.get(id=pk)
            else:
                agent = DeliveryAgentProfile.objects.get(user=request.user)
                assignment = DeliveryAssignment.objects.get(id=pk, agent=agent)
            
            if assignment.status != 'picked_up':
                return Response({'error': 'Delivery must be picked up first'}, status=status.HTTP_400_BAD_REQUEST)
            
            assignment.mark_in_transit()
            serializer = DeliveryAssignmentDetailSerializer(assignment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (DeliveryAgentProfile.DoesNotExist, DeliveryAssignment.DoesNotExist):
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark delivery as completed — requires OTP from customer."""
        is_admin = request.user.is_superuser or request.user.is_staff
        try:
            if is_admin:
                assignment = DeliveryAssignment.objects.select_related('order', 'order__user', 'agent').get(id=pk)
                agent = assignment.agent
            else:
                agent = DeliveryAgentProfile.objects.get(user=request.user)
                assignment = DeliveryAssignment.objects.select_related('order', 'order__user').get(id=pk, agent=agent)

            if assignment.status not in ['picked_up', 'in_transit', 'arrived']:
                return Response({'error': 'Delivery must be in status Picked Up, In Transit, or Arrived to complete'}, status=status.HTTP_400_BAD_REQUEST)

            # ── OTP Validation ─────────────────────────────────────────────
            entered_otp = request.data.get('otp_code', '').strip()
            if not entered_otp:
                return Response({'error': 'OTP is required to complete delivery. Ask the customer for their OTP.'}, status=status.HTTP_400_BAD_REQUEST)
            if not assignment.otp_code:
                return Response({'error': 'No OTP has been generated for this delivery. Ensure you marked it as In Transit first.'}, status=status.HTTP_400_BAD_REQUEST)
            if entered_otp != assignment.otp_code:
                return Response({'error': 'Incorrect OTP. Please ask the customer to check their email or in-app notification.'}, status=status.HTTP_400_BAD_REQUEST)

            # Handle optional proof of delivery
            if 'signature_image' in request.FILES:
                assignment.signature_image = request.FILES['signature_image']
            if 'delivery_photo' in request.FILES:
                assignment.delivery_photo = request.FILES['delivery_photo']

            assignment.otp_verified = True
            assignment.save(update_fields=['otp_verified', 'signature_image', 'delivery_photo'])

            with transaction.atomic():
                assignment.mark_delivered()



            serializer = DeliveryAssignmentDetailSerializer(assignment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (DeliveryAgentProfile.DoesNotExist, DeliveryAssignment.DoesNotExist):
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def failed(self, request, pk=None):
        """Mark delivery as failed"""
        is_admin = request.user.is_superuser or request.user.is_staff
        try:
            if is_admin:
                assignment = DeliveryAssignment.objects.get(id=pk)
            else:
                agent = DeliveryAgentProfile.objects.get(user=request.user)
                assignment = DeliveryAssignment.objects.get(id=pk, agent=agent)
            
            if assignment.status in ['delivered', 'cancelled', 'failed']:
                return Response({'error': 'Cannot mark finalized delivery as failed'}, status=status.HTTP_400_BAD_REQUEST)
            
            reason = request.data.get('notes', 'Agent reported delivery failure')
            assignment.mark_failed(reason=reason)
            
            return Response({
                'message': 'Delivery marked as failed and order cancelled',
                'status': assignment.status,
                'attempts': assignment.attempts_count,
                'reason': assignment.failure_reason
            }, status=status.HTTP_200_OK)
        except (DeliveryAgentProfile.DoesNotExist, DeliveryAssignment.DoesNotExist):
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get currently active deliveries"""
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            active = DeliveryAssignment.objects.filter(
                agent=agent,
                status__in=['assigned', 'accepted', 'picked_up', 'in_transit']
            ).order_by('-assigned_at')
            
            serializer = DeliveryAssignmentListSerializer(active, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DeliveryAgentProfile.DoesNotExist:
            return Response({'error': 'Agent profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===============================================
#      DELIVERY TRACKING VIEWSET
# ===============================================

class DeliveryTrackingViewSet(viewsets.ViewSet):
    """Real-time delivery tracking"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def update_location(self, request, pk=None):
        """Update current delivery location (real-time tracking)"""
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            assignment = DeliveryAssignment.objects.get(id=pk, agent=agent)
            
            # Create tracking record
            tracking = DeliveryTracking.objects.create(
                delivery_assignment=assignment,
                latitude=request.data.get('latitude'),
                longitude=request.data.get('longitude'),
                address=request.data.get('address', ''),
                status=request.data.get('status', 'In Transit'),
                speed=request.data.get('speed', None),
                notes=request.data.get('notes', '')
            )
            
            # Update assignment current location
            assignment.current_location = {
                'latitude': float(request.data.get('latitude', 0)),
                'longitude': float(request.data.get('longitude', 0)),
                'address': request.data.get('address', '')
            }
            assignment.save()
            
            serializer = DeliveryTrackingSerializer(tracking)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (DeliveryAgentProfile.DoesNotExist, DeliveryAssignment.DoesNotExist):
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def get_tracking_history(self, request, pk=None):
        """Get tracking history for a delivery"""
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            assignment = DeliveryAssignment.objects.get(id=pk, agent=agent)
            
            tracking = DeliveryTracking.objects.filter(
                delivery_assignment=assignment
            ).order_by('-tracked_at')
            
            serializer = DeliveryTrackingSerializer(tracking, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (DeliveryAgentProfile.DoesNotExist, DeliveryAssignment.DoesNotExist):
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===============================================
#    DELIVERY COMMISSION & EARNINGS VIEWSET
# ===============================================

class DeliveryEarningsViewSet(viewsets.ViewSet):
    """Commission and earnings tracking"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get all commissions/earnings"""
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            
            status_filter = request.query_params.get('status')
            queryset = DeliveryCommission.objects.filter(agent=agent).order_by('-created_at')
            
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            serializer = DeliveryCommissionSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DeliveryAgentProfile.DoesNotExist:
            return Response({'error': 'Agent profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get earnings summary with optional time filters (today, monthly, yearly)"""
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            filter_type = request.query_params.get('filter') # today, monthly, yearly
            
            commissions = DeliveryCommission.objects.filter(agent=agent)
            
            if filter_type == 'today':
                commissions = commissions.filter(created_at__date=timezone.now().date())
            elif filter_type == 'monthly':
                commissions = commissions.filter(created_at__month=timezone.now().month, created_at__year=timezone.now().year)
            elif filter_type == 'yearly':
                commissions = commissions.filter(created_at__year=timezone.now().year)
            
            total_pending = commissions.filter(status='pending').aggregate(Sum('total_commission'))['total_commission__sum'] or Decimal('0.00')
            total_approved = commissions.filter(status='approved').aggregate(Sum('total_commission'))['total_commission__sum'] or Decimal('0.00')
            total_paid = commissions.filter(status='paid').aggregate(Sum('total_commission'))['total_commission__sum'] or Decimal('0.00')
            
            return Response({
                'pending': str(total_pending),
                'approved': str(total_approved),
                'paid': str(total_paid),
                'total': str(total_pending + total_approved + total_paid),
            }, status=status.HTTP_200_OK)
        except DeliveryAgentProfile.DoesNotExist:
            return Response({'error': 'Agent profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===============================================
#      DELIVERY PAYMENT VIEWSET
# ===============================================

class DeliveryPaymentViewSet(viewsets.ViewSet):
    """Payment/payout management"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get all payment records"""
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            queryset = DeliveryPayment.objects.filter(agent=agent).order_by('-created_at')
            
            serializer = DeliveryPaymentSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DeliveryAgentProfile.DoesNotExist:
            return Response({'error': 'Agent profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending payout amount"""
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            pending_amount = DeliveryPayment.objects.filter(
                agent=agent,
                status__in=['pending', 'processing']
            ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            
            return Response({'pending_amount': str(pending_amount)}, status=status.HTTP_200_OK)
        except DeliveryAgentProfile.DoesNotExist:
            return Response({'error': 'Agent profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def withdraw(self, request):
        """Request a withdrawal of funds from wallet using Razorpay integration"""
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            from user.models import UserWallet
            wallet, created = UserWallet.objects.get_or_create(user=request.user)
            
            amount = Decimal(str(request.data.get('amount', 0)))
            method = request.data.get('method', 'bank_transfer')
            
            if amount < 100:
                return Response({'error': 'Minimum withdrawal amount is ₹100'}, status=400)
                
            if wallet.balance < amount:
                return Response({'error': 'Insufficient balance'}, status=400)
            
            from django.db import transaction
            
            with transaction.atomic():
                # 1. Deduct from wallet first
                wallet.deduct_balance(amount, f"Withdrawal request of ₹{amount}")
                
                # 2. Process via Razorpay Helper
                from .razorpay_utils import RazorpayPayoutHelper
                rp_helper = RazorpayPayoutHelper()
                payout_res = rp_helper.create_payout(agent, amount, method)
                
                if payout_res['status'] == 'success':
                    # Create payout record as completed
                    payout = DeliveryPayment.objects.create(
                        agent=agent,
                        amount=amount,
                        payment_method=method,
                        status='completed',
                        transaction_id=payout_res['data']['id'],
                        paid_at=timezone.now(),
                        from_date=timezone.now().date(),
                        to_date=timezone.now().date(),
                        notes=f"Processed via Razorpay to {agent.bank_name}"
                    )
                    
                    return Response({
                        'message': 'Withdrawal processed successfully',
                        'payout_id': payout.id,
                        'transaction_id': payout.transaction_id,
                        'current_balance': str(wallet.balance)
                    })
                else:
                    # Rollback wallet deduction manually if transaction not rolled back (though atomic handles db errors, logic error requires manual raise or manual rollback)
                    # Since we are inside atomic block, raising an exception will rollback the deduction.
                    raise Exception(f"Withdrawal failed: {payout_res.get('message')}")

        except Exception as e:
            return Response({'error': str(e)}, status=400)


# ===============================================
#     DELIVERY DAILY STATS VIEWSET
# ===============================================

class DeliveryDailyStatsViewSet(viewsets.ViewSet):
    """Daily statistics and performance tracking"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get daily stats for last 30 days"""
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            days = int(request.query_params.get('days', 30))
            
            stats = DeliveryDailyStats.objects.filter(
                agent=agent,
                date__gte=timezone.now().date() - timedelta(days=days)
            ).order_by('-date')
            
            serializer = DeliveryDailyStatsSerializer(stats, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DeliveryAgentProfile.DoesNotExist:
            return Response({'error': 'Agent profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's statistics"""
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            today = timezone.now().date()
            
            stats, created = DeliveryDailyStats.objects.get_or_create(
                agent=agent,
                date=today
            )
            
            serializer = DeliveryDailyStatsSerializer(stats)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DeliveryAgentProfile.DoesNotExist:
            return Response({'error': 'Agent profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===============================================
#       DELIVERY FEEDBACK VIEWSET
# ===============================================

class DeliveryFeedbackViewSet(viewsets.ViewSet):
    """Customer feedback and ratings"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Get all feedback for agent"""
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            feedback = DeliveryFeedback.objects.filter(agent=agent).order_by('-created_at')
            
            serializer = DeliveryFeedbackSerializer(feedback, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DeliveryAgentProfile.DoesNotExist:
            return Response({'error': 'Agent profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def rating_summary(self, request):
        """Get rating summary"""
        try:
            agent = DeliveryAgentProfile.objects.get(user=request.user)
            feedback = DeliveryFeedback.objects.filter(agent=agent)
            
            avg_rating = feedback.aggregate(Avg('overall_rating'))['overall_rating__avg'] or 0
            total_feedback = feedback.count()
            complaint_count = feedback.filter(is_complaint=True).count()
            
            return Response({
                'average_rating': float(avg_rating),
                'total_feedback': total_feedback,
                'complaint_count': complaint_count,
                'satisfaction_rate': float((total_feedback - complaint_count) / total_feedback * 100) if total_feedback > 0 else 0
            }, status=status.HTTP_200_OK)
        except DeliveryAgentProfile.DoesNotExist:
            return Response({'error': 'Agent profile not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===============================================
#     DELIVERY AGENT DASHBOARD VIEW
# ===============================================

class DeliveryAgentDashboardView(generics.RetrieveAPIView):
    """Comprehensive delivery agent dashboard"""
    permission_classes = [IsAuthenticated]
    serializer_class = DeliveryAgentDashboardSerializer
    
    def get_object(self):
        try:
            return DeliveryAgentProfile.objects.get(user=self.request.user)
        except DeliveryAgentProfile.DoesNotExist:
            from django.http import Http404
            raise Http404("Delivery agent profile not found")
    
    def retrieve(self, request, *args, **kwargs):
        from django.http import Http404
        try:
            agent = self.get_object()
            
            # Restrict access if not approved
            if agent.approval_status != 'approved':
                return Response({
                    'error': f'Agent account {agent.approval_status}',
                    'status': agent.approval_status,
                    'reason': agent.rejection_reason if agent.approval_status == 'rejected' else 'Awaiting admin approval'
                }, status=status.HTTP_403_FORBIDDEN)

            if agent.is_blocked:
                return Response({
                    'error': 'Agent account is blocked',
                    'reason': agent.blocked_reason
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = self.get_serializer(agent)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Http404 as e:
            # Let DRF handle 404
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            import traceback
            print(f"Error in DeliveryAgentDashboardView: {str(e)}")
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ===============================================
#   UPDATE ORDER STATUS (pickup / in_transit / failed)
# ===============================================

class UpdateOrderStatusView(APIView):
    """
    POST /api/delivery/assignments/{pk}/update-status/
    Body: { "status": "picked_up" | "in_transit" | "failed", "notes": "..." }

    Allowed transitions:
      accepted     → picked_up
      picked_up    → in_transit
      in_transit   → failed
      accepted     → failed
      picked_up    → failed

    Each step appends a DeliveryTracking record and syncs Order.status.
    """
    permission_classes = [IsAuthenticated]

    # Maps assignment status → Order.status
    ORDER_STATUS_MAP = {
        'picked_up':  'shipping',
        'in_transit': 'out_for_delivery',
        'arrived':    'out_for_delivery',
        'failed':     'cancelled',
    }

    VALID_TRANSITIONS = {
        'accepted':   ['picked_up', 'failed'],
        'picked_up':  ['in_transit', 'failed'],
        'in_transit': ['arrived', 'failed'],
        'arrived':    ['failed'],
    }

    def post(self, request, pk):
        # Check if the user is an admin or staff (allowing simulation from admin dashboard)
        is_admin = request.user.is_superuser or request.user.is_staff
        
        agent = None
        if not is_admin:
            try:
                agent = DeliveryAgentProfile.objects.get(user=request.user)
            except DeliveryAgentProfile.DoesNotExist:
                return Response({'error': 'Agent profile not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            if is_admin:
                # Admins can manage any assignment
                assignment = DeliveryAssignment.objects.select_related('order').get(id=pk)
            else:
                # Agents can only manage their own assignments
                assignment = DeliveryAssignment.objects.select_related('order').get(id=pk, agent=agent)
        except DeliveryAssignment.DoesNotExist:
            return Response({'error': 'Assignment not found'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status', '').strip().lower()
        notes = request.data.get('notes', '')

        allowed = self.VALID_TRANSITIONS.get(assignment.status, [])
        if new_status not in allowed:
            return Response({
                'error': f"Cannot transition from '{assignment.status}' to '{new_status}'. "
                         f"Allowed: {allowed or 'none'}"
            }, status=status.HTTP_400_BAD_REQUEST)

        import random
        from django.db import transaction

        with transaction.atomic():
            # Update assignment status
            assignment.status = new_status
            if new_status == 'picked_up':
                assignment.pickup_time = timezone.now()
                assignment.started_at = timezone.now()
            elif new_status == 'arrived':
                # Generate fresh 6-digit OTP for delivery verification when arrived
                otp = f"{random.randint(100000, 999999)}"
                assignment.otp_code = otp
            elif new_status == 'failed':
                assignment.attempts_count += 1
                if notes:
                    assignment.failure_reason = notes
            assignment.save()

            # Sync order status
            order_status = self.ORDER_STATUS_MAP.get(new_status)
            if order_status and assignment.order:
                assignment.order.status = order_status
                assignment.order.save(update_fields=['status'])

            # Create tracking record for delivery agent
            status_labels = {
                'picked_up':  'Picked Up from Vendor',
                'in_transit': 'Out for Delivery',
                'arrived':    'Arrived at Customer Location',
                'failed':     'Delivery Attempt Failed',
            }
            DeliveryTracking.objects.create(
                delivery_assignment=assignment,
                latitude=0,
                longitude=0,
                address=assignment.delivery_city,
                status=status_labels.get(new_status, new_status.title()),
                notes=notes or status_labels.get(new_status, ''),
            )

            # ── Sync with Customer's Order Tracking Feed ────────────────────
            try:
                from user.models import OrderTracking
                OrderTracking.objects.create(
                    order=assignment.order,
                    status=status_labels.get(new_status, new_status.title()),
                    location=assignment.delivery_city,
                    notes=notes or f"Order {status_labels.get(new_status, new_status.title()).lower()}"
                )
            except Exception as e:
                print(f"DEBUG: Error syncing customer tracking: {str(e)}")

        # ── OTP notification (only on arrived) ──────────────────────────
        otp_sent = False
        if new_status == 'arrived' and assignment.order:
            customer = assignment.order.user
            otp = assignment.otp_code
            order_number = assignment.order.order_number

            # 1. In-app notification
            try:
                from user.models import Notification
                Notification.objects.create(
                    user=customer,
                    notification_type='delivery',
                    title='🔐 Your Delivery OTP',
                    message=(
                        f'Your delivery agent is on the way! '
                        f'Your one-time delivery OTP is: {otp}\n'
                        f'Share this with the agent to confirm receipt of order #{order_number}.'
                    ),
                    related_order=assignment.order,
                )
            except Exception:
                pass  # Non-critical

            # 2. Email
            try:
                from django.core.mail import send_mail
                from django.conf import settings as django_settings
                send_mail(
                    subject=f'[ShopSphere] Delivery OTP for Order #{order_number}',
                    message=(
                        f'Hello {customer.first_name or customer.username},\n\n'
                        f'Your delivery agent is on the way with your order #{order_number}.\n\n'
                        f'Your one-time delivery OTP is:\n\n'
                        f'    {otp}\n\n'
                        f'Please share this OTP with the agent upon receiving your order.\n'
                        f'Do NOT share this OTP with anyone else.\n\n'
                        f'Thank you for shopping with ShopSphere!'
                    ),
                    from_email=django_settings.EMAIL_HOST_USER,
                    recipient_list=[customer.email],
                    fail_silently=True,
                )
                otp_sent = True
            except Exception:
                pass  # Non-critical

        return Response({
            'message': f'Status updated to {new_status}',
            'assignment_status': assignment.status,
            'order_status': order_status,
            'otp_sent': otp_sent,
        }, status=status.HTTP_200_OK)

