from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from core.decorators import role_required
from core.supabase_utils import upload_to_supabase
from clients.models import Client
from .forms import TaskForm
from .models import Task
from content.models import Document
from django.contrib.auth.decorators import login_required
from core.decorators import role_required

import json


# ✅ عرض قائمة المهام
@login_required
@role_required(['admin', 'staff'])
def task_list_view(request):
    user = request.user
    role = user.userprofile.role.name

    if role == 'admin':
        tasks = Task.objects.all()  # لا حاجة لـ order_by بسبب ordering في الموديل
    else:
        tasks = Task.objects.filter(assigned_to=user)

    return render(request, 'tasks/list.html', {'all_tasks': tasks})


# ✅ عرض تفاصيل مهمة
@login_required
def task_detail_view(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'tasks/detail.html', {'task': task})


# ✅ إضافة مهمة (للمدير فقط)
@login_required
@role_required(['admin'])
def add_task_view(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)

            uploaded_file = request.FILES.get('file')
            if uploaded_file:
                try:
                    public_url, file_path = upload_to_supabase(uploaded_file, uploaded_file.name)
                    task.file_url = public_url
                    task.file_path = file_path
                except Exception as e:
                    messages.error(request, f"فشل رفع الملف: {e}")
                    return render(request, 'tasks/add_task.html', {'form': form})

            task.save()
            form.save_m2m()
            messages.success(request, "تم إنشاء المهمة بنجاح.")
            return redirect('task_list')
    else:
        form = TaskForm()

    return render(request, 'tasks/add_task.html', {'form': form})


# ✅ إضافة مهمة مرتبطة بعميل (للمدير فقط)
@login_required
@role_required(['admin'])
def add_task_for_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.client = client

            uploaded_file = request.FILES.get('file')
            if uploaded_file:
                try:
                    public_url, file_path = upload_to_supabase(uploaded_file, uploaded_file.name)
                    task.file_url = public_url
                    task.file_path = file_path
                except Exception as e:
                    messages.error(request, f"فشل رفع الملف: {e}")
                    return render(request, 'tasks/add_task.html', {'form': form, 'client': client})

            task.save()
            form.save_m2m()
            messages.success(request, 'تمت إضافة المهمة لهذا العميل بنجاح.')
            return redirect('client_tasks', client_id=client.id)
    else:
        form = TaskForm()

    return render(request, 'tasks/add_task.html', {'form': form, 'client': client})


# ✅ تحديث حالة المهمة (مدير أو صاحب المهمة فقط)
@require_POST
@login_required
@role_required(['admin', 'staff'])
def update_task_status(request, task_id):
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        if new_status not in ['pending', 'completed', 'overdue']:
            return JsonResponse({'success': False, 'error': 'الحالة غير صالحة'})

        task = get_object_or_404(Task, pk=task_id)

        if request.user != task.assigned_to and request.user.userprofile.role.name != 'admin':
            return JsonResponse({'success': False, 'error': 'غير مصرح لك بتعديل هذه المهمة'})

        task.status = new_status
        task.save()
        return JsonResponse({'success': True})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'تنسيق البيانات غير صالح'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ✅ حذف مهمة (مدير فقط)
@require_POST
@login_required
@role_required(['admin'])
def delete_task_view(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        task.delete()
        return JsonResponse({'success': True})
    except Task.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'المهمة غير موجودة'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ✅ لوحة تحكم المدير
@login_required
@role_required(['admin'])
def admin_dashboard_view(request):
    total_tasks = Task.objects.count()
    tasks_completed = Task.objects.filter(status='completed').count()
    total_documents = Document.objects.count()
    total_clients = Client.objects.count()
    latest_tasks = Task.objects.all()[:5]  # ترتيب تلقائي من الموديل

    context = {
        'total_tasks': total_tasks,
        'tasks_completed': tasks_completed,
        'total_documents': total_documents,
        'total_clients': total_clients,
        'latest_tasks': latest_tasks,
        'role': request.user.userprofile.role.name,
    }

    return render(request, 'core/admin_dashboard.html', context)

@login_required
@role_required(['staff'])
def staff_dashboard_view(request):
    user = request.user
    role = user.userprofile.role.name

    tasks = Task.objects.filter(assigned_to=user)
    total_tasks = tasks.count()
    tasks_completed = tasks.filter(status='completed').count()
    tasks_pending = tasks.exclude(status='completed').count()

    total_documents = Document.objects.filter(uploaded_by=user).count()
    total_clients = Client.objects.filter(assigned_to=user).count()

    latest_tasks = tasks.order_by('-created_at')[:3]

    return render(request, 'core/staff_dashboard.html', {
        'role': role,
        'total_tasks': total_tasks,
        'tasks_completed': tasks_completed,
        'tasks_pending': tasks_pending,
        'total_documents': total_documents,
        'total_clients': total_clients,
        'latest_tasks': latest_tasks,
    })
