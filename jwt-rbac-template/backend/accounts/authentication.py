"""
JWT Authentication with Cookie Support
"""

import jwt
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from rest_framework.request import Request


class CookieJWTAuthentication(JWTAuthentication):
    """
    JWT Authentication that supports both header and cookie-based tokens.
    This enables HttpOnly cookie storage for better security.
    """
    
    def authenticate(self, request: Request):
        """
        Authenticate the request and return a tuple of (user, token).
        Checks for token in Authorization header first, then falls back to cookie.
        """
        # Get token from header (for API clients)
        header_token = self.get_header(request)
        if header_token:
            return self.authenticate_header(request, header_token)
        
        # Get token from cookie (for browser clients)
        cookie_token = request.COOKIES.get(settings.SIMPLE_JWT.get('REFRESH_TOKEN_NAME', 'refresh_token'))
        
        if not cookie_token:
            # Also check for access token in cookie (for initial load)
            cookie_token = request.COOKIES.get(settings.SIMPLE_JWT.get('ACCESS_TOKEN_NAME', 'access_token'))
        
        if not cookie_token:
            return None
        
        # Validate the token
        try:
            validated_token = self.get_validated_token(cookie_token)
        except InvalidToken as e:
            # Try to get user from the invalid token for more specific error
            return None
        
        return (self.get_user(validated_token), validated_token)
    
    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token.get('user_id')
            if not user_id:
                raise InvalidToken('Token contained no recognizable user identification')
            
            # Import here to avoid circular imports
            from core.models import User
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')
        except Exception as e:
            raise InvalidToken(str(e))
        
        if not user.is_active:
            raise AuthenticationFailed('User is inactive')
        
        return user
    
    def authenticate_header(self, request: Request):
        """
        Return a string to be used as the value of the WWW-Authenticate
        header in a 401 response, or None if not authenticated.
        """
        return 'Bearer'
