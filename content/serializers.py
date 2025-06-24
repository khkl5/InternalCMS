from rest_framework import serializers
from .models import Document
from utils.supabase_client import supabase

class DocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ['id', 'title', 'file_url', 'uploaded_by', 'client', 'access_level', 'created_at']

    def get_file_url(self, obj):
        if obj.file_path:
            bucket_name = "internal-cms"
            signed_url_resp = supabase.storage.from_(bucket_name).create_signed_url(
                path=obj.file_path,
                expires_in=3600  # 1 ساعة
            )
            return signed_url_resp.get('signedURL')
        return ""
