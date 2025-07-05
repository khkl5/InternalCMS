from django.urls import path
from . import views
from .views import task_detail_view


urlpatterns = [
    path('', views.task_list_view, name='task_list'),
    path('add/', views.add_task_view, name='add_task'),
    path('update-status/<int:task_id>/', views.update_task_status, name='update_task_status'),
    path('delete/<int:task_id>/', views.delete_task_view, name='delete_task'),
    path('add/client/<int:client_id>/', views.add_task_for_client, name='add_task_for_client'),
    path('tasks/<int:task_id>/', task_detail_view, name='task_detail'),
    path('staff-dashboard/', views.staff_dashboard_view, name='staff_dashboard'),

    

]
