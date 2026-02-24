from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction, models
from django.utils import timezone
from datetime import timedelta
import uuid
from .models import CategoryCommission, LedgerEntry, Payout
from user.models import OrderItem

class FinanceService:
    """
    Service layer for all financial operations.
    Ensures idempotency, auditability, and financial safety.
    """

    @staticmethod
    def get_commission_settings(category):
        """Fetch global commission settings for a category, fallback to GlobalCommission."""
        from .models import GlobalCommission
        try:
            return CategoryCommission.objects.get(category=category)
        except CategoryCommission.DoesNotExist:
            # Fallback to global setting if category specific not found
            global_settings = GlobalCommission.objects.first()
            if not global_settings:
                # Create default global setting if not exists
                global_settings = GlobalCommission.objects.create(percentage=Decimal('10.00'))
            return global_settings

    @staticmethod
    def calculate_commission(price, category):
        """
        Calculate commission based on price and category settings.
        Returns: (amount, rate_snapshot)
        """
        price = Decimal(str(price))
        settings = FinanceService.get_commission_settings(category)
        
        if not settings:
            # Default to 10% if not configured as per common marketplace defaults
            return (price * Decimal('0.10')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), "10% (Default)"

        amount = Decimal('0.00')
        rate_desc = ""

        if settings.commission_type == 'percentage':
            amount = (price * settings.percentage) / 100
            rate_desc = f"{settings.percentage}%"
        elif settings.commission_type == 'fixed':
            amount = settings.fixed_amount
            rate_desc = f"Fixed ₹{settings.fixed_amount}"
        elif settings.commission_type == 'hybrid':
            amount = ((price * settings.percentage) / 100) + settings.fixed_amount
            rate_desc = f"{settings.percentage}% + Fixed ₹{settings.fixed_amount}"

        return amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP), rate_desc

    @staticmethod
    @transaction.atomic
    def record_order_financials(order):
        """
        Consolidate financial entries: Creates ONE LedgerEntry per Vendor per Order.
        Calculates Gross, Commission, and Net in a single row.
        """
        # 1. Group items by vendor
        vendor_data = {}
        for item in order.items.all():
            if not item.product:
                continue
            if not item.vendor:
                continue  # skip items whose vendor couldn't be resolved
                
            vendor_id = item.vendor.id
            if vendor_id not in vendor_data:
                vendor_data[vendor_id] = {
                    'vendor': item.vendor,
                    'gross': Decimal('0.00'),
                    'commission': Decimal('0.00'),
                    'items': []
                }
            
            # Snapshot Commission for the item
            comm_amount, comm_desc = FinanceService.calculate_commission(
                item.product_price * item.quantity, 
                item.product.category
            )
            try:
                item.commission_rate = Decimal(comm_desc.split('%')[0]) if '%' in comm_desc else Decimal('0.00')
            except Exception:
                item.commission_rate = Decimal('0.00')
            item.commission_amount = comm_amount
            item.save()

            vendor_data[vendor_id]['gross'] += item.subtotal
            vendor_data[vendor_id]['commission'] += item.commission_amount
            vendor_data[vendor_id]['items'].append(item.product_name)

        # 2. Create Unified Ledger Entries
        for v_id, data in vendor_data.items():
            net = data['gross'] - data['commission']
            description = f"Unified entry for Order {order.order_number}: Items: {', '.join(data['items'])}"
            
            FinanceService._create_ledger_entry(
                vendor=data['vendor'],
                amount=net, # Net credited to vendor balance
                gross_amount=data['gross'],
                commission_amount=data['commission'],
                net_amount=net,
                entry_type='REVENUE',
                description=description,
                order=order,
                reference_id=f"ORD_{order.order_number}_V_{v_id}"
            )

    @staticmethod
    @transaction.atomic
    def cancel_order_financials(order):
        """
        Reverse all financial entries for a cancelled order.
        Creates CANCELLATION entries to offset the original REVENUE entries.
        """
        original_entries = LedgerEntry.objects.filter(order=order, entry_type='REVENUE')
        for entry in original_entries:
            # Create a reverse entry
            FinanceService._create_ledger_entry(
                vendor=entry.vendor,
                amount=-entry.amount,
                gross_amount=-entry.gross_amount,
                commission_amount=-entry.commission_amount,
                net_amount=-entry.net_amount,
                entry_type='CANCELLATION',
                description=f"Cancellation reversal for Order {order.order_number}",
                order=order,
                reference_id=f"CANCEL_{order.order_number}_V_{entry.vendor.id}",
                is_settled=True # Cancellations clear the uncleared balance immediately
            )
        
        # Also mark original as settled if they weren't, to remove from uncleared balance
        original_entries.filter(is_settled=False).update(is_settled=True, description=F('description') + " (CANCELLED)")

    @staticmethod
    @transaction.atomic
    def settle_order_financials(order):
        """
        Mark REVENUE ledger entries for this order with a 3-day settlement window.
        Executed when an order is successfully delivered.
        Funds are NOT released immediately to vendor wallet.
        """
        from datetime import timedelta
        # Funds stay uncleared for 3 days to allow for returns
        settlement_date = timezone.now() + timedelta(days=3)
        
        updated_count = LedgerEntry.objects.filter(
            order=order,
            entry_type='REVENUE'
        ).update(
            is_settled=False,  # Force false to ensure 3-day hold
            settlement_date=settlement_date
        )
        return updated_count

    @staticmethod
    @transaction.atomic
    def release_expired_funds():
        """
        Background task: Find all ledger entries where settlement_date has passed
        and no return request exists, then mark them as settled (releasing funds to vendor).
        """
        from user.models import OrderReturn
        
        # 1. Identify entries that reached settlement date
        pending_entries = LedgerEntry.objects.filter(
            is_settled=False,
            settlement_date__lte=timezone.now(),
            entry_type='REVENUE'
        )

        released_count = 0
        for entry in pending_entries:
            # Check if there's an active return request for this order
            if entry.order:
                has_active_return = OrderReturn.objects.filter(
                    order=entry.order
                ).exclude(status='rejected').exists()
                
                if not has_active_return:
                    entry.is_settled = True
                    entry.save(update_fields=['is_settled'])
                    released_count += 1
        
        return released_count

    @staticmethod
    @transaction.atomic
    def process_payout(vendor, amount):
        """
        Execute a payout to a vendor.
        Requirement: Concurrent payout prevention (via transaction.atomic and balance check).
        """
        amount = Decimal(str(amount))
        available = FinanceService.get_vendor_balance(vendor)
        
        if amount > available:
            raise ValueError(f"Insufficient funds. Available: {available}, Requested: {amount}")

        # 1. Create Payout Record
        # Snapshot bank details for audit safety
        bank_details = {
            "holder": vendor.bank_holder_name,
            "account": vendor.bank_account_number,
            "ifsc": vendor.bank_ifsc_code
        }
        
        payout = Payout.objects.create(
            vendor=vendor,
            amount=amount,
            bank_details_snapshot=bank_details,
            status='pending'
        )

        # 2. Create Ledger Entry (Debit)
        FinanceService._create_ledger_entry(
            vendor=vendor,
            amount=-amount,
            entry_type='PAYOUT',
            description=f"Payout Execution: ID {payout.id}",
            reference_id=f"PAYOUT_{payout.id}",
            is_settled=True # Payouts are immediately settled entries
        )
        
        return payout

    @staticmethod
    def _create_ledger_entry(vendor, amount, entry_type, description, order=None, order_item=None, reference_id=None, is_settled=False, gross_amount=0, commission_amount=0, net_amount=0):
        """Internal helper for creating immutable ledger entries."""
        if not reference_id:
            reference_id = str(uuid.uuid4())

        # Settlement date is T+7 unless specified (like for payouts)
        settlement_date = timezone.now() + timedelta(days=7) if not is_settled else timezone.now()

        return LedgerEntry.objects.create(
            vendor=vendor,
            amount=amount,
            gross_amount=gross_amount,
            commission_amount=commission_amount,
            net_amount=net_amount,
            entry_type=entry_type,
            description=description,
            order=order,
            order_item=order_item,
            reference_id=reference_id,
            settlement_date=settlement_date,
            is_settled=is_settled
        )

    @staticmethod
    def get_vendor_balance(vendor):
        """
        Calculate vendor balance from ledger entries.
        Requirement: Never update vendor balance directly. All balances must be derived.
        """
        # Sum of settled credits and debits
        balance = LedgerEntry.objects.filter(
            vendor=vendor,
            is_settled=True
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        
        return balance

    @staticmethod
    def get_uncleared_balance(vendor):
        """Sum of ledger entries that are not yet settled (T+7 period)."""
        balance = LedgerEntry.objects.filter(
            vendor=vendor,
            is_settled=False
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        
        return balance

    @staticmethod
    @transaction.atomic
    def process_refund(order_item, refund_amount, reason="Refund"):
        """
        Handle full or partial refunds.
        Requirement: Handle Full refunds, Partial refunds, Order cancellations.
        """
        # Proportional commission reversal
        full_amount = order_item.subtotal
        comm_total = order_item.commission_amount
        
        # Commission reversal amount = (refund_amount / full_amount) * comm_total
        comm_reversal = (Decimal(str(refund_amount)) / full_amount) * comm_total
        comm_reversal = comm_reversal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # 1. Reverse Revenue (Debit Vendor)
        FinanceService._create_ledger_entry(
            vendor=order_item.vendor,
            amount=-Decimal(str(refund_amount)),
            entry_type='REFUND',
            description=f"Refund Reversal for {order_item.order.order_number}: {reason}",
            order=order_item.order,
            order_item=order_item,
            reference_id=f"REFUND_REV_{uuid.uuid4().hex[:8]}"
        )

        # 2. Reverse Commission (Credit Vendor)
        FinanceService._create_ledger_entry(
            vendor=order_item.vendor,
            amount=comm_reversal,
            entry_type='REFUND',
            description=f"Commission Reversal for {order_item.order.order_number}: {reason}",
            order=order_item.order,
            order_item=order_item,
            reference_id=f"REFUND_COM_{uuid.uuid4().hex[:8]}"
        )

    @staticmethod
    def get_vendor_earnings_summary(vendor):
        """Consolidated summary for vendor dashboard."""
        from .models import Payout
        available = FinanceService.get_vendor_balance(vendor)
        uncleared = FinanceService.get_uncleared_balance(vendor)
        total_orders = LedgerEntry.objects.filter(vendor=vendor, entry_type='REVENUE').count()
        pending_payouts = Payout.objects.filter(vendor=vendor, status='pending').aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        recent = LedgerEntry.objects.filter(vendor=vendor).order_by('-created_at')[:10]
        
        # Total Earnings = All REVENUE + All COMMISSION (net of all time)
        lifetime_earnings = LedgerEntry.objects.filter(
            vendor=vendor, 
            entry_type__in=['REVENUE', 'COMMISSION']
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

        # Gross / Commission / Net aggregates (from REVENUE entries)
        revenue_agg = LedgerEntry.objects.filter(
            vendor=vendor,
            entry_type='REVENUE'
        ).aggregate(
            gross=models.Sum('gross_amount'),
            commission=models.Sum('commission_amount'),
            net=models.Sum('net_amount'),
        )

        return {
            "available_balance": available,
            "uncleared_balance": uncleared,
            "lifetime_earnings": lifetime_earnings,
            "total_orders": total_orders,
            "pending_payouts": pending_payouts,
            "recent_activities": recent,
            "total_gross": revenue_agg['gross'] or Decimal('0.00'),
            "total_commission": revenue_agg['commission'] or Decimal('0.00'),
            "total_net": revenue_agg['net'] or Decimal('0.00'),
        }

    @staticmethod
    def get_vendor_analytics(vendor, period='weekly'):
        """Aggregate earnings for charts."""
        if period == 'today':
            start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            entries = LedgerEntry.objects.filter(vendor=vendor, created_at__gte=start_date).order_by('created_at')
            data = {}
            for entry in entries:
                hour_key = entry.created_at.strftime("%I%p") # e.g. 09AM
                data[hour_key] = data.get(hour_key, Decimal('0.00')) + entry.amount
            return [{"name": k, "earnings": v} for k, v in data.items()]

        days = 7 if period == 'weekly' else 30 if period == 'monthly' else 365
        start_date = timezone.now() - timedelta(days=days)
        
        entries = LedgerEntry.objects.filter(
            vendor=vendor,
            created_at__gte=start_date
        ).order_by('created_at')

        data = {}
        for entry in entries:
            date_key = entry.created_at.date().strftime("%Y-%m-%d")
            data[date_key] = data.get(date_key, Decimal('0.00')) + entry.amount
        
        return [{"name": k, "earnings": v} for k, v in data.items()]
