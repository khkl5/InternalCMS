# utils/test_supabase.py

from utils.supabase_client import supabase

# اسم الباكت
bucket_name = "media"

# مسار الصورة في جهازك
local_file_path = "test_file.jpg"  # ضعي صورة بهذا الاسم في مجلد InternalCMS
remote_file_path = "uploads/test_file.jpg"


# تجربة: جلب أسماء الباكت
def test_connection():
    try:
        response = supabase.storage.list_buckets()
        print("✅ Buckets:", [bucket.name for bucket in response])
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {e}")


# رفع ملف
def upload_file():
    try:
        with open(local_file_path, "rb") as f:
            res = supabase.storage.from_(bucket_name).upload(remote_file_path, f)
            print("✅ File uploaded:", res)
    except Exception as e:
        print(f"❌ Upload failed: {e}")


# جلب Public URL
def get_file_url():
    try:
        url = supabase.storage.from_(bucket_name).get_public_url(remote_file_path)
        print("✅ Public URL:", url)
    except Exception as e:
        print(f"❌ Failed to get public URL: {e}")


# تشغيل
test_connection()
upload_file()
get_file_url()
