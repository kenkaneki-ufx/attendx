from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout
from django.utils import timezone
from datetime import timedelta


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware to log user actions for audit purposes.
    """
    
    def process_request(self, request):
        # Add audit info to request
        request.audit_ip = self.get_client_ip(request)
        request.audit_user_agent = request.META.get('HTTP_USER_AGENT', '')
        return None
    
    def process_response(self, request, response):
        # Log response if needed
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SessionTrackingMiddleware(MiddlewareMixin):
    """
    Middleware to track user sessions and enforce session limits.
    """
    
    def process_request(self, request):
        if request.user.is_authenticated:
            # Update last activity timestamp
            request.session['last_activity'] = timezone.now().isoformat()
            
            # Check for session expiry
            last_activity = request.session.get('last_activity')
            if last_activity:
                last_activity_time = timezone.datetime.fromisoformat(last_activity)
                if timezone.now() - last_activity_time > timedelta(hours=24):
                    logout(request)
                    return None
        
        return None
