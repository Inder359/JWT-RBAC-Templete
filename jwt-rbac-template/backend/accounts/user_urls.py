"""
URL Configuration for User Management (Admin/Manager endpoints)
"""

from django.urls import path
from .views import (
    UserListView,
    UserDetailView,
    UpdateUserRoleView,
)

urlpatterns = [
    # Admin/Manager endpoints
    path('', UserListView.as_view(), name='user_list'),
    path('<uuid:id>/', UserDetailView.as_view(), name='user_detail'),
    path('role/', UpdateUserRoleView.as_view(), name='update_user_role'),
]
