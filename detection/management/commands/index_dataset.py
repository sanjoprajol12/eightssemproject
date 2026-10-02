"""
detection/management/commands/index_dataset.py
==============================================
Populates the SQLite FTS5 news index from the project datasets:
- train.csv, test.csv, valid.csv (LIAR benchmark with Statement, Label)
- liar_dataset/*.tsv (Multi-class benchmark mapped to real / fake)
- True.csv / Fake.csv (if provided)
- Deduplicates via SHA-256 hash
- Inserts into IndexedNews + FTS5 virtual table
"""

import os
import time
import csv
import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from detection.models import IndexedNews


class Command(BaseCommand):
    help = "Index news statements from project datasets into SQLite FTS5 with SHA-256 deduplication."

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=25000,
            help="Maximum records to index from all datasets (default: 25000)"
        )
        parser.add_argument(
            '--chunk-size',
            type=int,
            default=1000,
            help="Batch insert chunk size"
        )

    def handle(self, *args, **options):
        limit = options['limit']
        chunk_size = options['chunk_size']
        base_dir = str(settings.BASE_DIR)

        start_time = time.time()
        self.stdout.write(self.style.NOTICE(f"Indexing project datasets into FTS5 (limit: {limit})..."))

        existing_hashes = set(IndexedNews.objects.values_list('content_hash', flat=True))
        self.stdout.write(f"Existing indexed articles in DB: {len(existing_hashes)}")

        total_inserted = 0

        def save_batch(batch):
            nonlocal total_inserted
            if not batch:
                return
            with transaction.atomic():
                IndexedNews.objects.bulk_create(batch, ignore_conflicts=True)
            total_inserted += len(batch)

        # 1. Process Statement/Label CSV files (train.csv, test.csv, valid.csv)
        csv_files = ['train.csv', 'valid.csv', 'test.csv']
        for rel_csv in csv_files:
            csv_path = os.path.join(base_dir, rel_csv)
            if not os.path.exists(csv_path):
                continue

            self.stdout.write(f"Processing {rel_csv}...")
            batch = []
            try:
                df = pd.read_csv(csv_path, low_memory=False)
                # Drop invalid rows
                if 'Statement' in df.columns and 'Label' in df.columns:
                    for _, row in df.iterrows():
                        if total_inserted + len(batch) >= limit:
                            break
                        statement = str(row.get('Statement', '')).strip()
                        raw_label = str(row.get('Label', '')).strip().lower()
                        if not statement or statement.lower() == 'nan' or len(statement) < 8:
                            continue

                        label = 'real' if raw_label in ('true', '1', 'real', 'mostly-true') else 'fake'
                        chash = IndexedNews.compute_hash(statement)
                        if chash in existing_hashes:
                            continue

                        existing_hashes.add(chash)
                        batch.append(IndexedNews(
                            title=statement[:500],
                            summary=statement[:300],
                            source=f"Benchmark Dataset ({rel_csv})",
                            label=label,
                            content_hash=chash,
                            is_verified=(label == 'real')
                        ))

                        if len(batch) >= chunk_size:
                            save_batch(batch)
                            self.stdout.write(f"  Inserted {total_inserted} records...")
                            batch = []

                if batch:
                    save_batch(batch)
                    batch = []
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Could not read {rel_csv}: {e}"))

        # 2. Process liar_dataset TSV files
        tsv_files = [
            os.path.join(base_dir, 'liar_dataset', 'train.tsv'),
            os.path.join(base_dir, 'liar_dataset', 'valid.tsv'),
            os.path.join(base_dir, 'liar_dataset', 'test.tsv'),
        ]
        for tsv_path in tsv_files:
            if not os.path.exists(tsv_path) or total_inserted >= limit:
                continue

            rel_name = os.path.basename(tsv_path)
            self.stdout.write(f"Processing liar_dataset/{rel_name}...")
            batch = []
            try:
                with open(tsv_path, 'r', encoding='utf-8', errors='ignore') as f:
                    reader = csv.reader(f, delimiter='\t')
                    for row in reader:
                        if total_inserted + len(batch) >= limit:
                            break
                        if len(row) < 3:
                            continue
                        raw_label = row[1].strip().lower()
                        statement = row[2].strip()
                        if not statement or len(statement) < 8:
                            continue

                        # Map fine-grained labels
                        if raw_label in ('true', 'mostly-true', 'half-true'):
                            label = 'real'
                        else:
                            label = 'fake'

                        chash = IndexedNews.compute_hash(statement)
                        if chash in existing_hashes:
                            continue

                        subject = row[3] if len(row) > 3 else ''
                        speaker = row[4] if len(row) > 4 else ''
                        source_meta = f"LIAR ({speaker}: {subject})" if speaker else f"LIAR ({rel_name})"

                        existing_hashes.add(chash)
                        batch.append(IndexedNews(
                            title=statement[:500],
                            summary=statement[:300],
                            source=source_meta[:200],
                            label=label,
                            content_hash=chash,
                            is_verified=(label == 'real')
                        ))

                        if len(batch) >= chunk_size:
                            save_batch(batch)
                            self.stdout.write(f"  Inserted {total_inserted} records...")
                            batch = []

                if batch:
                    save_batch(batch)
                    batch = []
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Error reading {tsv_path}: {e}"))

        # 3. Check for True.csv and Fake.csv if available in workspace
        for fname, label in [('True.csv', 'real'), ('Fake.csv', 'fake')]:
            fpath = os.path.join(base_dir, fname)
            if os.path.exists(fpath) and total_inserted < limit:
                self.stdout.write(f"Processing {fname}...")
                batch = []
                try:
                    for chunk in pd.read_csv(fpath, chunksize=chunk_size, low_memory=False):
                        for _, row in chunk.iterrows():
                            if total_inserted + len(batch) >= limit:
                                break
                            title = str(row.get('title', '')).strip()
                            text = str(row.get('text', '')).strip()
                            if not title or len(title) < 10 or title.lower() == 'nan':
                                continue
                            chash = IndexedNews.compute_hash(title)
                            if chash in existing_hashes:
                                continue
                            existing_hashes.add(chash)
                            batch.append(IndexedNews(
                                title=title[:500],
                                summary=text[:300] if text else title[:300],
                                source=f"Kaggle/Reuters ({fname})",
                                label=label,
                                content_hash=chash,
                                is_verified=(label == 'real')
                            ))
                            if len(batch) >= chunk_size:
                                save_batch(batch)
                                batch = []
                        if total_inserted + len(batch) >= limit:
                            break
                    if batch:
                        save_batch(batch)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Error reading {fname}: {e}"))

        elapsed = round(time.time() - start_time, 2)
        total_in_db = IndexedNews.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"\n[COMPLETE] Successfully indexed {total_inserted} news records into database in {elapsed}s.\n"
            f"Total indexed articles in FTS database: {total_in_db}"
        ))
