from django.shortcuts import render
from clients.models import Client
from tasks.models import Task
from content.models import Document

def dashboard_view(request):
    # بيانات الكروت
    total_clients = Client.objects.count()
    total_tasks = Task.objects.count()
    total_documents = Document.objects.count()

    # إحصائيات المهام
    tasks_pending = Task.objects.filter(status='pending').count()
    tasks_completed = Task.objects.filter(status='completed').count()
    tasks_overdue = Task.objects.filter(status='overdue').count()

    # جدول: أحدث 5 مهام
    latest_tasks = Task.objects.order_by('-created_at')[:5]

    context = {
        'total_clients': total_clients,
        'total_tasks': total_tasks,
        'total_documents': total_documents,
        'tasks_pending': tasks_pending,
        'tasks_completed': tasks_completed,
        'tasks_overdue': tasks_overdue,
        'latest_tasks': latest_tasks,
    }

    return render(request, 'core/dashboard.html', context)

# باقي الصفحات تبقى كما هي
def login_view(request):
    return render(request, 'core/login.html')

def profile_view(request):
    return render(request, 'core/profile.html')

def reports_view(request):
    return render(request, 'core/reports.html')
