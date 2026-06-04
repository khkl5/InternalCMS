from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include


def health_check(_request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path('health/', health_check, name='health_check'),
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('content/', include('content.urls')),
    path('tasks/', include('tasks.urls')),
    path('clients/', include('clients.urls')),
]
