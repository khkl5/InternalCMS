from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, document_list_view, delete_document_view

router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')

urlpatterns = [
    # ✅ أولاً: نضيف رابط HTML (قبل include(router.urls))
    path('documents/list/', document_list_view, name='document_list'),
    path('documents/delete/<int:document_id>/', delete_document_view, name='delete_document'),


    # ✅ بعدين نضيف الـ API router
    path('', include(router.urls)),
]
