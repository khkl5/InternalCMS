from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.decorators import role_required
from .models import Client
from tasks.models import Task
from content.models import Document



@login_required
@role_required(['admin', 'staff'])
def client_list(request):
    user = request.user
    if user.userprofile.role.name == 'admin':
        clients = Client.objects.all()
    else:
        clients = Client.objects.filter(assigned_to=user)
    return render(request, 'clients/list.html', {'clients': clients})
