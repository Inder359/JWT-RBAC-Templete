"""
Custom User Model with Role-Based Access Control (RBAC)
"""

import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    """User roles for RBAC"""
    ADMIN = 'admin', _('Admin')
    MANAGER = 'manager', _('Manager')
    USER = 'user', _('User')


class User(AbstractUser):
    """
    Custom User model with role-based access control.
    Inherits all fields from AbstractUser and adds role field.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.USER,
        help_text=_('User role for access control')
    )
    
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _('A user with that email already exists.'),
        },
    )
    
    is_verified = models.BooleanField(
        _('verified'),
        default=False,
        help_text=_('Designates whether the user has verified their email.')
    )
    
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('last login IP')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Require email for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()
    
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == UserRole.ADMIN
    
    def is_manager(self):
        """Check if user has manager role"""
        return self.role == UserRole.MANAGER
    
    def is_user(self):
        """Check if user has regular user role"""
        return self.role == UserRole.USER
    
    def has_role(self, role):
        """Check if user has specific role"""
        return self.role == role
    
    def has_roles(self, roles):
        """Check if user has any of the specified roles"""
        return self.role in roles


class UserProfile(models.Model):
    """
    Extended user profile information.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('phone number')
    )
    
    bio = models.TextField(
        blank=True,
        verbose_name=_('bio')
    )
    
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name=_('avatar')
    )
    
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('date of birth')
    )
    
    address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('address')
    )
    
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('city')
    )
    
    country = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('country')
    )
    
    # Social links
    github = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('GitHub')
    )
    
    linkedin = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('LinkedIn')
    )
    
    website = models.URLField(
        blank=True,
        verbose_name=_('website')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
    
    def __str__(self):
        return f"Profile for {self.user.email}"
    
    def save(self, *args, **kwargs):
        """Create profile if it doesn't exist when user is created"""
        if not self.pk and self.user_id:
            # Check if profile already exists
            if UserProfile.objects.filter(user_id=self.user_id).exists():
                return
        super().save(*args, **kwargs)
