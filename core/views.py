from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from clients.models import Client
from tasks.models import Task
from content.models import Document
from .models import UserProfile
from core.decorators import role_required
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse



def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    profile = getattr(request.user, 'userprofile', None)
    role = getattr(profile.role, 'name', 'viewer')  # تأكدنا أنه اسم وليس كائن

    total_clients = total_tasks = total_documents = 0
    tasks_pending = tasks_completed = tasks_overdue = 0
    latest_tasks = []

    if role == 'admin':
        total_clients = Client.objects.count()
        total_tasks = Task.objects.count()
        total_documents = Document.objects.count()
        tasks_pending = Task.objects.filter(status='pending').count()
        tasks_completed = Task.objects.filter(status='completed').count()
        tasks_overdue = Task.objects.filter(status='overdue').count()
        latest_tasks = Task.objects.order_by('-created_at')[:5]

    elif role == 'staff':
        user = request.user
        total_tasks = Task.objects.filter(assigned_to=user).count()
        tasks_pending = Task.objects.filter(assigned_to=user, status='pending').count()
        tasks_completed = Task.objects.filter(assigned_to=user, status='completed').count()
        latest_tasks = Task.objects.filter(assigned_to=user).order_by('-created_at')[:3]

    elif role == 'viewer':
        total_documents = Document.objects.filter(uploaded_by=request.user).count()

    context = {
        'role': role,
        'total_clients': total_clients,
        'total_tasks': total_tasks,
        'total_documents': total_documents,
        'tasks_pending': tasks_pending,
        'tasks_completed': tasks_completed,
        'tasks_overdue': tasks_overdue,
        'latest_tasks': latest_tasks,
    }

    return render(request, 'core/dashboard.html', context)


@role_required(['admin'])
def admin_dashboard(request):
    total_users = UserProfile.objects.count()
    total_staff = UserProfile.objects.filter(role__name='staff').count()
    total_tasks = Task.objects.count()
    total_documents = Document.objects.count()
    total_clients = Client.objects.count()

    context = {
        'total_users': total_users,
        'total_staff': total_staff,
        'total_tasks': total_tasks,
        'total_documents': total_documents,
        'total_clients': total_clients,
    }

    return render(request, 'core/admin_dashboard.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')

    return render(request, 'core/login.html')


def profile_view(request):
    return render(request, 'core/profile.html')


def reports_view(request):
    return render(request, 'content/reports.html')



def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def settings_view(request):
    return HttpResponse("صفحة الإعدادات")

@login_required
def user_list_view(request):
    return HttpResponse("قائمة المستخدمين")
@role_required(['admin'])
@login_required
def settings_view(request):
    return HttpResponse("صفحة الإعدادات")
@role_required(['admin', 'staff'])
@login_required
def user_list_view(request):
    return HttpResponse("قائمة المستخدمين")
