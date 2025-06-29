# core/supabase_utils.py
import uuid
import requests
from django.conf import settings

def upload_to_supabase(file_obj, original_filename):
    file_ext = original_filename.split('.')[-1]
    unique_filename = f"task_{uuid.uuid4()}.{file_ext}"
    path_in_bucket = f"task_files/{unique_filename}"

    SUPABASE_BUCKET = "media"
    SUPABASE_PROJECT_URL = settings.SUPABASE_URL.replace("https://", "")
    SUPABASE_STORAGE_URL = f"https://eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwamZ2bWdhZXdlb2p3bWVka2lsIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MDc3MzQ3NywiZXhwIjoyMDY2MzQ5NDc3fQ.URc11ePF2BtaqJ0cpmNzep5OaUWRxNr-f9fQHYFGShk/storage/v1/object"
    SUPABASE_SERVICE_KEY = settings.SUPABASE_SERVICE_KEY

    upload_url = f"{SUPABASE_STORAGE_URL}/{SUPABASE_BUCKET}/{path_in_bucket}"

    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": file_obj.content_type,
        "x-upsert": "true",
    }

    response = requests.post(
        upload_url,
        data=file_obj.read(),
        headers=headers,
    )

    if response.status_code == 200:
        public_url = f"https://{SUPABASE_PROJECT_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{path_in_bucket}"
        return public_url, path_in_bucket
    else:
        raise Exception(f"رفع الملف فشل: {response.status_code} - {response.text}")