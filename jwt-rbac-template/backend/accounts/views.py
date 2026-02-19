"""
API Views for Accounts Application
"""

import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema, extend_schema_view

from core.models import User, UserProfile
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    UserDetailSerializer, ChangePasswordSerializer,
    UpdateUserSerializer, UpdateProfileSerializer,
    RoleUpdateSerializer
)
from .permissions import IsAdminUser, IsManagerOrAdmin, IsUserOrAbove

logger = logging.getLogger(__name__)
User = get_user_model()


def get_tokens_for_user(user):
    """Generate JWT tokens for user"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def set_cookie_tokens(response, tokens):
    """Set tokens as HTTPOnly cookies"""
    access_token_name = settings.SIMPLE_JWT.get('ACCESS_TOKEN_NAME', 'access_token')
    refresh_token_name = settings.SIMPLE_JWT.get('REFRESH_TOKEN_NAME', 'refresh_token')
    
    # Cookie settings
    cookie_settings = {
        'httponly': True,
        'secure': settings.COOKIE_TOKEN_SECURE,
        'samesite': settings.COOKIE_SAME_SITE,
    }
    
    if settings.COOKIE_DOMAIN:
        cookie_settings['domain'] = settings.COOKIE_DOMAIN
    
    # Set access token cookie (shorter lifespan for security)
    response.set_cookie(
        access_token_name,
        tokens['access'],
        max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
        path='/',
        **cookie_settings
    )
    
    # Set refresh token cookie
    response.set_cookie(
        refresh_token_name,
        tokens['refresh'],
        max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds(),
        path='/',
        **cookie_settings
    )
    
    return response


def clear_cookie_tokens(response):
    """Clear token cookies"""
    access_token_name = settings.SIMPLE_JWT.get('ACCESS_TOKEN_NAME', 'access_token')
    refresh_token_name = settings.SIMPLE_JWT.get('REFRESH_TOKEN_NAME', 'refresh_token')
    
    cookie_settings = {
        'httponly': True,
        'secure': settings.COOKIE_TOKEN_SECURE,
        'samesite': settings.COOKIE_SAME_SITE,
        'path': '/',
    }
    
    if settings.COOKIE_DOMAIN:
        cookie_settings['domain'] = settings.COOKIE_DOMAIN
    
    response.delete_cookie(access_token_name, **cookie_settings)
    response.delete_cookie(refresh_token_name, **cookie_settings)
    
    return response


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
        tokens = get_tokens_for_user(user)
        
        # Create response
        response = Response({
            'success': True,
            'message': 'User registered successfully',
            'user': UserSerializer(user).data,
            'tokens': tokens,
        }, status=status.HTTP_201_CREATED)
        
        # Set cookies
        set_cookie_tokens(response, tokens)
        
        return response


class LoginView(APIView):
    """
    User login endpoint.
    Returns tokens in both JSON and cookies.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.check_password(password):
            return Response({
                'success': False,
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({
                'success': False,
                'error': 'User account is disabled'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get client IP for logging
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Update last login IP
        user.last_login_ip = ip
        user.save(update_fields=['last_login_ip'])
        
        # Generate tokens
        tokens = get_tokens_for_user(user)
        
        response = Response({
            'success': True,
            'message': 'Login successful',
            'user': UserDetailSerializer(user).data,
            'tokens': tokens,
        }, status=status.HTTP_200_OK)
        
        # Set cookies
        set_cookie_tokens(response, tokens)
        
        logger.info(f"User {user.email} logged in from {ip}")
        
        return response


class LogoutView(APIView):
    """
    User logout endpoint.
    Blacklists the refresh token and clears cookies.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Get refresh token from cookie or header
            refresh_token = request.COOKIES.get(
                settings.SIMPLE_JWT.get('REFRESH_TOKEN_NAME', 'refresh_token')
            )
            
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                logger.info(f"User {request.user.email} logged out, token blacklisted")
            
            response = Response({
                'success': True,
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
            
            # Clear cookies
            clear_cookie_tokens(response)
            
            return response
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            response = Response({
                'success': True,
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
            clear_cookie_tokens(response)
            return response


class TokenRefreshCookieView(TokenRefreshView):
    """
    Refresh access token using refresh token from cookie.
    """
    
    def post(self, request, *args, **kwargs):
        # Get refresh token from cookie
        refresh_token = request.COOKIES.get(
            settings.SIMPLE_JWT.get('REFRESH_TOKEN_NAME', 'refresh_token')
        )
        
        if not refresh_token:
            # Try to get from request data
            refresh_token = request.data.get('refresh')
        
        if not refresh_token:
            return Response({
                'success': False,
                'error': 'No refresh token provided'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Create a new request with the refresh token
        request.data._set('refresh', refresh_token)
        
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Update access token cookie
            access_token_name = settings.SIMPLE_JWT.get('ACCESS_TOKEN_NAME', 'access_token')
            cookie_settings = {
                'httponly': True,
                'secure': settings.COOKIE_TOKEN_SECURE,
                'samesite': settings.COOKIE_SAME_SITE,
                'path': '/',
                'max_age': settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds(),
            }
            
            if settings.COOKIE_DOMAIN:
                cookie_settings['domain'] = settings.COOKIE_DOMAIN
            
            response.set_cookie(
                access_token_name,
                response.data['access'],
                **cookie_settings
            )
        
        return response


class CurrentUserView(APIView):
    """
    Get current authenticated user.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({
            'success': True,
            'user': UserDetailSerializer(request.user).data
        })


class ChangePasswordView(APIView):
    """
    Change user password.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        # Verify old password
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({
                'success': False,
                'error': 'Incorrect old password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Set new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        logger.info(f"User {user.email} changed their password")
        
        return Response({
            'success': True,
            'message': 'Password changed successfully'
        })


class UpdateProfileView(generics.UpdateAPIView):
    """
    Update user profile.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateUserSerializer
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'user': UserDetailSerializer(instance).data
        })


class UpdateUserRoleView(APIView):
    """
    Update user role (Admin only).
    """
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        serializer = RoleUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = User.objects.get(id=serializer.validated_data['user_id'])
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        old_role = user.role
        user.role = serializer.validated_data['role']
        user.save()
        
        logger.info(f"Admin {request.user.email} changed role of {user.email} from {old_role} to {user.role}")
        
        return Response({
            'success': True,
            'message': f'Role updated from {old_role} to {user.role}',
            'user': UserSerializer(user).data
        })


class UserListView(generics.ListAPIView):
    """
    List all users (Admin and Manager only).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsManagerOrAdmin]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by role
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Filter by verification status
        is_verified = self.request.query_params.get('is_verified')
        if is_verified:
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')
        
        return queryset


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'
