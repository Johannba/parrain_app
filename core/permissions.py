from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def is_superadmin(user):
    return getattr(user, "is_authenticated", False) and user.role == "SUPERADMIN"

def superadmin_required(view_func):
    decorated = user_passes_test(is_superadmin, login_url="accounts:login")(view_func)
    return decorated

class SuperadminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not is_superadmin(request.user):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
