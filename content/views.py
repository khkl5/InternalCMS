import logging
from pathlib import Path

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from rest_framework import permissions, viewsets

from core.decorators import get_user_role
from utils.supabase_client import create_signed_file_url, delete_file, upload_file

from .forms import DocumentUploadForm
from .models import Document
from .permissions import visible_documents_for
from .serializers import DocumentSerializer
from .utils import slugify_filename

logger = logging.getLogger(__name__)


def _attach_document_download_url(document):
    document.file_url = create_signed_file_url(document.file_path) if document.file_path else ""
    extension = Path(document.file_path or "").suffix.lower()
    document.is_image = extension in {".jpg", ".jpeg", ".png", ".gif"}
    document.is_pdf = extension == ".pdf"


@login_required
def document_list_view(request):
    role = get_user_role(request.user)
    documents = visible_documents_for(request.user).select_related("client", "uploaded_by")
    query = request.GET.get("q", "").strip()
    if query:
        documents = documents.filter(title__icontains=query)

    documents = list(documents)
    for document in documents:
        try:
            _attach_document_download_url(document)
        except Exception:
            logger.exception("Failed to create a signed URL for document %s", document.pk)
            document.file_url = ""
        document.can_download = document.can_view(request.user)
        document.can_delete = document.can_delete(request.user)

    return render(
        request,
        "content/document_list.html",
        {
            "documents": documents,
            "role": role,
            "is_admin": role == "admin",
            "query": query,
        },
    )


@require_POST
@login_required
def delete_document_view(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    if not document.can_delete(request.user):
        return JsonResponse(
            {"success": False, "error": "غير مصرح لك بحذف هذا المستند"},
            status=403,
        )

    document.delete()
    return JsonResponse({"success": True})


@login_required
def upload_document_view(request):
    role = get_user_role(request.user)
    if role not in {"admin", "staff"}:
        return render(request, "403.html", status=403)

    form = DocumentUploadForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        bucket_path = ""
        try:
            uploaded_file = request.FILES["file"]
            bucket_path = f"uploads/documents/{slugify_filename(uploaded_file.name)}"
            upload_file(uploaded_file, bucket_path)

            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.file_path = bucket_path
            document.save()
            form.save_m2m()
        except Exception:
            logger.exception("Failed to upload a document")
            if bucket_path:
                try:
                    delete_file(bucket_path)
                except Exception:
                    logger.exception("Failed to clean up an incomplete document upload")
            messages.error(request, "تعذر رفع المستند. يرجى المحاولة لاحقًا.")
        else:
            messages.success(request, "تم رفع المستند بنجاح.")
            return redirect("document_list")

    return render(request, "content/upload_document.html", {"form": form})


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return visible_documents_for(self.request.user).select_related("uploaded_by", "client")
