from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from finance.models import LedgerEntry

class Command(BaseCommand):
    help = 'Process T+7 settlement for vendor ledger entries'

    def handle(self, *args, **options):
        from finance.services import FinanceService
        
        count = FinanceService.release_expired_funds()
        self.stdout.write(self.style.SUCCESS(f'Successfully processed and released funds for {count} orders.'))
