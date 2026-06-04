import logging

from django import forms
from django.contrib import admin

from core.file_validation import validate_uploaded_file
from utils.supabase_client import delete_file, upload_file

from .models import Document
from .utils import slugify_filename

logger = logging.getLogger(__name__)


class DocumentAdminForm(forms.ModelForm):
    upload_file = forms.FileField(
        required=False,
        label="رفع ملف",
        validators=[validate_uploaded_file],
    )

    class Meta:
        model = Document
        fields = "__all__"


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    form = DocumentAdminForm
    list_display = ("title", "uploaded_by", "client", "access_level", "created_at")
    list_display_links = ("title",)
    search_fields = ("title", "uploaded_by__username")
    list_filter = ("access_level", "created_at", "uploaded_by")
    ordering = ("-created_at",)

    def save_model(self, request, obj, form, change):
        uploaded_file = form.cleaned_data.get("upload_file")
        old_path = ""
        if change:
            old_path = (
                Document.objects.filter(pk=obj.pk).values_list("file_path", flat=True).first()
                or ""
            )

        if uploaded_file:
            new_path = f"uploads/documents/{slugify_filename(uploaded_file.name)}"
            upload_file(uploaded_file, new_path)
            obj.file_path = new_path
        if not obj.uploaded_by_id:
            obj.uploaded_by = request.user

        super().save_model(request, obj, form, change)

        if uploaded_file and old_path and old_path != obj.file_path:
            try:
                delete_file(old_path)
            except Exception:
                logger.exception("Failed to delete replaced admin upload %s", old_path)
