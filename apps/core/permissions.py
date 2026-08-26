from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class IsFacultyMixin(UserPassesTestMixin):
    """Mixin to check if user is faculty."""
    
    def test_func(self):
        return self.request.user.is_authenticated and hasattr(self.request.user, 'employee_id')


class IsAdminMixin(UserPassesTestMixin):
    """Mixin to check if user is admin."""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin


class IsOwnerOrAdminMixin(UserPassesTestMixin):
    """Mixin to check if user is owner or admin."""
    
    def test_func(self):
        if self.request.user.is_admin:
            return True
        return self.get_object().faculty_id == self.request.user.id


def faculty_required(view_func):
    """Decorator to require faculty role."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not hasattr(request.user, 'employee_id'):
            raise PermissionDenied("Faculty access required.")
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Decorator to require admin role."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin:
            raise PermissionDenied("Admin access required.")
        return view_func(request, *args, **kwargs)
    return wrapper
