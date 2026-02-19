"""
URL Configuration for Accounts Application
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    TokenRefreshCookieView,
    CurrentUserView,
    ChangePasswordView,
    UpdateProfileView,
)

urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshCookieView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
    
    # User endpoints
    path('me/', CurrentUserView.as_view(), name='current_user'),
    path('password/', ChangePasswordView.as_view(), name='change_password'),
    path('profile/', UpdateProfileView.as_view(), name='update_profile'),
]
