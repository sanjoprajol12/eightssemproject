from django.contrib import admin
from .models import (
    Album, AlbumValue, BlogCategory, Blog, Career, CareerApplication,
    Download, Enquiry, FaqCategory, Faq, Media, Menu, MenuItem,
    NewsAndUpdate, Notice, Page, Popup, Service, SiteSetting,
    PaymentGatewaySetting, SmsProviderSetting, Slider, SliderType,
    Team, Testimonial
)


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'position', 'event_date', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'description', 'tags')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(AlbumValue)
class AlbumValueAdmin(admin.ModelAdmin):
    list_display = ('title', 'album', 'position', 'is_featured', 'created_at')
    list_filter = ('is_featured', 'album')
    search_fields = ('title', 'path')


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'position', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'blog_category', 'publish_date', 'is_active', 'created_at')
    list_filter = ('is_active', 'blog_category')
    search_fields = ('title', 'description', 'keywords')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ('title', 'employment_type', 'no_of_vacancies', 'expiry_date', 'is_active')
    list_filter = ('is_active', 'employment_type')
    search_fields = ('title', 'description')


@admin.register(CareerApplication)
class CareerApplicationAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'career', 'email', 'phone', 'is_read', 'is_shortlisted', 'created_at')
    list_filter = ('is_read', 'is_shortlisted', 'career')
    search_fields = ('first_name', 'last_name', 'email', 'phone')


@admin.register(Download)
class DownloadAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'is_private', 'is_active', 'created_at')
    list_filter = ('is_active', 'is_private')
    search_fields = ('title', 'description')


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'mark_as_read', 'created_at')
    list_filter = ('mark_as_read',)
    search_fields = ('name', 'email', 'subject', 'message')


@admin.register(FaqCategory)
class FaqCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'position', 'type', 'is_active')
    list_filter = ('is_active', 'type')
    search_fields = ('name', 'description')


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ('title', 'faq_category', 'position', 'is_active')
    list_filter = ('is_active', 'faq_category')
    search_fields = ('title', 'description')


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'size', 'is_downloadable', 'is_featured', 'is_active', 'created_at')
    list_filter = ('type', 'is_active', 'is_featured')
    search_fields = ('title', 'path')


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'menu_type', 'header', 'is_active')
    list_filter = ('is_active', 'header')
    search_fields = ('title', 'menu_type')


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'menu', 'page', 'blog', 'position', 'display_on_website', 'is_active')
    list_filter = ('is_active', 'menu')
    search_fields = ('title', 'link')


@admin.register(NewsAndUpdate)
class NewsAndUpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_by', 'publish_date', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'published_by')


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_type', 'position', 'visible_from_date', 'is_active')
    list_filter = ('is_active', 'user_type')
    search_fields = ('name', 'description')


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'position', 'views', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Popup)
class PopupAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'position', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'type')
    search_fields = ('title', 'description')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'type', 'position', 'is_active')
    list_filter = ('is_active', 'type')
    search_fields = ('title', 'description')


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'email', 'phone', 'website', 'storage_type')
    search_fields = ('company_name', 'email', 'phone')


@admin.register(PaymentGatewaySetting)
class PaymentGatewaySettingAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'merchant_id', 'is_active')
    list_filter = ('is_active', 'type')
    search_fields = ('title', 'merchant_id')


@admin.register(SmsProviderSetting)
class SmsProviderSettingAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'sender', 'is_active')
    list_filter = ('is_active', 'type')
    search_fields = ('title', 'sender')


@admin.register(SliderType)
class SliderTypeAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title',)


@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'show_button', 'is_active', 'created_at')
    list_filter = ('is_active', 'show_button')
    search_fields = ('title', 'heading_text')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'type', 'position', 'email', 'contact_number', 'is_active')
    list_filter = ('is_active', 'type')
    search_fields = ('name', 'role', 'email')


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'position', 'status', 'is_active')
    list_filter = ('is_active', 'status', 'rating')
    search_fields = ('name', 'description')
