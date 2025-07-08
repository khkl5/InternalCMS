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
from .utils import slugify_filename  # تأكد أنه موجود
import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Document


logger = logging.getLogger(__name__)


# عرض قائمة المستندات

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Document
from supabase import create_client
import logging

logger = logging.getLogger(__name__)

supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# عرض قائمة المستندات مع دعم الصلاحيات
@login_required
def document_list_view(request):
    user = request.user
    role = getattr(user.userprofile.role, 'name', None)

    # جلب كل المستندات التي يحق للمستخدم رؤيتها (باستخدام دالة can_view)
    all_documents = Document.objects.all()
    documents = [doc for doc in all_documents if doc.can_view(user)]

    # دعم البحث
    query = request.GET.get('q', '')
    if query:
        documents = [doc for doc in documents if query.lower() in doc.title.lower()]

    # تجهيز خصائص العرض/التحميل (كما كان في الكود الأصلي)
    for doc in documents:
        doc.can_download = doc.can_view(user)
        doc.can_delete = doc.can_delete(user)
        if doc.file_url:
            extension = doc.file_url.lower().split('.')[-1]
            doc.is_image = extension in ['jpg', 'jpeg', 'png', 'gif']
            doc.is_pdf = extension == 'pdf'
        else:
            doc.is_image = False
            doc.is_pdf = False

    return render(request, 'content/document_list.html', {
        'documents': documents,
        'role': role,
        'is_admin': role == 'admin',
        'query': query,
    })

# حذف مستند (مراعاة صلاحية الحذف)
@login_required
def delete_document_view(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    user = request.user

    # التحقق من صلاحية الحذف
    if not document.can_delete(user):
        return render(request, '403.html', status=403)

    try:
        # حذف الملف من supabase إذا وجد
        if document.file_path:
            delete_response = supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET).remove([document.file_path])
            if hasattr(delete_response, "error") and delete_response.error:
                logger.error("فشل حذف الملف من Supabase: %s", delete_response.error)
        document.delete()
        messages.success(request, 'تم حذف المستند بنجاح.')

    except Exception as e:
        logger.exception("خطأ أثناء حذف المستند: %s", e)
        messages.error(request, 'حدث خطأ أثناء الحذف.')

    return redirect('document_list')

@login_required
def upload_document_view(request):
    role = getattr(request.user.userprofile.role, 'name', None)

    # السماح فقط للمدير أو الموظف
    if role not in ['admin', 'staff']:
        return render(request, '403.html', status=403)

    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                file = request.FILES['file']
                safe_filename = slugify_filename(file.name)
                bucket_path = f"uploads/documents/{safe_filename}"
                file_bytes = file.read()

                # رفع الملف إلى supabase
                upload_response = supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET).upload(
                    path=bucket_path,
                    file=file_bytes,
                    file_options={"contentType": file.content_type}
                )

                if hasattr(upload_response, "error") and upload_response.error:
                    messages.error(request, "فشل رفع الملف إلى Supabase.")
                    logger.error("Upload error: %s", upload_response["error"])
                    return redirect('upload_document')

                # توليد رابط تحميل موقّع
                signed_url_response = supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET).create_signed_url(
                    path=bucket_path,
                    expires_in=86400  # 24 ساعة
                )

                signed_url = signed_url_response.get('signedURL')
                if not signed_url:
                    messages.error(request, "فشل إنشاء رابط التحميل.")
                    logger.error("Signed URL error: %s", signed_url_response)
                    return redirect('upload_document')

                # حفظ المستند
                document = form.save(commit=False)
                document.uploaded_by = request.user
                document.file_path = bucket_path
                document.file_url = signed_url

                # تحقق يدوي من العنوان (إجراء احتياطي)
                if not document.title:
                    messages.error(request, "العنوان مفقود.")
                    return redirect('upload_document')

                document.save()
                form.save_m2m()

                logger.info("تم حفظ المستند: %s", document)
                messages.success(request, "تم رفع المستند بنجاح.")
                return redirect('document_list')

            except Exception as e:
                logger.exception("خطأ أثناء رفع المستند: %s", e)
                messages.error(request, "حدث خطأ أثناء رفع المستند. يرجى المحاولة لاحقًا.")

        else:
            logger.warning("❌ أخطاء النموذج: %s", form.errors)
            messages.warning(request, "الرجاء التأكد من تعبئة جميع الحقول بشكل صحيح.")
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

