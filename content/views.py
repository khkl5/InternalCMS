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

@login_required
def document_list_view(request):
    user = request.user
    role = getattr(user.userprofile.role, 'name', None)

    # جلب المستندات حسب الدور
    if role == 'admin':
        documents = Document.objects.all()
    elif role == 'staff':
        documents = Document.objects.filter(uploaded_by=user)
    else:
        documents = Document.objects.filter(access_level__in=['public', 'restricted'])

    # دعم البحث
    query = request.GET.get('q', '')
    if query:
        documents = documents.filter(title__icontains=query)

    # تجهيز خصائص العرض/التحميل
    for doc in documents:
        doc.can_download = (
            role == 'admin' or
            (role == 'staff' and doc.uploaded_by == user) or
            (role == 'viewer' and doc.access_level in ['public', 'restricted'])
        )
        if doc.file_url:
            extension = doc.file_url.lower().split('.')[-1]
            doc.is_image = extension in ['jpg', 'jpeg', 'png', 'gif']
            doc.is_pdf = extension == 'pdf'
        else:
            doc.is_image = False
            doc.is_pdf = False

    # إرسال جميع المتغيرات الضرورية
    return render(request, 'content/document_list.html', {
        'documents': documents,
        'role': role,
        'is_admin': role == 'admin',   # <-- أضف هذا فقط
        'query': query,
    })

# حذف مستند (للمشرف فقط)
@login_required
def delete_document_view(request, document_id):
    role = getattr(request.user.userprofile.role, 'name', None)

    if role != 'admin':
        return render(request, '403.html', status=403)

    document = get_object_or_404(Document, id=document_id)

    try:
        # حذف الملف من supabase إذا وجد
        if document.file_path:
            delete_response = supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET).remove([document.file_path])
            if hasattr(delete_response, "error") and delete_response.error:
                logger.error("فشل حذف الملف من Supabase: %s", delete_response.error)
            else:
                logger.info("تم حذف الملف من Supabase: %s", document.file_path)

        # حذف المستند من قاعدة البيانات
        document.delete()
        messages.success(request, 'تم حذف المستند بنجاح.')

    except Exception as e:
        logger.exception("خطأ أثناء حذف المستند: %s", e)
        messages.error(request, 'حدث خطأ أثناء الحذف.')

    return redirect('document_list')

# دالة رفع مستند (للواجهة - للموظف فقط)
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def slugify_filename(filename):
    name, ext = filename.rsplit('.', 1)
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    name = re.sub(r'[^a-zA-Z0-9_-]+', '-', name).strip('-')
    unique_suffix = uuid.uuid4().hex[:8]
    return f"{name}-{unique_suffix}.{ext}"

logger = logging.getLogger(__name__)  # لتسجيل الأخطاء

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

