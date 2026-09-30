from django.urls import path
from detection import views

urlpatterns = [
    # Modern JSON APIs
    path('api/detect/', views.detect_api_view, name='api_detect'),
    path('api/detect/url/', views.detect_url_api_view, name='api_detect_url'),
    path('api/system/stats/', views.system_stats_api, name='api_system_stats'),
    path('api/detections/history/', views.detection_history_api, name='api_detection_history'),

    # Backward compatible detect endpoint
    path('detect/', views.legacy_detect_view, name='legacy_detect'),
]
