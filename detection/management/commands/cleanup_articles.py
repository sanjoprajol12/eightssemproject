"""
detection/management/commands/cleanup_articles.py
=================================================
Automated maintenance command implementing the data retention policy.
- Purges temporary/transient fetched articles older than N days (default: 30)
- Preserves all verified reference articles (`is_verified=True`)
- Cleans orphaned DetectionLogs older than 90 days
- Supports --dry-run mode
"""

from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from detection.models import IndexedNews, DetectionLog


class Command(BaseCommand):
    help = "Clean up transient indexed news according to the 30-day retention policy and purge old detection logs."

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help="Retention period in days for transient news (default: 30 days)"
        )
        parser.add_argument(
            '--log-days',
            type=int,
            default=90,
            help="Retention period in days for detection audit logs (default: 90 days)"
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Simulate the cleanup operation without deleting records"
        )

    def handle(self, *args, **options):
        days = options['days']
        log_days = options['log_days']
        dry_run = options['dry_run']

        now = timezone.now()
        cutoff_date = now - timedelta(days=days)
        log_cutoff = now - timedelta(days=log_days)

        self.stdout.write(self.style.NOTICE(
            f"Running article retention cleanup (cutoff: {cutoff_date.strftime('%Y-%m-%d %H:%M')})..."
        ))

        # Query transient unverified news older than retention cutoff
        transient_query = IndexedNews.objects.filter(
            is_verified=False,
            created_at__lt=cutoff_date
        )
        transient_count = transient_query.count()

        # Query old detection logs
        old_logs_query = DetectionLog.objects.filter(created_at__lt=log_cutoff)
        old_logs_count = old_logs_query.count()

        # Protected verified count
        verified_count = IndexedNews.objects.filter(is_verified=True).count()

        if dry_run:
            self.stdout.write(self.style.WARNING("[DRY RUN MODE] No records were modified."))
            self.stdout.write(f"  Transient news eligible for removal (> {days} days): {transient_count}")
            self.stdout.write(f"  Protected verified reference articles: {verified_count}")
            self.stdout.write(f"  Old audit logs eligible for removal (> {log_days} days): {old_logs_count}")
            return

        # Execute deletion
        deleted_transient, _ = transient_query.delete()
        deleted_logs, _ = old_logs_query.delete()

        self.stdout.write(self.style.SUCCESS(
            f"[CLEANUP COMPLETE]\n"
            f"  Removed expired transient news: {deleted_transient}\n"
            f"  Removed expired audit logs: {deleted_logs}\n"
            f"  Protected verified articles preserved: {verified_count}\n"
            f"  Active indexed news remaining: {IndexedNews.objects.count()}"
        ))
