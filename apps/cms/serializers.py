from rest_framework import serializers
from .models import (
    Album, AlbumValue, BlogCategory, Blog, Career, CareerApplication,
    Download, Enquiry, FaqCategory, Faq, Media, Menu, MenuItem,
    NewsAndUpdate, Notice, Page, Popup, Service, SiteSetting,
    PaymentGatewaySetting, SmsProviderSetting, Slider, SliderType,
    Team, Testimonial
)


class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class AlbumValueSerializer(serializers.ModelSerializer):
    album_title = serializers.ReadOnlyField(source='album.title')

    class Meta:
        model = AlbumValue
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class BlogSerializer(serializers.ModelSerializer):
    category_title = serializers.ReadOnlyField(source='blog_category.title')

    class Meta:
        model = Blog
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class CareerSerializer(serializers.ModelSerializer):
    applications_count = serializers.IntegerField(source='applications.count', read_only=True)

    class Meta:
        model = Career
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class CareerApplicationSerializer(serializers.ModelSerializer):
    career_title = serializers.ReadOnlyField(source='career.title')

    class Meta:
        model = CareerApplication
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class DownloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Download
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class EnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class FaqCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FaqCategory
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class FaqSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='faq_category.name')

    class Meta:
        model = Faq
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class MenuItemSerializer(serializers.ModelSerializer):
    menu_title = serializers.ReadOnlyField(source='menu.title')

    class Meta:
        model = MenuItem
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class NewsAndUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsAndUpdate
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class PopupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Popup
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class SiteSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSetting
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class PaymentGatewaySettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentGatewaySetting
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class SmsProviderSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmsProviderSetting
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class SliderTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SliderType
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class SliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slider
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
