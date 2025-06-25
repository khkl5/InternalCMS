from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # لوحة الإدارة
    path('admin/', admin.site.urls),

    # روابط التطبيقات
    path('', include('core.urls')),          # الصفحة الرئيسية = dashboard
    path('content/', include('content.urls')),
    path('tasks/', include('tasks.urls')),
    path('clients/', include('clients.urls')),

    # لو عندك api:
    # path('api/', include('content.api_urls')),
]
