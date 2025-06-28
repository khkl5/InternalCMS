from rest_framework import viewsets, permissions
from .models import Document
from .serializers import DocumentSerializer

class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        role = getattr(user.userprofile.role, 'name', None)

        if role == 'admin':
            return Document.objects.all()

        if role == 'staff':
            return Document.objects.filter(uploaded_by=user)

        # افتراضيًا للمشاهدين وغيرهم
        return Document.objects.filter(access_level__in=['public', 'restricted'])
