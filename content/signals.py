from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Document
from django.conf import settings
import requests

@receiver(post_delete, sender=Document)
def delete_file_from_supabase(sender, instance, **kwargs):
    bucket_name = settings.SUPABASE_STORAGE_BUCKET
    file_path = instance.file_path

    if not file_path:
        print(f"⚠️ [Supabase Delete] لا يوجد file_path للمستند '{instance}'. تخطيت الحذف.")
        return

    try:
        project_url = settings.SUPABASE_URL.replace("https://", "")
        service_key = settings.SUPABASE_SERVICE_KEY
        delete_url = f"https://{project_url}/storage/v1/object/{bucket_name}/{file_path}"

        headers = {
            "Authorization": f"Bearer {service_key}",
        }

        response = requests.delete(delete_url, headers=headers)

        if response.status_code in [200, 204]:
            print(f"✅ [Supabase Delete] الملف '{file_path}' تم حذفه بنجاح.")
        else:
            print(f"❌ [Supabase Delete] فشل حذف الملف. الكود: {response.status_code}, الرسالة: {response.text}")

    except Exception as e:
        print(f"❌ [Supabase Delete] خطأ أثناء محاولة حذف الملف '{file_path}':", e)
