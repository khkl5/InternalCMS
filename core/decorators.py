from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from functools import wraps

def role_required(allowed_roles):
    """
    ديكوريتر لتقييد الوصول لواجهات معينة حسب الدور.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')  # أو استخدمي HttpResponseForbidden إذا كنتِ تفضلين ذلك

            user_profile = getattr(request.user, 'userprofile', None)
            role = getattr(getattr(user_profile, 'role', None), 'name', None)

            if role in allowed_roles:
                return view_func(request, *args, **kwargs)

            return HttpResponseForbidden("⚠️ ليس لديك صلاحية للوصول إلى هذه الصفحة.")
        return wrapper
    return decorator
