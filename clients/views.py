from django.shortcuts import render
from .models import Client
from tasks.models import Task
from content.models import Document  # ✅ تم التعديل هنا

def reports_view(request):
    total_clients = Client.objects.count()
    total_tasks = Task.objects.count()
    tasks_completed = Task.objects.filter(status='completed').count()
    total_documents = Document.objects.count()

    context = {
        'total_clients': total_clients,
        'total_tasks': total_tasks,
        'tasks_completed': tasks_completed,
        'total_documents': total_documents,
    }

    return render(request, 'content/reports.html', context)

def client_list(request):
    clients = Client.objects.all()
    return render(request, 'clients/list.html', {'clients': clients})
