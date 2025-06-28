from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('reports/', views.reports_view, name='reports'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),  # ⬅️ تمت إضافته
]
