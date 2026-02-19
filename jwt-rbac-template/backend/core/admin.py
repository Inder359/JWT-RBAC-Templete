"""
Core Application Admin Configuration
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin"""
    
    list_display = ('email', 'username', 'role', 'is_verified', 'is_active', 'created_at')
    list_filter = ('role', 'is_verified', 'is_active', 'is_staff', 'created_at')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role & Verification', {
            'fields': ('role', 'is_verified')
        }),
        ('Additional Info', {
            'fields': ('last_login_ip', 'created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """User Profile Admin"""
    
    list_display = ('user', 'phone', 'city', 'country', 'created_at')
    list_filter = ('country', 'city')
    search_fields = ('user__email', 'user__username', 'phone', 'bio')
    raw_id_fields = ('user',)
    
    readonly_fields = ('created_at', 'updated_at')
