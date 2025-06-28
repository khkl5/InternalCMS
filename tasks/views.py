from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from core.decorators import role_required
from .models import Task
import json

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


# ✅ تحديث حالة المهمة بشكل آمن
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

        # التحقق من الصلاحيات
        if request.user != task.assigned_to and request.user.userprofile.role.name != 'admin':
            return JsonResponse({'success': False, 'error': 'غير مصرح لك بتعديل هذه المهمة'})

        task.status = new_status
        task.save()
        return JsonResponse({'success': True})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'تنسيق البيانات غير صالح'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
