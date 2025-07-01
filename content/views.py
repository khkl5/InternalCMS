from rest_framework import viewsets, permissions
from .models import Document
from .serializers import DocumentSerializer
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from supabase import create_client
import uuid, unicodedata, re
from .forms import DocumentUploadForm
from django.conf import settings



# عرض قائمة المستندات
@login_required
def document_list_view(request):
    role = getattr(request.user.userprofile.role, 'name', None)

    if role == 'admin':
        documents = Document.objects.all()
    elif role == 'staff':
        documents = Document.objects.filter(uploaded_by=request.user)
    else:
        documents = Document.objects.filter(access_level__in=['public', 'restricted'])

    query = request.GET.get('q')
    if query:
        documents = documents.filter(title__icontains=query)

    return render(request, 'content/document_list.html', {
        'documents': documents,
        'role': role,
        'query': query or '',
    })


# حذف مستند (للمشرف فقط)
@login_required
def delete_document_view(request, document_id):
    role = getattr(request.user.userprofile.role, 'name', None)

    if role != 'admin':
        return render(request, '403.html', status=403)

    document = get_object_or_404(Document, id=document_id)
    document.delete()
    messages.success(request, 'تم حذف المستند بنجاح.')
    return redirect('document_list')


# دالة رفع مستند (للواجهة - للموظف فقط)
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def slugify_filename(filename):
    name, ext = filename.rsplit('.', 1)
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    name = re.sub(r'[^a-zA-Z0-9_-]+', '-', name).strip('-')
    unique_suffix = uuid.uuid4().hex[:8]
    return f"{name}-{unique_suffix}.{ext}"

@login_required
def upload_document_view(request):
    role = getattr(request.user.userprofile.role, 'name', None)

    if role != 'staff':
        return render(request, '403.html', status=403)

    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            safe_filename = slugify_filename(file.name)
            bucket_path = f"uploads/documents/{safe_filename}"
            file_bytes = file.read()

            supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET).upload(
                path=bucket_path,
                file=file_bytes,
                file_options={"contentType": file.content_type}
            )

            signed_url = supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET).create_signed_url(
                path=bucket_path,
                expires_in=86400
            ).get('signedURL')

            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.file_path = bucket_path
            document.file_url = signed_url
            document.save()

            messages.success(request, "تم رفع المستند بنجاح.")
            return redirect('document_list')
    else:
        form = DocumentUploadForm()

    return render(request, 'content/upload_document.html', {'form': form})
# API ViewSet
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
        return Document.objects.filter(access_level__in=['public', 'restricted'])

