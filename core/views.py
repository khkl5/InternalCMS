from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Count

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from core.models import UserProfile
from core.forms import StaffEditForm
from core.models import UserProfile
from core.decorators import role_required
from clients.models import Client
from tasks.models import Task
from content.models import Document
from core.forms import AddStaffForm
from clients.models import Client
from tasks.models import Task
from content.models import Document
from django.shortcuts import render, redirect
from django.contrib.auth.models import User


@login_required
def dashboard_view(request):
    try:
        profile = request.user.userprofile
        role = getattr(profile.role, 'name', 'viewer')
    except UserProfile.DoesNotExist:
        role = 'viewer'

    context = {
        'role': role,
        'total_clients': 0,
        'total_tasks': 0,
        'total_documents': 0,
        'tasks_pending': 0,
        'tasks_completed': 0,
        'tasks_overdue': 0,
        'latest_tasks': [],
    }

    if role == 'admin':
        context.update({
            'total_clients': Client.objects.count(),
            'total_tasks': Task.objects.count(),
            'total_documents': Document.objects.count(),
            'tasks_pending': Task.objects.filter(status='pending').count(),
            'tasks_completed': Task.objects.filter(status='completed').count(),
            'tasks_overdue': Task.objects.filter(status='overdue').count(),
            'latest_tasks': Task.objects.select_related('assigned_to').order_by('-created_at')[:5],
        })

    elif role == 'staff':
        user = request.user
        assigned_tasks = Task.objects.filter(assigned_to=user)
        context.update({
            'total_tasks': assigned_tasks.count(),
            'tasks_pending': assigned_tasks.filter(status='pending').count(),
            'tasks_completed': assigned_tasks.filter(status='completed').count(),
            'latest_tasks': assigned_tasks.order_by('-created_at')[:3],
        })

    elif role == 'viewer':
        context['total_documents'] = Document.objects.filter(uploaded_by=request.user).count()

    template_map = {
        'admin': 'core/admin_dashboard.html',
        'staff': 'core/staff_dashboard.html',
        'viewer': 'core/viewer_dashboard.html',
    }
    template = template_map.get(role, 'core/admin_dashboard.html')
    return render(request, template, context)


@role_required(['admin'])
@login_required
def admin_dashboard(request):
    context = {
        'total_users': UserProfile.objects.count(),
        'total_staff': UserProfile.objects.filter(role__name='staff').count(),
        'total_tasks': Task.objects.count(),
        'total_documents': Document.objects.count(),
        'total_clients': Client.objects.count(),
    }
    return render(request, 'core/admin_dashboard.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            logout(request)  # إنهاء الجلسة السابقة بشكل آمن بدون حذف CSRF token
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')

    return render(request, 'core/login.html')


@login_required
def profile_view(request):
    return render(request, 'core/profile.html')




@login_required
def reports_view(request):
    user = request.user
    role = getattr(user.userprofile.role, 'name', None)

    context = {
        'role': role,  # نستخدمه داخل القالب للتحكم في العرض
        'total_clients': 0,
        'total_tasks': 0,
        'tasks_completed': 0,
        'total_documents': 0,
    }

    if role == 'admin':
        context.update({
            'total_clients': Client.objects.count(),
            'total_tasks': Task.objects.count(),
            'tasks_completed': Task.objects.filter(status='completed').count(),
            'total_documents': Document.objects.count(),
        })

    elif role == 'staff':
        context.update({
            'total_clients': Client.objects.filter(assigned_to=user).count(),
            'total_tasks': Task.objects.filter(assigned_to=user).count(),
            'tasks_completed': Task.objects.filter(assigned_to=user, status='completed').count(),
            'total_documents': Document.objects.filter(uploaded_by=user).count(),
        })

    elif role == 'viewer':
        context.update({
            'total_tasks': Task.objects.filter(access_level__in=['public', 'restricted']).count(),
            'tasks_completed': Task.objects.filter(status='completed', access_level__in=['public', 'restricted']).count(),
            'total_documents': Document.objects.filter(access_level='public').count(),
        })

    return render(request, 'content/reports.html', context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@role_required(['admin'])
@login_required
def settings_view(request):
    return HttpResponse("صفحة الإعدادات")


@role_required(['admin', 'staff'])
@login_required
def user_list_view(request):
    return HttpResponse("قائمة المستخدمين")
@role_required(['staff'])
@login_required
def staff_dashboard(request):
    return render(request, 'core/staff_dashboard.html')

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'تم تسجيل الخروج بنجاح. الرجاء تسجيل الدخول من جديد.')
    return redirect('login')

@role_required(['admin'])
@login_required
def add_staff_view(request):
    if request.method == 'POST':
        form = AddStaffForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم إضافة الموظف بنجاح.')
            return redirect('add_staff')
    else:
        form = AddStaffForm()

    return render(request, 'core/add_staff.html', {'form': form})
@login_required
@role_required(['admin'])
def staff_list_view(request):
    staff_list = User.objects.exclude(is_superuser=True)
    return render(request, 'core/staff_list.html', {'staff_list': staff_list})
@login_required
@role_required(['admin'])
def delete_staff_view(request, staff_id):
    user = get_object_or_404(User, id=staff_id)
    if user.is_superuser:
        messages.error(request, "لا يمكن حذف المدير الخارق.")
    else:
        user.delete()
        messages.success(request, "تم حذف الموظف بنجاح.")
    return redirect('staff_list')
from .forms import StaffEditForm

@login_required
@role_required(['admin'])
def edit_staff_view(request, staff_id):
    user = get_object_or_404(User, id=staff_id)
    if request.method == "POST":
        form = StaffEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث بيانات الموظف بنجاح.")
            return redirect('staff_list')
    else:
        form = StaffEditForm(instance=user)
    return render(request, 'core/edit_staff.html', {'form': form, 'user_obj': user})
# core/views.py


def edit_staff_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(UserProfile, user=user)
    if request.method == "POST":
        form = StaffEditForm(request.POST, user_instance=user, profile_instance=profile)
        if form.is_valid():
            form.save(user, profile)
            messages.success(request, "تم تعديل بيانات الموظف بنجاح")
            return redirect('staff_list')
        else:
            messages.error(request, "حدث خطأ أثناء تعديل بيانات الموظف.")
    else:
        form = StaffEditForm(user_instance=user, profile_instance=profile)
    return render(request, 'core/edit_staff.html', {'form': form, 'user_obj': user})
from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings

def send_test_email(request):
    send_mail(
        subject='تجربة إرسال إيميل من Django',
        message='تم إرسال هذا البريد بنجاح عبر SendGrid! 🚀',
        recipient_list=['khklooookh@gmail.com'],  # الإيميل الذي تريدين استقباله
        from_email=settings.DEFAULT_FROM_EMAIL,    # تأكدي أنه مطابق للإيميل الموثق
        fail_silently=False,
    )
    return HttpResponse("تم إرسال الإيميل! تحقق من بريدك 🚀")

