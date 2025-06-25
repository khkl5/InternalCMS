from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),  # ← الصفحة الرئيسية = dashboard
    path('login/', views.login_view, name='login'),
    path('profile/', views.profile_view, name='profile'),
    path('reports/', views.reports_view, name='reports'),
]
