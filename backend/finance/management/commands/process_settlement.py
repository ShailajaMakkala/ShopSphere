from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from finance.models import LedgerEntry

class Command(BaseCommand):
    help = 'Process T+7 settlement for vendor ledger entries'

    def handle(self, *args, **options):
        now = timezone.now()
        
        with transaction.atomic():
            # Find all unsettled entries where the settlement period has passed
            entries = LedgerEntry.objects.filter(
                is_settled=False,
                settlement_date__lte=now
            )
            
            count = entries.count()
            entries.update(is_settled=True)
            
            self.stdout.write(self.style.SUCCESS(f'Successfully settled {count} ledger entries.'))
