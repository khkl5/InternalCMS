from django.urls import path
from . import views

urlpatterns = [
    path('', views.client_list, name='client_list'),
    path('list/', views.client_list, name='client_list'),
    path('add/', views.add_client, name='add_client'),  # ⬅️ مسار إضافة عميل
    path('<int:client_id>/tasks/', views.client_tasks, name='client_tasks'),
    path('client/<int:client_id>/tasks/', views.client_tasks, name='client_tasks'),

]
