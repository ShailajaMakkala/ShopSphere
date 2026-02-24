import os
import django
import sys
from decimal import Decimal

# Add the project root to sys.path
sys.path.append('c:\\Users\\imvis\\Desktop\\Project-Ecommerce\\project-ecommerce\\Duplicate\\ShopSphere')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ShopSphere.settings')
django.setup()

from user.models import Order, OrderItem
from finance.services import FinanceService
from finance.models import LedgerEntry

def backfill_commissions():
    print("Starting Commission Backfill...")
    
    # 1. Update OrderItems with missing commission
    items_to_fix = OrderItem.objects.filter(commission_amount=0)
    print(f"Found {items_to_fix.count()} items with zero commission.")
    
    for item in items_to_fix:
        if not item.product:
            print(f"Skipping Item {item.id}: No product attached.")
            continue
            
        comm_amount, comm_desc = FinanceService.calculate_commission(
            item.product_price * item.quantity, 
            item.product.category
        )
        # Extract percentage from description like "10%"
        try:
            rate = Decimal(comm_desc.split('%')[0]) if '%' in comm_desc else Decimal('0.00')
        except:
            rate = Decimal('0.00')
            
        item.commission_rate = rate
        item.commission_amount = comm_amount
        item.save()
        print(f"Updated Item {item.id}: {item.product_name} | Commission: {comm_amount} ({comm_desc})")

    # 2. Ensure LedgerEntries exist for completed orders
    completed_orders = Order.objects.filter(payment_status='completed')
    print(f"\nVerifying Ledger Entries for {completed_orders.count()} completed orders...")
    
    for order in completed_orders:
        # Check if ledger entry already exists to avoid duplicates
        # FinanceService.record_order_financials handles grouping by vendor
        # and checking for duplicates via reference_id
        try:
            FinanceService.record_order_financials(order)
            print(f"Processed Order {order.order_number}")
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                # This is actually expected if ledger already exists
                pass
            else:
                print(f"Error processing Order {order.order_number}: {e}")

    print("\nBackfill Complete.")

if __name__ == "__main__":
    backfill_commissions()
