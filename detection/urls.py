from django.urls import path
from detection import views

urlpatterns = [
    # Modern JSON APIs
    path('api/detect/', views.detect_api_view, name='api_detect'),
    path('api/detect/url/', views.detect_url_api_view, name='api_detect_url'),
    path('api/system/stats/', views.system_stats_api, name='api_system_stats'),
    path('api/detections/history/', views.detection_history_api, name='api_detection_history'),

    # Source / Domain credibility checker
    path('api/source/check/', views.source_check_api, name='api_source_check'),

    # Articles endpoints for dashboard
    path('api/articles/', views.articles_api, name='api_articles'),
    path('api/articles/<int:pk>/', views.article_detail_api, name='api_article_detail'),

    # Human-in-the-Loop Review Queue
    path('api/detections/needs-review/', views.needs_review_api, name='api_needs_review'),
    path('api/review-queue/', views.needs_review_api, name='api_review_queue_alias'),
    path('api/detections/<int:detection_id>/review/', views.review_detection_api, name='api_review_detection'),

    # History endpoints
    path('api/history/', views.detection_history_api, name='api_history_alias'),

    # ML Models Analytics & Training Endpoints
    path('api/models/summary/', views.models_summary_api, name='api_models_summary'),
    path('api/models/data/', views.models_data_api, name='api_models_data'),
    path('api/models/train/', views.models_train_api, name='api_models_train'),
    path('api/models/train/status/', views.models_train_status_api, name='api_models_train_status'),

    # Backward compatible detect endpoint
    path('detect/', views.legacy_detect_view, name='legacy_detect'),
]

