from rest_framework import viewsets, permissions, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.core.permissions import IsAdminRole
from apps.core.pagination import StandardResultsSetPagination

from .models import (
    Album, AlbumValue, BlogCategory, Blog, Career, CareerApplication,
    Download, Enquiry, FaqCategory, Faq, Media, Menu, MenuItem,
    NewsAndUpdate, Notice, Page, Popup, Service, SiteSetting,
    PaymentGatewaySetting, SmsProviderSetting, Slider, SliderType,
    Team, Testimonial
)
from .serializers import (
    AlbumSerializer, AlbumValueSerializer, BlogCategorySerializer, BlogSerializer,
    CareerSerializer, CareerApplicationSerializer, DownloadSerializer, EnquirySerializer,
    FaqCategorySerializer, FaqSerializer, MediaSerializer, MenuSerializer, MenuItemSerializer,
    NewsAndUpdateSerializer, NoticeSerializer, PageSerializer, PopupSerializer,
    ServiceSerializer, SiteSettingSerializer, PaymentGatewaySettingSerializer,
    SmsProviderSettingSerializer, SliderTypeSerializer, SliderSerializer,
    TeamSerializer, TestimonialSerializer
)


class BaseCmsViewSet(viewsets.ModelViewSet):
    """Base ViewSet enforcing Admin-only access, soft deletes, and pagination."""
    permission_classes = [IsAdminRole]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]


class AlbumViewSet(BaseCmsViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    search_fields = ['title', 'description', 'tags']


class AlbumValueViewSet(BaseCmsViewSet):
    queryset = AlbumValue.objects.all()
    serializer_class = AlbumValueSerializer
    search_fields = ['title', 'path']


class BlogCategoryViewSet(BaseCmsViewSet):
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    search_fields = ['title', 'description']


class BlogViewSet(BaseCmsViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    search_fields = ['title', 'description', 'keywords', 'seo_title']


class CareerViewSet(BaseCmsViewSet):
    queryset = Career.objects.all()
    serializer_class = CareerSerializer
    search_fields = ['title', 'employment_type', 'min_qualification', 'description']


class CareerApplicationViewSet(BaseCmsViewSet):
    queryset = CareerApplication.objects.all()
    serializer_class = CareerApplicationSerializer
    search_fields = ['first_name', 'last_name', 'email', 'phone']


class DownloadViewSet(BaseCmsViewSet):
    queryset = Download.objects.all()
    serializer_class = DownloadSerializer
    search_fields = ['title', 'description']


class EnquiryViewSet(BaseCmsViewSet):
    queryset = Enquiry.objects.all()
    serializer_class = EnquirySerializer
    search_fields = ['name', 'email', 'subject', 'message', 'phone']

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()


class FaqCategoryViewSet(BaseCmsViewSet):
    queryset = FaqCategory.objects.all()
    serializer_class = FaqCategorySerializer
    search_fields = ['name', 'description']


class FaqViewSet(BaseCmsViewSet):
    queryset = Faq.objects.all()
    serializer_class = FaqSerializer
    search_fields = ['title', 'description']


class MediaViewSet(BaseCmsViewSet):
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    search_fields = ['title', 'path', 'type']


class MenuViewSet(BaseCmsViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    search_fields = ['title', 'menu_type']


class MenuItemViewSet(BaseCmsViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    search_fields = ['title', 'link']


class NewsAndUpdateViewSet(BaseCmsViewSet):
    queryset = NewsAndUpdate.objects.all()
    serializer_class = NewsAndUpdateSerializer
    search_fields = ['title', 'published_by', 'url']


class NoticeViewSet(BaseCmsViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    search_fields = ['name', 'description', 'user_type']


class PageViewSet(BaseCmsViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    search_fields = ['title', 'content', 'seo_title']


class PopupViewSet(BaseCmsViewSet):
    queryset = Popup.objects.all()
    serializer_class = PopupSerializer
    search_fields = ['title', 'description', 'location']


class ServiceViewSet(BaseCmsViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    search_fields = ['title', 'type', 'description']


class SiteSettingViewSet(BaseCmsViewSet):
    queryset = SiteSetting.objects.all()
    serializer_class = SiteSettingSerializer
    search_fields = ['company_name', 'email', 'phone', 'website']


class PaymentGatewaySettingViewSet(BaseCmsViewSet):
    queryset = PaymentGatewaySetting.objects.all()
    serializer_class = PaymentGatewaySettingSerializer
    search_fields = ['title', 'type', 'merchant_id', 'app_id']


class SmsProviderSettingViewSet(BaseCmsViewSet):
    queryset = SmsProviderSetting.objects.all()
    serializer_class = SmsProviderSettingSerializer
    search_fields = ['title', 'type', 'sender']


class SliderTypeViewSet(BaseCmsViewSet):
    queryset = SliderType.objects.all()
    serializer_class = SliderTypeSerializer
    search_fields = ['title']


class SliderViewSet(BaseCmsViewSet):
    queryset = Slider.objects.all()
    serializer_class = SliderSerializer
    search_fields = ['title', 'heading_text', 'description']


class TeamViewSet(BaseCmsViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    search_fields = ['name', 'role', 'type', 'email', 'contact_number']


class TestimonialViewSet(BaseCmsViewSet):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    search_fields = ['name', 'description', 'type']


class CmsStatsView(APIView):
    """Returns total record counts across all CMS modules for the Admin Dashboard."""
    permission_classes = [IsAdminRole]

    def get(self, request):
        stats = {
            'albums': Album.objects.count(),
            'blogs': Blog.objects.count(),
            'blog_categories': BlogCategory.objects.count(),
            'careers': Career.objects.count(),
            'career_applications': CareerApplication.objects.count(),
            'downloads': Download.objects.count(),
            'enquiries': Enquiry.objects.count(),
            'faqs': Faq.objects.count(),
            'media': Media.objects.count(),
            'menus': Menu.objects.count(),
            'menu_items': MenuItem.objects.count(),
            'news_and_updates': NewsAndUpdate.objects.count(),
            'notices': Notice.objects.count(),
            'pages': Page.objects.count(),
            'popups': Popup.objects.count(),
            'services': Service.objects.count(),
            'sliders': Slider.objects.count(),
            'teams': Team.objects.count(),
            'testimonials': Testimonial.objects.count(),
            'payment_gateways': PaymentGatewaySetting.objects.count(),
            'sms_providers': SmsProviderSetting.objects.count(),
        }
        return Response(stats, status=status.HTTP_200_OK)
