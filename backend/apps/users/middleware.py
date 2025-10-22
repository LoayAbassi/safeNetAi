from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from .models import User

class UserLanguageMiddleware(MiddlewareMixin):
    """
    Middleware to activate user's preferred language based on their profile
    """
    
    def process_request(self, request):
        # Get user from request
        user = getattr(request, 'user', None)
        
        # If user is authenticated, activate their preferred language
        if user and user.is_authenticated:
            # Get user's preferred language
            user_language = getattr(user, 'language', 'en')
            
            # Activate the language
            translation.activate(user_language)
            
            # Also set the language in the request for templates
            request.LANGUAGE_CODE = user_language
        else:
            # For anonymous users, use the default language
            translation.activate('en')
            request.LANGUAGE_CODE = 'en'