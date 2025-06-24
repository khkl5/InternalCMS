from rest_framework import viewsets, permissions
from .models import Document
from .serializers import DocumentSerializer

class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Document.objects.all().order_by('-created_at')
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Document.objects.all()

        # لو فيه صلاحيات... هنا فين تحددين:
        # مدير النظام يشوف الكل
        # موظف يشوف حسب client
        # قارئ فقط يشوف حسب access_level

        return Document.objects.filter(
            access_level__in=['public', 'restricted']
        )
