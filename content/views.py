from rest_framework import viewsets, permissions
from .models import Document
from .serializers import DocumentSerializer
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages


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
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Document

@login_required
def document_list_view(request):
    role = getattr(request.user.userprofile.role, 'name', None)

    if role != 'admin':
        return render(request, '403.html', status=403)

    query = request.GET.get('q')
    documents = Document.objects.all().order_by('-created_at')

    if query:
        documents = documents.filter(title__icontains=query)

    return render(request, 'content/document_list.html', {
        'documents': documents,
        'role': role,
        'query': query or '',
    })


@login_required
def delete_document_view(request, document_id):
    role = getattr(request.user.userprofile.role, 'name', None)

    if role != 'admin':
        return render(request, '403.html', status=403)

    document = get_object_or_404(Document, id=document_id)

    # حذف المستند
    document.delete()
    messages.success(request, 'تم حذف المستند بنجاح.')
    return redirect('document_list')
