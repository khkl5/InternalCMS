from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.decorators import role_required
from .models import Client
from tasks.models import Task
from content.models import Document

@login_required
@role_required(['admin', 'staff'])
def reports_view(request):
    user = request.user
    role = user.userprofile.role.name

    if role == 'admin':
        total_clients = Client.objects.count()
        total_tasks = Task.objects.count()
        tasks_completed = Task.objects.filter(status='completed').count()
        total_documents = Document.objects.count()
    else:
        total_clients = Client.objects.filter(assigned_to=user).count()
        total_tasks = Task.objects.filter(assigned_to=user).count()
        tasks_completed = Task.objects.filter(assigned_to=user, status='completed').count()
        total_documents = Document.objects.filter(uploaded_by=user).count()

    context = {
        'total_clients': total_clients,
        'total_tasks': total_tasks,
        'tasks_completed': tasks_completed,
        'total_documents': total_documents,
    }

    return render(request, 'content/reports.html', context)


@login_required
@role_required(['admin', 'staff'])
def client_list(request):
    user = request.user
    if user.userprofile.role.name == 'admin':
        clients = Client.objects.all()
    else:
        clients = Client.objects.filter(assigned_to=user)
    return render(request, 'clients/list.html', {'clients': clients})
