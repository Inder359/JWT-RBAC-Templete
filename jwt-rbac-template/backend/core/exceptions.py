"""
Custom Exception Handler for DRF
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns standardized error responses.
    """
    # Handle Django validation errors
    if isinstance(exc, ValidationError):
        return Response(
            {
                'success': False,
                'error': 'Validation Error',
                'detail': exc.message_dict if hasattr(exc, 'message_dict') else str(exc),
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Call REST framework's default exception handler
    response = exception_handler(exc, context)
    
    if response is not None:
        # Transform error response to consistent format
        error_data = {
            'success': False,
            'error': get_error_title(response.status_code),
            'detail': response.data,
        }
        
        # Add non-field errors to top level
        if 'non_field_errors' in response.data:
            error_data['detail'] = response.data['non_field_errors']
        elif 'detail' in response.data:
            error_data['detail'] = response.data['detail']
        
        response.data = error_data
        
        # Log error
        logger.error(
            f"API Error: {response.status_code} - {error_data['error']} - {error_data['detail']}"
        )
    
    else:
        # Handle unexpected exceptions
        logger.exception(f"Unhandled exception: {exc}")
        response = Response(
            {
                'success': False,
                'error': 'Internal Server Error',
                'detail': 'An unexpected error occurred. Please try again later.',
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return response


def get_error_title(status_code):
    """Get error title based on status code"""
    titles = {
        400: 'Bad Request',
        401: 'Unauthorized',
        403: 'Forbidden',
        404: 'Not Found',
        405: 'Method Not Allowed',
        409: 'Conflict',
        422: 'Unprocessable Entity',
        429: 'Too Many Requests',
        500: 'Internal Server Error',
        503: 'Service Unavailable',
    }
    return titles.get(status_code, 'Error')
