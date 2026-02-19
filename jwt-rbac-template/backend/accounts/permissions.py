"""
Custom Permissions for Role-Based Access Control (RBAC)
"""

from rest_framework import permissions
from core.models import UserRole


class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to admin users.
    """
    
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == UserRole.ADMIN
        )


class IsManagerOrAdmin(permissions.BasePermission):
    """
    Allows access to manager and admin users.
    """
    
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in [UserRole.MANAGER, UserRole.ADMIN]
        )


class IsUserOrAbove(permissions.BasePermission):
    """
    Allows access to all authenticated users (user, manager, admin).
    """
    
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in [UserRole.USER, UserRole.MANAGER, UserRole.ADMIN]
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allows access to admin users or the owner of the object.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin can access everything
        if request.user.role == UserRole.ADMIN:
            return True
        
        # Check if user owns the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        if hasattr(obj, 'email'):
            return obj.email == request.user.email
        
        return False


class IsVerifiedUser(permissions.BasePermission):
    """
    Allows access only to verified users.
    """
    
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_verified
        )


def check_role(user, allowed_roles):
    """
    Helper function to check if user has one of the allowed roles.
    
    Args:
        user: The user object to check
        allowed_roles: List of allowed role strings
    
    Returns:
        bool: True if user has an allowed role
    """
    if not user or not user.is_authenticated:
        return False
    return user.role in allowed_roles
