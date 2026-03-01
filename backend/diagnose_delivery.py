import os
import django
import sys
from decimal import Decimal

try:
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    pass

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ShopSphere.settings')
django.setup()

from deliveryAgent.models import DeliveryAssignment, DeliveryCommission, DeliveryDailyStats, DeliveryAgentProfile
from django.db.models import Sum

def check_delivery_stats():
    print("--- Delivery Stats Diagnosis ---")
    
    agents = DeliveryAgentProfile.objects.all()
    print(f"Total Agents: {agents.count()}")
    
    for agent in agents:
        delivered_count = DeliveryAssignment.objects.filter(agent=agent, status='delivered').count()
        commissions = DeliveryCommission.objects.filter(agent=agent)
        total_comm = commissions.aggregate(Sum('total_commission'))['total_commission__sum'] or Decimal('0.00')
        
        print(f"\nAgent: {agent.user.email} (ID: {agent.id})")
        print(f"  - Delivered Assignments: {delivered_count}")
        print(f"  - Total Commissions (Earnings): INR {total_comm}")
        print(f"  - Commission Records: {commissions.count()}")
        
        stats = DeliveryDailyStats.objects.filter(agent=agent)
        print(f"  - Daily Stats Records: {stats.count()}")

    print("\n--- Summary of Assignments ---")
    statuses = DeliveryAssignment.objects.values_list('status', flat=True).distinct()
    for s in statuses:
        count = DeliveryAssignment.objects.filter(status=s).count()
        print(f"- {s}: {count}")

if __name__ == "__main__":
    check_delivery_stats()
