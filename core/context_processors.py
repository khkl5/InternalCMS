from core.decorators import get_user_role
from tasks.models import Task


def user_role(request):
    role = get_user_role(request.user)
    notification_count = 0
    department = ""

    if getattr(request.user, "is_authenticated", False):
        if role == "admin":
            notification_count = Task.objects.exclude(status="completed").count()
        elif role == "staff":
            notification_count = Task.objects.filter(
                assigned_to=request.user,
                status__in=["pending", "overdue"],
            ).count()

        profile = getattr(request.user, "userprofile", None)
        department = getattr(profile, "department", "")

    return {
        "role": role,
        "notification_count": notification_count,
        "profile_department": department,
    }
