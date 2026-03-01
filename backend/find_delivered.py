import os
import django
import sys

try:
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    pass

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ShopSphere.settings')
django.setup()

from deliveryAgent.models import DeliveryAssignment

def find_delivered():
    ds = DeliveryAssignment.objects.filter(status='delivered')
    print(f"Total Delivered: {ds.count()}")
    for d in ds:
        print(f"Assignment ID: {d.id}, Agent: {d.agent.user.email} (ID: {d.agent.id}), Order: {d.order.order_number}")

if __name__ == "__main__":
    find_delivered()
