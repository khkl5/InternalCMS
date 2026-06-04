from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.decorators import role_required
from .models import Client
from .forms import ClientForm
from tasks.models import Task
from tasks.access import attach_task_download_url
from core.decorators import get_user_role

@login_required
@role_required(['admin', 'staff'])
def client_list(request):
    user = request.user
    if get_user_role(user) == 'admin':
        clients = Client.objects.all()
    else:
        clients = Client.objects.filter(assigned_to=user)
    return render(request, 'clients/list.html', {'clients': clients})

@login_required
@role_required(['admin'])
def add_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('client_list')
    else:
        form = ClientForm()
    return render(request, 'clients/add_client.html', {'form': form})
@login_required
@role_required(['admin', 'staff'])
def client_tasks(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    # التحقق من صلاحية الوصول
    role = get_user_role(request.user)
    if role != 'admin' and client.assigned_to != request.user:
        return render(request, '403.html', status=403)

    tasks = list(Task.objects.filter(client=client).select_related('assigned_to').order_by('-created_at'))
    for task in tasks:
        attach_task_download_url(task)
    
    return render(request, 'clients/client_tasks.html', {
        'client': client,
        'tasks': tasks,
        'role': role,
    })
