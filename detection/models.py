from django.db import models
from django.utils import timezone
import hashlib


class IndexedNews(models.Model):
    """
    High-performance searchable news index replacing full CSV linear scans.
    Stores metadata, clean title, brief summary, and a SHA-256 content hash
    for instantaneous duplicate detection.
    """
    LABEL_CHOICES = (
        ('real', 'Real News'),
        ('fake', 'Fake News'),
    )

    title = models.CharField(max_length=500, db_index=True)
    summary = models.TextField(blank=True, default='')
    source = models.CharField(max_length=200, default='Seed Dataset', db_index=True)
    label = models.CharField(max_length=10, choices=LABEL_CHOICES, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    content_hash = models.CharField(max_length=64, unique=True, db_index=True)
    is_verified = models.BooleanField(
        default=False,
        help_text="Protected reference article that will not be purged by retention cleanup."
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['label', 'created_at']),
            models.Index(fields=['content_hash']),
        ]

    def __str__(self):
        return f"[{self.label.upper()}] {self.title[:60]}"

    @staticmethod
    def compute_hash(title: str, text: str = "") -> str:
        """Normalized SHA-256 hash to prevent duplicates."""
        norm_title = " ".join((title or "").strip().lower().split())
        return hashlib.sha256(norm_title.encode('utf-8')).hexdigest()

    def save(self, *args, **kwargs):
        if not self.content_hash:
            self.content_hash = self.compute_hash(self.title, self.summary)
        super().save(*args, **kwargs)


class DetectionLog(models.Model):
    """
    Log of detection requests for auditing, dashboard statistics, and explainability tracking.
    """
    INPUT_CHOICES = (
        ('text', 'Text Input'),
        ('url', 'URL Input'),
    )

    query_text = models.TextField()
    input_type = models.CharField(max_length=10, choices=INPUT_CHOICES, default='text')
    url = models.URLField(max_length=1000, blank=True, null=True)
    result = models.CharField(max_length=50) # 'Real News', 'Fake News', 'Inconclusive'
    confidence = models.FloatField(default=0.0)
    source_info = models.CharField(max_length=255, blank=True)
    evidence = models.JSONField(default=dict, blank=True)
    model_predictions = models.JSONField(default=dict, blank=True)
    explanation = models.JSONField(default=list, blank=True)
    response_time_ms = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.created_at.strftime('%Y-%m-%d %H:%M')} - {self.result} ({self.confidence:.1f}%)"
