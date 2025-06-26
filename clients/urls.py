from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.client_list, name='client_list'),
]
