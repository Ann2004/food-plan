from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Subscription


class Command(BaseCommand):
    help = "Deletes unpaid (status='new') subscriptions older than 1 hour"

    def handle(self, *args, **options):
        cutoff = timezone.now() - timedelta(hours=1)
        qs = Subscription.objects.filter(
            status=Subscription.Status.NEW,
            created_at__lt=cutoff,
        )
        count = qs.count()
        qs.delete()
        self.stdout.write(f"Deleted {count} unpaid subscription(s).")
