from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.decorators import role_required
from .models import Client
from .forms import ClientForm
from tasks.models import Task

@login_required
@role_required(['admin', 'staff'])
def client_list(request):
    user = request.user
    if user.userprofile.role.name == 'admin':
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
    if request.user.userprofile.role.name != 'admin' and client.assigned_to != request.user:
        return render(request, '403.html')

    tasks = Task.objects.filter(client=client).order_by('-created_at')
    
    return render(request, 'clients/client_tasks.html', {
        'client': client,
        'tasks': tasks
    })
