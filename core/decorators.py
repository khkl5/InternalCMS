from django.http import HttpResponseForbidden

def role_required(allowed_roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("يجب تسجيل الدخول")

            user_profile = getattr(request.user, 'userprofile', None)
            role = getattr(getattr(user_profile, 'role', None), 'name', None)

            if role in allowed_roles:
                return view_func(request, *args, **kwargs)

            return HttpResponseForbidden("ليس لديك صلاحية للوصول لهذه الصفحة")
        return wrapper
    return decorator
