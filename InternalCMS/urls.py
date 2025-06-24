from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # روابط التطبيقات
    path('core/', include('core.urls')),
    path('content/', include('content.urls')),
    path('tasks/', include('tasks.urls')),
    path('clients/', include('clients.urls')),

    # روابط الـ API
    path('api/', include('content.urls')),

    # الصفحة الرئيسية (مؤقتاً)
    path('', lambda request: HttpResponse("🎉 أهلاً بك في InternalCMS — لوحة الإدارة"), name='home'),
]
