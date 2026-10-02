from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AlbumViewSet, AlbumValueViewSet, BlogCategoryViewSet, BlogViewSet,
    CareerViewSet, CareerApplicationViewSet, DownloadViewSet, EnquiryViewSet,
    FaqCategoryViewSet, FaqViewSet, MediaViewSet, MenuViewSet, MenuItemViewSet,
    NewsAndUpdateViewSet, NoticeViewSet, PageViewSet, PopupViewSet,
    ServiceViewSet, SiteSettingViewSet, PaymentGatewaySettingViewSet,
    SmsProviderSettingViewSet, SliderTypeViewSet, SliderViewSet,
    TeamViewSet, TestimonialViewSet, CmsStatsView
)

router = DefaultRouter()
router.register(r'albums', AlbumViewSet, basename='album')
router.register(r'album-values', AlbumValueViewSet, basename='album-value')
router.register(r'blog-categories', BlogCategoryViewSet, basename='blog-category')
router.register(r'blogs', BlogViewSet, basename='blog')
router.register(r'careers', CareerViewSet, basename='career')
router.register(r'career-applications', CareerApplicationViewSet, basename='career-application')
router.register(r'downloads', DownloadViewSet, basename='download')
router.register(r'enquiries', EnquiryViewSet, basename='enquiry')
router.register(r'faq-categories', FaqCategoryViewSet, basename='faq-category')
router.register(r'faqs', FaqViewSet, basename='faq')
router.register(r'media', MediaViewSet, basename='media')
router.register(r'menus', MenuViewSet, basename='menu')
router.register(r'menu-items', MenuItemViewSet, basename='menu-item')
router.register(r'news-and-updates', NewsAndUpdateViewSet, basename='news-and-update')
router.register(r'notices', NoticeViewSet, basename='notice')
router.register(r'pages', PageViewSet, basename='page')
router.register(r'popups', PopupViewSet, basename='popup')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'site-settings', SiteSettingViewSet, basename='site-setting')
router.register(r'payment-gateway-settings', PaymentGatewaySettingViewSet, basename='payment-gateway-setting')
router.register(r'sms-provider-settings', SmsProviderSettingViewSet, basename='sms-provider-setting')
router.register(r'slider-types', SliderTypeViewSet, basename='slider-type')
router.register(r'sliders', SliderViewSet, basename='slider')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'testimonials', TestimonialViewSet, basename='testimonial')

urlpatterns = [
    path('stats/', CmsStatsView.as_view(), name='cms-stats'),
    path('', include(router.urls)),
]
