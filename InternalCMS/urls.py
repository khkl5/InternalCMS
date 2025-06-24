from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # روابط التطبيقات
    path('core/', include('core.urls')),
    path('content/', include('content.urls')),
    path('tasks/', include('tasks.urls')),
    path('clients/', include('clients.urls')),

    # روابط الـ API
    path('api/', include('content.urls')),

    # الصفحة الرئيسية → تعرض home.html
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]
