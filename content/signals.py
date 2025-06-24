from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Document
from supabase import create_client, Client
from django.conf import settings

_supabase_client = None

def get_supabase_client():
    global _supabase_client
    if _supabase_client is None:
        SUPABASE_URL = settings.SUPABASE_URL
        SUPABASE_KEY = settings.SUPABASE_SERVICE_KEY
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in settings.")
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client

@receiver(post_delete, sender=Document)
def delete_file_from_supabase(sender, instance, **kwargs):
    bucket_name = settings.SUPABASE_STORAGE_BUCKET
    file_path = instance.file_path
    
    if not file_path:
        print(f"⚠️ [Supabase Delete] لا يوجد file_path للمستند '{instance}'. تخطيت الحذف.")
        return
    
    try:
        supabase = get_supabase_client()
        response = supabase.storage.from_(bucket_name).remove([file_path])
        
        print(f"✅ [Supabase Delete] الملف '{file_path}' تم حذفه من الباكت '{bucket_name}'. Response:", response)
    
    except Exception as e:
        print(f"❌ [Supabase Delete] خطأ أثناء محاولة حذف الملف '{file_path}':", e)
