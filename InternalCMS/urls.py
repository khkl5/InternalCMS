from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('content/', include('content.urls')),
    path('tasks/', include('tasks.urls')),
    path('clients/', include('clients.urls')),
]
