from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('users/', views.user_list_view, name='users'),

    path('reports/', views.reports_view, name='reports'),
    path('logout/', views.logout_view, name='logout'),  # ✅ أضفنا الفاصلة هنا
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
