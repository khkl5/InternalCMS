from django.urls import path
from . import views
from .views import dashboard_view


urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-dashboard/', dashboard_view, name='admin_dashboard'),

    # لوحات التحكم
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    

    # صفحات عامة
    path('profile/', views.profile_view, name='profile'),
    path('reports/', views.reports_view, name='reports'),
    path('settings/', views.settings_view, name='settings'),
    path('users/', views.user_list_view, name='users'),
    path('add-staff/', views.add_staff_view, name='add_staff'),
]
