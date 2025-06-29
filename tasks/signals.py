from django.db.models.signals import post_delete
from django.dispatch import receiver
from tasks.models import Task
from django.conf import settings
import requests

@receiver(post_delete, sender=Task)
def delete_task_file_from_supabase(sender, instance, **kwargs):
    file_path = instance.file_path
    if not file_path:
        print(f"⚠️ [Supabase Delete] لا يوجد file_path للمهمة. تم تجاهل الحذف.")
        return

    try:
        bucket = settings.SUPABASE_STORAGE_BUCKET
        project_url = settings.SUPABASE_URL.replace("https://", "")
        service_key = settings.SUPABASE_SERVICE_KEY

        delete_url = f"https://{project_url}/storage/v1/object/{bucket}/{file_path}"
        headers = {
            "Authorization": f"Bearer {service_key}"
        }

        response = requests.delete(delete_url, headers=headers)

        if response.status_code in [200, 204]:
            print(f"✅ [Supabase] تم حذف ملف المهمة: {file_path}")
        else:
            print(f"❌ [Supabase] فشل الحذف. الكود: {response.status_code}, الرسالة: {response.text}")
    except Exception as e:
        print(f"❌ [Supabase] خطأ أثناء حذف الملف:", e)
