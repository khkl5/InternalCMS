from django.urls import path
from . import views
from .views import dashboard_view
from django.contrib.auth import views as auth_views
from core.views import staff_list_view
from .views import send_test_email

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('staff/', views.staff_list_view, name='staff_list'),
    path('staff/delete/<int:staff_id>/', views.delete_staff_view, name='delete_staff'),
    path('staff/edit/<int:user_id>/', views.edit_staff_view, name='edit_staff'),
     path('send-test-email/', send_test_email, name='send_test_email'),


    # تغيير كلمة المرور باستخدام الواجهة المخصصة
    path(
        'password_change/',
        auth_views.PasswordChangeView.as_view(template_name='core/change_password.html'),
        name='password_change'
    ),
    path(
        'password_change/done/',
        auth_views.PasswordChangeDoneView.as_view(template_name='core/change_password_done.html'),
        name='password_change_done'
    ),

    # لوحات التحكم
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),

    # صفحات عامة
    path('profile/', views.profile_view, name='profile'),
    path('reports/', views.reports_view, name='reports'),
    path('settings/', views.settings_view, name='settings'),
    path('users/', views.user_list_view, name='users'),
    path('add-user/', views.add_user_view, name='add_user'),

]
