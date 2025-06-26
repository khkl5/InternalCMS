from django.shortcuts import render, redirect
from clients.models import Client
from tasks.models import Task
from content.models import Document
from .models import UserProfile  # تأكدي أن المسار صحيح

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render


def dashboard_view(request):
    # التحقق من تسجيل الدخول
    if not request.user.is_authenticated:
        return redirect('login')

    # الحصول على الدور من UserProfile
    profile = getattr(request.user, 'userprofile', None)
    role = profile.role if profile else 'viewer'

    # تهيئة القيم الافتراضية
    total_clients = total_tasks = total_documents = 0
    tasks_pending = tasks_completed = tasks_overdue = 0
    latest_tasks = []

    # تخصيص البيانات حسب الدور
    if role == 'admin':
        total_clients = Client.objects.count()
        total_tasks = Task.objects.count()
        total_documents = Document.objects.count()
        tasks_pending = Task.objects.filter(status='pending').count()
        tasks_completed = Task.objects.filter(status='completed').count()
        tasks_overdue = Task.objects.filter(status='overdue').count()
        latest_tasks = Task.objects.order_by('-created_at')[:5]

    elif role == 'staff':
        total_tasks = Task.objects.count()
        tasks_pending = Task.objects.filter(status='pending').count()
        tasks_completed = Task.objects.filter(status='completed').count()
        latest_tasks = Task.objects.order_by('-created_at')[:3]

    elif role == 'viewer':
        total_documents = Document.objects.count()

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

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # يرجع المستخدم للوحة التحكم
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')

    return render(request, 'core/login.html')

# عرض صفحة تسجيل الدخول
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'core/login.html', {'error': 'بيانات الدخول غير صحيحة'})

    return render(request, 'core/login.html')

# عرض صفحة الملف الشخصي (مؤقتًا فقط صفحة فارغة)
def profile_view(request):
    return render(request, 'core/profile.html')


def reports_view(request):
    return render(request, 'content/reports.html')
