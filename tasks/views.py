from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Task

@csrf_exempt
def update_task_status(request, task_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_status = data.get('status')

        try:
            task = Task.objects.get(pk=task_id)
            task.status = new_status
            task.save()
            return JsonResponse({'success': True})
        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})
