from rest_framework import serializers
from .models import Document
from django.conf import settings

class DocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['id', 'title', 'file_url', 'uploaded_by', 'client', 'access_level', 'created_at']

    def get_file_url(self, obj):
        if obj.file_path:
            bucket_name = settings.SUPABASE_STORAGE_BUCKET  # "media"
            project_url = settings.SUPABASE_URL.replace("https://", "")
            public_url = f"https://{project_url}/storage/v1/object/public/{bucket_name}/{obj.file_path}"
            return public_url
        return ""
