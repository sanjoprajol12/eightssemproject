"""
detection/management/commands/index_dataset.py
==============================================
Populates the SQLite FTS5 news index from True.csv and Fake.csv.
- Deduplicates via SHA-256 hash
- Inserts into IndexedNews + FTS5 virtual table
- Safe to re-run: Skips existing hashes
"""

import os
import time
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from detection.models import IndexedNews


class Command(BaseCommand):
    help = "Index historical news from CSV into SQLite FTS5 table with SHA-256 deduplication."

    def add_arguments(self, parser):
        parser.add_argument(
            '--true-csv',
            type=str,
            default=r"C:\Users\sanjo\OneDrive\Desktop\8th sem project\FakeNewsDetect\True.csv",
            help="Path to True.csv"
        )
        parser.add_argument(
            '--fake-csv',
            type=str,
            default=r"C:\Users\sanjo\OneDrive\Desktop\8th sem project\FakeNewsDetect\Fake.csv",
            help="Path to Fake.csv"
        )
        parser.add_argument(
            '--limit-per-label',
            type=int,
            default=5000,
            help="Maximum articles to index per label (default: 5000)"
        )
        parser.add_argument(
            '--chunk-size',
            type=int,
            default=1000,
            help="Batch chunk size for database inserts"
        )

    def handle(self, *args, **options):
        true_path = options['true_csv']
        fake_path = options['fake_csv']
        limit = options['limit_per_label']
        chunk_size = options['chunk_size']

        start_time = time.time()
        self.stdout.write(self.style.NOTICE(f"Starting news indexing (limit: {limit} per label)..."))

        # Pre-load existing hashes in memory to prevent duplicate DB lookups
        existing_hashes = set(IndexedNews.objects.values_list('content_hash', flat=True))
        self.stdout.write(f"Existing indexed articles: {len(existing_hashes)}")

        total_inserted = 0

        # Helper to process a CSV file
        def index_file(filepath, label, source_name):
            nonlocal total_inserted
            if not os.path.exists(filepath):
                self.stdout.write(self.style.WARNING(f"File not found: {filepath}"))
                return

            self.stdout.write(f"Reading {filepath} for [{label.upper()}] news...")
            count = 0
            batch = []

            try:
                # Read line by line or in chunks to avoid memory spike
                for chunk in pd.read_csv(filepath, chunksize=chunk_size, low_memory=False):
                    for _, row in chunk.iterrows():
                        if count >= limit:
                            break

                        title = str(row.get('title', '')).strip()
                        if not title or len(title) < 10 or title.lower() == 'nan':
                            continue

                        text = str(row.get('text', '')).strip()
                        summary = text[:300] if text and text.lower() != 'nan' else ''

                        chash = IndexedNews.compute_hash(title, summary)
                        if chash in existing_hashes:
                            continue

                        existing_hashes.add(chash)
                        batch.append(IndexedNews(
                            title=title[:500],
                            summary=summary,
                            source=source_name,
                            label=label,
                            content_hash=chash,
                            is_verified=(label == 'real') # Real seed articles are verified
                        ))
                        count += 1

                        if len(batch) >= chunk_size:
                            with transaction.atomic():
                                IndexedNews.objects.bulk_create(batch, ignore_conflicts=True)
                            self.stdout.write(f"  Indexed {count} [{label}] articles...")
                            batch = []

                    if count >= limit:
                        break

                if batch:
                    with transaction.atomic():
                        IndexedNews.objects.bulk_create(batch, ignore_conflicts=True)
                    batch = []

                self.stdout.write(self.style.SUCCESS(f"Finished [{label.upper()}]: {count} new articles indexed."))
                total_inserted += count

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing {filepath}: {e}"))

        # 1. Index Real News
        index_file(true_path, 'real', 'Reuters / Verified Corpus')

        # 2. Index Fake News
        index_file(fake_path, 'fake', 'Kaggle Fake Corpus')

        elapsed = round(time.time() - start_time, 2)
        total_in_db = IndexedNews.objects.count()

        self.stdout.write(self.style.SUCCESS(
            f"\n[COMPLETE] Successfully indexed {total_inserted} articles in {elapsed}s.\n"
            f"Total indexed articles in FTS database: {total_in_db}"
        ))
