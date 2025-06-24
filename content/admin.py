from django.contrib import admin
from django import forms
from .models import Document
from utils.supabase_client import supabase
from django.conf import settings
import re
import unicodedata
import uuid

# دالة تنظيف اسم الملف
def slugify_filename(filename):
    name, ext = filename.rsplit('.', 1)
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    name = re.sub(r'[^a-zA-Z0-9_-]+', '-', name).strip('-')
    unique_suffix = uuid.uuid4().hex[:8]  # نحط جزء عشوائي للتفادي التكرار
    return f"{name}-{unique_suffix}.{ext}"

class DocumentAdminForm(forms.ModelForm):
    upload_file = forms.FileField(required=False, label='رفع ملف')

    class Meta:
        model = Document
        fields = '__all__'

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    form = DocumentAdminForm
    list_display = ('title', 'uploaded_by', 'client', 'access_level', 'created_at', 'file_url')
    list_display_links = ('title',)
    search_fields = ('title', 'uploaded_by__username')
    list_filter = ('access_level', 'created_at', 'uploaded_by')
    ordering = ('-created_at',)

    def save_model(self, request, obj, form, change):
        upload_file = form.cleaned_data.get('upload_file')

        if upload_file:
            bucket_name = settings.SUPABASE_STORAGE_BUCKET
            safe_filename = slugify_filename(upload_file.name)
            bucket_file_path = f"uploads/documents/{safe_filename}"

            # نقرأ الملف bytes
            file_bytes = upload_file.file.read()

            # رفع إلى supabase
            supabase.storage.from_(bucket_name).upload(
                path=bucket_file_path,
                file=file_bytes,
                file_options={ "contentType": upload_file.content_type }
            )

            # Signed URL لمدة يوم
            signed_url_resp = supabase.storage.from_(bucket_name).create_signed_url(
                path=bucket_file_path,
                expires_in=86400
            )

            # نخزن البيانات في الموديل
            obj.file_path = bucket_file_path
            obj.file_url = signed_url_resp.get('signedURL')

        # حفظ الموديل
        super().save_model(request, obj, form, change)
