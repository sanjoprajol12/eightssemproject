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
    result = models.CharField(max_length=50)  # 'Real News', 'Fake News', 'Inconclusive'
    confidence = models.FloatField(default=0.0)
    source_info = models.CharField(max_length=255, blank=True)
    evidence = models.JSONField(default=dict, blank=True)
    model_predictions = models.JSONField(default=dict, blank=True)
    explanation = models.JSONField(default=list, blank=True)
    response_time_ms = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # Human-in-the-loop review fields
    needs_review = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Auto-flagged when confidence is in the borderline 40–65% range."
    )
    is_reviewed = models.BooleanField(
        default=False,
        help_text="Set to True once a human reviewer has validated this detection."
    )
    reviewer_verdict = models.CharField(
        max_length=50, blank=True, default='',
        help_text="Human reviewer override verdict."
    )

    # Bias analysis fields
    bias_label = models.CharField(
        max_length=100, blank=True, default='',
        help_text="Detected bias type, e.g. 'Political Right', 'Emotional Alarmism'."
    )
    political_lean = models.CharField(
        max_length=20, blank=True, default='',
        help_text="Detected political lean: left, right, center, or neutral."
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.created_at.strftime('%Y-%m-%d %H:%M')} - {self.result} ({self.confidence:.1f}%)"


class Article(models.Model):
    """
    User/Admin curated articles repository.
    Mapped to existing accounts_article database table.
    """
    image = models.ImageField(upload_to='articles/', blank=True, null=True)
    title = models.CharField(max_length=255)
    username = models.CharField(max_length=100, default='Admin')
    description = models.TextField(blank=True, default='')
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)
    admin_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_article'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
