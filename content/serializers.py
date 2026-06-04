import logging

from rest_framework import serializers

from utils.supabase_client import create_signed_file_url

from .models import Document

logger = logging.getLogger(__name__)


class DocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ["id", "title", "file_url", "uploaded_by", "client", "access_level", "created_at"]

    def get_file_url(self, obj):
        try:
            return create_signed_file_url(obj.file_path)
        except Exception:
            logger.exception("Failed to create a signed URL for document %s", obj.pk)
            return ""
