import uuid
import json
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.decorators import role_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import TaskForm
from .models import Task
from core.decorators import role_required
from core.supabase_utils import upload_to_supabase
from .models import Task
from .forms import TaskForm

# ✅ عرض قائمة المهام
@login_required
@role_required(['admin', 'staff'])
def task_list_view(request):
    user = request.user
    if user.userprofile.role.name == 'admin':
        all_tasks = Task.objects.order_by('-created_at')
    else:
        all_tasks = Task.objects.filter(assigned_to=user).order_by('-created_at')

    return render(request, 'tasks/list.html', {'all_tasks': all_tasks})


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
# ✅ تحديث حالة المهمة
@require_POST
@login_required
@role_required(['admin', 'staff'])
def update_task_status(request, task_id):
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        valid_statuses = ['pending', 'completed', 'overdue']

        if new_status not in valid_statuses:
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
