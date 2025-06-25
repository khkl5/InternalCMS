from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Task
import json

# ✅ عرض قائمة المهام
@login_required
def task_list_view(request):
    all_tasks = Task.objects.order_by('-created_at')
    return render(request, 'tasks/list.html', {'all_tasks': all_tasks})


# ✅ تحديث حالة المهمة بشكل آمن
@require_POST
@login_required
def update_task_status(request, task_id):
    try:
        # قراءة البيانات المرسلة
        data = json.loads(request.body)
        new_status = data.get('status')

        # التحقق من صحة الحالة الجديدة
        valid_statuses = ['pending', 'completed', 'overdue']
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'error': 'الحالة غير صالحة'})

        # جلب المهمة والتحقق من وجودها
        task = get_object_or_404(Task, pk=task_id)

        # تحقق من الصلاحيات: المدير أو من تم تعيين المهمة له
        if request.user != task.assigned_to and not request.user.is_superuser:
            return JsonResponse({'success': False, 'error': 'غير مصرح لك بتعديل هذه المهمة'})

        # تحديث الحالة وحفظ
        task.status = new_status
        task.save()

        return JsonResponse({'success': True})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'تنسيق البيانات غير صالح'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
