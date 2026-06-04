from functools import wraps

from django.http import HttpResponseForbidden
from django.shortcuts import redirect


def get_user_role(user):
    if not getattr(user, "is_authenticated", False):
        return None
    if user.is_superuser:
        return "admin"

    profile = getattr(user, "userprofile", None)
    role = getattr(profile, "role", None)
    return getattr(role, "name", None)


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")

            if get_user_role(request.user) in allowed_roles:
                return view_func(request, *args, **kwargs)

            return HttpResponseForbidden("ليس لديك صلاحية للوصول إلى هذه الصفحة.")

        return wrapper

    return decorator
