from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from django.core.cache import cache
from django.db import IntegrityError
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.utils.crypto import salted_hmac
from django.utils import timezone

from clients.models import Client
from content.models import Document
from content.permissions import visible_documents_for
from core.decorators import get_user_role, role_required
from core.forms import AddUserForm, StaffEditForm
from core.models import UserProfile
from core.role import Role
from tasks.models import Task


def _login_attempt_key(request, username):
    source = f"{request.META.get('REMOTE_ADDR', 'unknown')}:{username.lower()}"
    return f"login-attempts:{salted_hmac('login-attempts', source).hexdigest()}"


def _dashboard_document_type(document):
    filename = (document.file_path or document.title).lower()
    extension = filename.rsplit(".", 1)[-1] if "." in filename else ""
    if extension in {"xls", "xlsx", "csv"}:
        return "spreadsheet"
    if extension in {"ppt", "pptx"}:
        return "presentation"
    if extension == "pdf":
        return "pdf"
    if extension in {"doc", "docx", "txt"}:
        return "document"
    return "generic"


def _dashboard_context(user):
    role = get_user_role(user) or "viewer"
    documents = visible_documents_for(user)

    if role == "admin":
        tasks = Task.objects.all()
        total_clients = Client.objects.count()
        total_users = UserProfile.objects.count()
    elif role == "staff":
        tasks = Task.objects.filter(assigned_to=user)
        total_clients = Client.objects.filter(assigned_to=user).count()
        total_users = 0
    else:
        tasks = Task.objects.none()
        total_clients = 0
        total_users = 0

    latest_documents = list(
        documents.select_related("uploaded_by", "client").order_by("-created_at")[:5]
    )
    for document in latest_documents:
        document.dashboard_file_type = _dashboard_document_type(document)

    return {
        "role": role,
        "today": timezone.localdate(),
        "total_clients": total_clients,
        "total_users": total_users,
        "total_tasks": tasks.count(),
        "total_documents": documents.count(),
        "shared_documents": documents.filter(
            access_level__in=["public", "restricted", "client_shared"]
        ).count(),
        "tasks_pending": tasks.filter(status="pending").count(),
        "tasks_completed": tasks.filter(status="completed").count(),
        "tasks_overdue": tasks.filter(status="overdue").count(),
        "latest_tasks": tasks.select_related("assigned_to", "client").order_by(
            "-created_at"
        )[:5],
        "latest_documents": latest_documents,
    }


@login_required
def dashboard_view(request):
    return render(request, "core/dashboard.html", _dashboard_context(request.user))


@role_required(["admin"])
def admin_dashboard(request):
    return render(request, "core/dashboard.html", _dashboard_context(request.user))


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        role_name = request.POST.get("role", "")
        
        # تحديد المستخدم بناءً على الدور
        role_map = {
            "admin": "admin_user",
            "staff": "staff_user",
        }
        
        username = role_map.get(role_name)
        if not username:
            messages.error(request, "دور غير صحيح.")
            return render(request, "core/login.html")
        
        # البحث عن أو إنشاء المستخدم
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "first_name": "مستخدم",
                "last_name": role_name.capitalize(),
                "is_active": True,
            }
        )
        
        # إنشاء أو تحديث ملف المستخدم مع الدور
        try:
            role = Role.objects.get(name=role_name)
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={"role": role}
            )
            if profile.role != role:
                profile.role = role
                profile.save()
        except Role.DoesNotExist:
            messages.error(request, "الدور غير موجود في النظام.")
            return render(request, "core/login.html")
        
        # تسجيل الدخول مباشرة
        login(request, user)
        return redirect("dashboard")

    # جلب الأدوار المتاحة
    roles = Role.objects.all()
    return render(request, "core/login.html", {"roles": roles})


@login_required
def profile_view(request):
    profile = getattr(request.user, "userprofile", None)
    return render(
        request,
        "core/profile.html",
        {
            "phone": getattr(profile, "phone_number", ""),
            "department": getattr(profile, "department", ""),
        },
    )


@login_required
def reports_view(request):
    role = get_user_role(request.user)
    context = {
        "role": role,
        "total_clients": 0,
        "total_tasks": 0,
        "tasks_completed": 0,
        "total_documents": 0,
    }

    if role == "admin":
        context.update(
            {
                "total_clients": Client.objects.count(),
                "total_tasks": Task.objects.count(),
                "tasks_completed": Task.objects.filter(status="completed").count(),
                "total_documents": Document.objects.count(),
            }
        )
    elif role == "staff":
        context.update(
            {
                "total_clients": Client.objects.filter(assigned_to=request.user).count(),
                "total_tasks": Task.objects.filter(assigned_to=request.user).count(),
                "tasks_completed": Task.objects.filter(
                    assigned_to=request.user, status="completed"
                ).count(),
                "total_documents": Document.objects.filter(uploaded_by=request.user).count(),
            }
        )
    else:
        context["total_documents"] = Document.objects.filter(access_level="public").count()

    return render(request, "content/reports.html", context)


@require_POST
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "تم تسجيل الخروج بنجاح.")
    return redirect("login")


@role_required(["admin"])
def settings_view(request):
    return render(request, "core/settings.html")


@role_required(["admin"])
def user_list_view(request):
    staff_list = (
        User.objects.exclude(is_superuser=True)
        .filter(userprofile__isnull=False)
        .select_related("userprofile__role")
    )
    return render(request, "core/staff_list.html", {"staff_list": staff_list})


@role_required(["staff"])
def staff_dashboard(request):
    return redirect("dashboard")


@role_required(["admin"])
def staff_list_view(request):
    staff_list = (
        User.objects.exclude(is_superuser=True)
        .filter(userprofile__isnull=False)
        .select_related("userprofile__role")
    )
    return render(request, "core/staff_list.html", {"staff_list": staff_list})


@require_POST
@role_required(["admin"])
def delete_staff_view(request, staff_id):
    user = get_object_or_404(User, id=staff_id)
    if user.is_superuser:
        return HttpResponseForbidden("لا يمكن حذف المدير الخارق.")
    if user == request.user:
        return HttpResponseForbidden("لا يمكنك حذف حسابك أثناء استخدامه.")

    user.delete()
    messages.success(request, "تم حذف المستخدم بنجاح.")
    return redirect("staff_list")


@role_required(["admin"])
def edit_staff_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_superuser:
        return HttpResponseForbidden("لا يمكن تعديل المدير الخارق من هذه الصفحة.")

    profile = get_object_or_404(UserProfile, user=user)
    form = StaffEditForm(
        request.POST or None,
        user_instance=user,
        profile_instance=profile,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "تم تعديل بيانات المستخدم بنجاح.")
        return redirect("staff_list")

    return render(request, "core/edit_staff.html", {"form": form, "user_obj": user})


@role_required(["admin"])
def add_user_view(request):
    form = AddUserForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            profile = form.save()
        except IntegrityError:
            messages.error(request, "فشل إنشاء المستخدم بسبب بيانات مكررة.")
        else:
            messages.success(
                request,
                f"تمت إضافة المستخدم {profile.user.get_full_name()} بنجاح.",
            )
            return redirect("add_user")

    return render(request, "core/add_user.html", {"form": form})
