from django.db import models
from django.utils.text import slugify
from django.utils import timezone


class TimeStampedModel(models.Model):
    """Abstract base model with auto-managed created_at and updated_at fields."""
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    def active(self):
        return self.filter(deleted_at__isnull=True)

    def deleted(self):
        return self.filter(deleted_at__isnull=False)

    def hard_delete(self):
        return super().delete()

    def delete(self):
        return super().update(deleted_at=timezone.now())


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)

    def all_with_deleted(self):
        return SoftDeleteQuerySet(self.model, using=self._db)

    def deleted_only(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=False)


class SoftDeleteModel(models.Model):
    """Abstract base model supporting soft deletes."""
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def restore(self):
        self.deleted_at = None
        self.save(update_fields=['deleted_at'])

    def hard_delete(self):
        super().delete()


class SluggableModel(models.Model):
    """Abstract model providing unique slug auto-generation from a source field."""
    slug = models.SlugField(max_length=255, null=True, blank=True, db_index=True)

    class Meta:
        abstract = True

    def get_slug_source(self):
        for field in ['title', 'name']:
            if hasattr(self, field) and getattr(self, field):
                return getattr(self, field)
        return ''

    def save(self, *args, **kwargs):
        if not self.slug:
            source = self.get_slug_source()
            if source:
                base_slug = slugify(source)[:200]
                slug = base_slug
                counter = 1
                ModelClass = self.__class__
                while ModelClass.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1
                self.slug = slug
        super().save(*args, **kwargs)
