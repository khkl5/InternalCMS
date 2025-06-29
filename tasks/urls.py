from django.urls import path
from .views import update_task_status, task_list_view
from .views import add_task_view
from .views import task_list_view, add_task_view, update_task_status

urlpatterns = [
    path('update-status/<int:task_id>/', update_task_status, name='update_task_status'),
    path('', task_list_view, name='task_list'),
    path('add/', add_task_view, name='add_task'),
    path('update-status/<int:task_id>/', update_task_status, name='update_task_status'),


]
