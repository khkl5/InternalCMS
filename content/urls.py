from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DocumentViewSet,
    document_list_view,
    delete_document_view,
    upload_document_view,
)


router = DefaultRouter()
router.register(r'documents-api', DocumentViewSet, basename='document')

urlpatterns = [
    # HTML views
    path('documents/', document_list_view, name='document_list'),
    path('documents/upload/', upload_document_view, name='upload_document'),
    path('documents/delete/<int:document_id>/', delete_document_view, name='delete_document'),

    # DRF API views
    path('', include(router.urls)),
]
