# accounts/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import home, login_view, dashboard_view, register_template, register_view, index
from . import views

urlpatterns = [
    path('', index, name='index'),
    path('login/', home, name='login'),
    path('register/', views.register_view, name='register'),
    path('register-page/', views.register_template, name='register_template'),  
    path('login-view/', login_view, name='login_api'),  
    path('dashboard/', dashboard_view, name='dashboard'),
    
    # Article API endpoints
    path('api/articles/', views.articles_json, name='articles_json'),
    path('api/articles/<int:article_id>/', views.article_detail, name='article_detail'),
    
    # Admin management
    path('admin/<int:admin_id>/edit/', views.admin_edit, name='admin_edit'),
    path('admin/<int:admin_id>/delete/', views.admin_delete, name='admin_delete'),
    path('api/profile/', views.profile_api, name='profile_api'),
    
    path('logout/', views.logout_view, name='logout'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)