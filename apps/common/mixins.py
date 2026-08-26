from django.http import HttpResponseRedirect, Http404
from django.urls import reverse


class AdminRequiredMixin:
    """Mixin to ensure only admin users can access the view.
    Redirects unauthenticated users to login, raises 404 for non-admin users.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(f"{reverse('accounts:login')}?next={request.path}")
        if not request.user.is_admin:
            raise Http404
        return super().dispatch(request, *args, **kwargs)
