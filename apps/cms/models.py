from django.db import models
from apps.core.models import TimeStampedModel, SoftDeleteModel, SluggableModel


# ─────────────────────────────────────────────────────────────────────────────
# 1 & 2. ALBUMS & ALBUM VALUES
# ─────────────────────────────────────────────────────────────────────────────
class Album(TimeStampedModel, SoftDeleteModel, SluggableModel):
    title = models.CharField(max_length=255, null=True, blank=True)
    cover_image = models.TextField(null=True, blank=True, help_text="Image file path or URL")
    description = models.TextField(null=True, blank=True)
    tags = models.CharField(max_length=255, null=True, blank=True)
    position = models.IntegerField(null=True, blank=True, default=0)
    event_date = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    album_id = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_albums')

    class Meta:
        db_table = 'albums'
        ordering = ['position', '-created_at']

    def __str__(self):
        return self.title or f"Album #{self.pk}"


class AlbumValue(TimeStampedModel, SoftDeleteModel, SluggableModel):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True, blank=True, related_name='values')
    title = models.CharField(max_length=255, null=True, blank=True)
    path = models.TextField(null=True, blank=True, help_text="Image or asset path")
    is_featured = models.BooleanField(default=False)
    position = models.IntegerField(null=True, blank=True, default=0)

    class Meta:
        db_table = 'album_values'
        ordering = ['position', '-created_at']

    def __str__(self):
        return self.title or f"AlbumValue #{self.pk}"


# ─────────────────────────────────────────────────────────────────────────────
# 3 & 4. BLOGS & CATEGORIES
# ─────────────────────────────────────────────────────────────────────────────
class BlogCategory(TimeStampedModel, SoftDeleteModel, SluggableModel):
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    position = models.IntegerField(null=True, blank=True, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'blog_categories'
        verbose_name_plural = 'Blog Categories'
        ordering = ['position', 'title']

    def __str__(self):
        return self.title or f"BlogCategory #{self.pk}"


class Blog(TimeStampedModel, SoftDeleteModel, SluggableModel):
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(null=True, blank=True)
    keywords = models.CharField(max_length=255, null=True, blank=True)
    publish_date = models.DateTimeField(null=True, blank=True)
    seo_title = models.CharField(max_length=255, null=True, blank=True)
    seo_keywords = models.CharField(max_length=255, null=True, blank=True)
    seo_description = models.TextField(null=True, blank=True)
    image = models.TextField(null=True, blank=True)
    blog_category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='blogs')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'blogs'
        ordering = ['-publish_date', '-created_at']

    def __str__(self):
        return self.title


# ─────────────────────────────────────────────────────────────────────────────
# 5 & 6. CAREERS & APPLICATIONS
# ─────────────────────────────────────────────────────────────────────────────
class Career(TimeStampedModel, SoftDeleteModel, SluggableModel):
    title = models.CharField(max_length=255, null=True, blank=True)
    employment_type = models.CharField(max_length=100, null=True, blank=True)
    no_of_vacancies = models.IntegerField(null=True, blank=True, default=1)
    salary_offer = models.IntegerField(null=True, blank=True)
    opened_at = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    min_qualification = models.CharField(max_length=255, null=True, blank=True)
    position = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'careers'
        ordering = ['-created_at']

    def __str__(self):
        return self.title or f"Career #{self.pk}"


class CareerApplication(TimeStampedModel, SoftDeleteModel):
    career = models.ForeignKey(Career, on_delete=models.CASCADE, null=True, blank=True, related_name='applications')
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    file = models.TextField(null=True, blank=True, help_text="Resume file path or URL")
    received_at = models.CharField(max_length=100, null=True, blank=True)
    is_read = models.CharField(max_length=50, null=True, blank=True, default='0')
    is_shortlisted = models.CharField(max_length=50, null=True, blank=True, default='0')

    class Meta:
        db_table = 'career_applications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


# ─────────────────────────────────────────────────────────────────────────────
# 7. DOWNLOADS
# ─────────────────────────────────────────────────────────────────────────────
class Download(TimeStampedModel, SoftDeleteModel, SluggableModel):
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    position = models.IntegerField(null=True, blank=True, default=0)
    path = models.TextField(null=True, blank=True)
    file_path = models.TextField(null=True, blank=True)
    preview_image = models.TextField(null=True, blank=True)
    is_private = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'downloads'
        ordering = ['position', '-created_at']

    def __str__(self):
        return self.title or f"Download #{self.pk}"


# ─────────────────────────────────────────────────────────────────────────────
# 8. ENQUIRIES
# ─────────────────────────────────────────────────────────────────────────────
class Enquiry(TimeStampedModel, SoftDeleteModel, SluggableModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    token = models.CharField(max_length=255, null=True, blank=True)
    mark_as_read = models.BooleanField(default=False)

    class Meta:
        db_table = 'enquiries'
        verbose_name_plural = 'Enquiries'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"


# ─────────────────────────────────────────────────────────────────────────────
# 9 & 10. FAQS & FAQ CATEGORIES
# ─────────────────────────────────────────────────────────────────────────────
class FaqCategory(TimeStampedModel, SoftDeleteModel, SluggableModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    position = models.IntegerField(null=True, blank=True, default=0)
    type = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'faq_categories'
        verbose_name_plural = 'FAQ Categories'
        ordering = ['position', 'name']

    def __str__(self):
        return self.name


class Faq(TimeStampedModel, SoftDeleteModel, SluggableModel):
    faq_category = models.ForeignKey(FaqCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='faqs')
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(null=True, blank=True)
    position = models.IntegerField(null=True, blank=True, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'faqs'
        ordering = ['position', '-created_at']

    def __str__(self):
        return self.title


# ─────────────────────────────────────────────────────────────────────────────
# 11. MEDIA
# ─────────────────────────────────────────────────────────────────────────────
class Media(TimeStampedModel, SoftDeleteModel):
    path = models.TextField()
    title = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=50, default='other')
    size = models.FloatField(null=True, blank=True)
    is_downloadable = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    uploaded_by = models.CharField(max_length=150, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'medias'
        verbose_name_plural = 'Media'
        ordering = ['-created_at']

    def __str__(self):
        return self.title or self.path


# ─────────────────────────────────────────────────────────────────────────────
# 12 & 13. MENUS & MENU ITEMS
# ─────────────────────────────────────────────────────────────────────────────
class Menu(TimeStampedModel, SoftDeleteModel):
    title = models.CharField(max_length=255)
    position = models.IntegerField(null=True, blank=True, default=0)
    menu_type = models.CharField(max_length=100, null=True, blank=True)
    header = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'menus'
        ordering = ['position', 'title']

    def __str__(self):
        return self.title


class MenuItem(TimeStampedModel, SoftDeleteModel):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, null=True, blank=True, related_name='items')
    page = models.ForeignKey('Page', on_delete=models.CASCADE, null=True, blank=True, related_name='menu_items')
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, null=True, blank=True, related_name='menu_items')
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=50, null=True, blank=True)
    link = models.TextField(null=True, blank=True)
    position = models.IntegerField(null=True, blank=True, default=0)
    new_tab = models.BooleanField(default=False)
    display_on_website = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'menu_items'
        ordering = ['position', 'title']

    def __str__(self):
        return self.title


# ─────────────────────────────────────────────────────────────────────────────
# 14. NEWS AND UPDATES
# ─────────────────────────────────────────────────────────────────────────────
class NewsAndUpdate(TimeStampedModel, SoftDeleteModel, SluggableModel):
    title = models.CharField(max_length=255, db_index=True)
    url = models.TextField(null=True, blank=True)
    published_by = models.CharField(max_length=150, null=True, blank=True)
    publish_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'news_and_updates'
        verbose_name_plural = 'News & Updates'
        ordering = ['-publish_date', '-created_at']

    def __str__(self):
        return self.title


# ─────────────────────────────────────────────────────────────────────────────
# 15. NOTICES
# ─────────────────────────────────────────────────────────────────────────────
class Notice(TimeStampedModel, SoftDeleteModel, SluggableModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    user_type = models.CharField(max_length=100, default='all')
    position = models.IntegerField(default=0)
    visible_from_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'notices'
        ordering = ['position', '-created_at']

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────────────────────────────────────
# 16. PAGES
# ─────────────────────────────────────────────────────────────────────────────
class Page(TimeStampedModel, SoftDeleteModel, SluggableModel):
    title = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    position = models.BigIntegerField(null=True, blank=True, default=0)
    seo_title = models.CharField(max_length=255, null=True, blank=True)
    seo_keyword = models.CharField(max_length=255, null=True, blank=True)
    seo_description = models.TextField(null=True, blank=True)
    views = models.BigIntegerField(null=True, blank=True, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'pages'
        ordering = ['position', 'title']

    def __str__(self):
        return self.title or f"Page #{self.pk}"


# ─────────────────────────────────────────────────────────────────────────────
# 17. POPUPS
# ─────────────────────────────────────────────────────────────────────────────
class Popup(TimeStampedModel, SoftDeleteModel, SluggableModel):
    title = models.CharField(max_length=255, null=True, blank=True)
    position = models.IntegerField(null=True, blank=True, default=0)
    description = models.TextField(null=True, blank=True)
    link = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    video_url = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    show_location = models.CharField(max_length=100, null=True, blank=True)
    image = models.TextField(null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'popups'
        ordering = ['position', '-created_at']

    def __str__(self):
        return self.title or f"Popup #{self.pk}"


# ─────────────────────────────────────────────────────────────────────────────
# 18. SERVICES
# ─────────────────────────────────────────────────────────────────────────────
class Service(TimeStampedModel, SoftDeleteModel):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    position = models.IntegerField(null=True, blank=True, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'services'
        ordering = ['position', 'title']

    def __str__(self):
        return self.title


# ─────────────────────────────────────────────────────────────────────────────
# 19. SITE SETTING
# ─────────────────────────────────────────────────────────────────────────────
class SiteSetting(TimeStampedModel, SoftDeleteModel):
    company_name = models.CharField(max_length=255, default='Fake News')
    description = models.TextField(null=True, blank=True)
    slogan = models.CharField(max_length=255, null=True, blank=True)
    tagline = models.CharField(max_length=255, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    date_format = models.CharField(max_length=50, default='d/m/Y')
    copy_right_text = models.CharField(max_length=255, null=True, blank=True)
    terms_condition = models.TextField(null=True, blank=True)

    # Contact
    mobile = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    map_url = models.TextField(null=True, blank=True)
    zoom_link = models.TextField(null=True, blank=True)

    # Social Links
    facebook = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    youtube = models.URLField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    tiktok = models.URLField(null=True, blank=True)
    pinterest = models.URLField(null=True, blank=True)
    viber = models.CharField(max_length=50, null=True, blank=True)
    whatsapp = models.CharField(max_length=50, null=True, blank=True)
    play_store_link = models.URLField(null=True, blank=True)
    app_store_link = models.URLField(null=True, blank=True)

    # Tracking & Widgets
    facebook_chat_widgets = models.TextField(null=True, blank=True)
    google_analytics = models.TextField(null=True, blank=True)
    pixels = models.TextField(null=True, blank=True)

    # Cookies
    enable_cookies = models.BooleanField(default=False)
    cookie_content_text = models.TextField(null=True, blank=True)

    # Logos & Images
    fav_icon = models.TextField(null=True, blank=True)
    logo = models.TextField(null=True, blank=True)
    login_bg_image = models.TextField(null=True, blank=True)
    app_logo = models.TextField(null=True, blank=True)
    email_logo_image = models.TextField(null=True, blank=True)
    footer_logo = models.TextField(null=True, blank=True)

    # reCAPTCHA
    recaptcha_site_key = models.CharField(max_length=255, null=True, blank=True)
    recaptcha_secret_key = models.CharField(max_length=255, null=True, blank=True)

    # Mail Configuration
    mail_driver = models.CharField(max_length=50, null=True, blank=True)
    mail_host = models.CharField(max_length=150, null=True, blank=True)
    mail_port = models.CharField(max_length=20, null=True, blank=True)
    mail_user_name = models.CharField(max_length=150, null=True, blank=True)
    mail_password = models.CharField(max_length=255, null=True, blank=True)
    mail_encryption = models.CharField(max_length=50, null=True, blank=True)
    mail_sender_name = models.CharField(max_length=150, null=True, blank=True)
    mail_sender_address = models.CharField(max_length=150, null=True, blank=True)

    # Storage Configuration
    storage_url = models.TextField(null=True, blank=True)
    storage_type = models.CharField(max_length=50, default='local')
    storage_access_key = models.CharField(max_length=255, null=True, blank=True)
    storage_secret_key = models.CharField(max_length=255, null=True, blank=True)
    storage_region = models.CharField(max_length=100, null=True, blank=True)
    storage_endpoint = models.CharField(max_length=255, null=True, blank=True)
    storage_bucket_name = models.CharField(max_length=150, null=True, blank=True)

    # Tax & Registration
    tax_percentage = models.CharField(max_length=20, null=True, blank=True)
    pan_no = models.CharField(max_length=50, null=True, blank=True)
    vat_no = models.CharField(max_length=50, null=True, blank=True)
    is_admission_form_active = models.BooleanField(default=False)

    # SEO
    seo_title = models.CharField(max_length=255, null=True, blank=True)
    seo_keyword = models.CharField(max_length=255, null=True, blank=True)
    seo_description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'site_settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.company_name


# ─────────────────────────────────────────────────────────────────────────────
# 20. PAYMENT GATEWAY SETTING
# ─────────────────────────────────────────────────────────────────────────────
class PaymentGatewaySetting(TimeStampedModel, SoftDeleteModel):
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=100)
    merchant_id = models.CharField(max_length=255, null=True, blank=True)
    public_key = models.TextField(null=True, blank=True)
    private_key = models.TextField(null=True, blank=True)
    app_id = models.CharField(max_length=255, null=True, blank=True)
    app_name = models.CharField(max_length=255, null=True, blank=True)
    user_name = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    pfx_password = models.CharField(max_length=255, null=True, blank=True)
    bank_qr_code = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'payment_gateway_settings'
        ordering = ['title']

    def __str__(self):
        return f"{self.title} ({self.type})"


# ─────────────────────────────────────────────────────────────────────────────
# 21. SMS PROVIDER SETTING
# ─────────────────────────────────────────────────────────────────────────────
class SmsProviderSetting(TimeStampedModel, SoftDeleteModel):
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=100)
    token = models.TextField(null=True, blank=True)
    sender = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'sms_provider_settings'
        ordering = ['title']

    def __str__(self):
        return f"{self.title} ({self.sender})"


# ─────────────────────────────────────────────────────────────────────────────
# 22 & 23. SLIDERS & SLIDER TYPES
# ─────────────────────────────────────────────────────────────────────────────
class SliderType(TimeStampedModel, SoftDeleteModel, SluggableModel):
    title = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'slider_types'
        ordering = ['title']

    def __str__(self):
        return self.title


class Slider(TimeStampedModel, SoftDeleteModel, SluggableModel):
    title = models.CharField(max_length=255, null=True, blank=True)
    link = models.TextField(null=True, blank=True)
    position = models.IntegerField(null=True, blank=True, default=0)
    new_tab = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    heading_text = models.CharField(max_length=255, null=True, blank=True)
    sub_heading_text = models.CharField(max_length=255, null=True, blank=True)
    button_text = models.CharField(max_length=100, null=True, blank=True)
    show_button = models.BooleanField(default=True)
    image = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'sliders'
        ordering = ['position', '-created_at']

    def __str__(self):
        return self.title or f"Slider #{self.pk}"


# ─────────────────────────────────────────────────────────────────────────────
# 24. TEAM
# ─────────────────────────────────────────────────────────────────────────────
class Team(TimeStampedModel, SoftDeleteModel, SluggableModel):
    name = models.CharField(max_length=255)
    position = models.IntegerField(default=0)
    branch_id = models.BigIntegerField(null=True, blank=True)
    role = models.CharField(max_length=150, null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    fb_url = models.URLField(null=True, blank=True)
    linked_url = models.URLField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    contact_number = models.CharField(max_length=50, null=True, blank=True)
    whatsapp_number = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'teams'
        ordering = ['position', 'name']

    def __str__(self):
        return f"{self.name} - {self.role or 'Member'}"


# ─────────────────────────────────────────────────────────────────────────────
# 25. TESTIMONIALS
# ─────────────────────────────────────────────────────────────────────────────
class Testimonial(TimeStampedModel, SoftDeleteModel, SluggableModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    image = models.TextField(null=True, blank=True)
    position = models.IntegerField(null=True, blank=True, default=0)
    rating = models.IntegerField(null=True, blank=True, default=5)
    status = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'testimonials'
        ordering = ['position', '-created_at']

    def __str__(self):
        return self.name or f"Testimonial #{self.pk}"
