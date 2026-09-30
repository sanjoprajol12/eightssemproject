from django.db import models
from django.core.exceptions import ValidationError
import os

def validate_image_extension(value):
    """Validate that the uploaded file is an image"""
    if value:
        ext = os.path.splitext(value.name)[1].lower()
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        if ext not in valid_extensions:
            raise ValidationError(f'Unsupported file extension. Allowed extensions: {", ".join(valid_extensions)}')

def validate_image_size(value):
    """Validate that the uploaded image is not too large"""
    if value:
        if value.size > 10 * 1024 * 1024:  # 5MB
            raise ValidationError('Image file too large. Maximum size is 5MB.')
class Admin(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store hashed passwords (see notes below)
    phone = models.CharField(max_length=20, blank=True)
    note = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return self.name

class Article(models.Model):
    image = models.ImageField(
        upload_to='articles/', 
        blank=True, 
        null=True,
        validators=[validate_image_extension, validate_image_size],
        help_text="Upload an image (JPG, PNG, GIF, WebP). Maximum size: 5MB."
    )
    title = models.CharField(max_length=255)
    username = models.CharField(max_length=100)
    description = models.TextField()
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    admin = models.ForeignKey('Admin', on_delete=models.CASCADE, related_name='articles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        """Override delete method to also delete the image file"""
        if self.image:
            try:
                if os.path.isfile(self.image.path):
                    os.remove(self.image.path)
            except (ValueError, OSError):
                pass
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        """Override save method for additional image processing if needed"""
        # If this is an update and the image has changed, delete the old image
        if self.pk:
            try:
                old_instance = Article.objects.get(pk=self.pk)
                if old_instance.image != self.image and old_instance.image:
                    try:
                        if os.path.isfile(old_instance.image.path):
                            os.remove(old_instance.image.path)
                    except (ValueError, OSError):
                        pass
            except Article.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
