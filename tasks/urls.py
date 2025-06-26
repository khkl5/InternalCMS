from django.urls import path
from .views import update_task_status, task_list_view

urlpatterns = [
    path('update-status/<int:task_id>/', update_task_status, name='update_task_status'),
    path('', task_list_view, name='task_list'),

]
