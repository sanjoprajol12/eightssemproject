from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginView, LogoutView, MeView, UserViewSet, RegisterView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('me/', MeView.as_view(), name='auth-me'),
    path('', include(router.urls)),
]
