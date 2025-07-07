# core/context_processors.py

def user_role(request):
    role = None
    if request.user.is_authenticated:
        # يفترض أن عندك userprofile مرتبط بالمستخدم
        if hasattr(request.user, 'userprofile'):
            role = request.user.userprofile.role.name
    return {'role': role}
