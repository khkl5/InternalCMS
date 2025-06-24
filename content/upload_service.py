from utils.supabase_client import supabase

bucket_name = "internal-cms"  # ضعي اسم البكت اللي أنشأتِه

# مسار الملف اللي تبغين ترفعينه
file_path = "C:/Users/khklo/InternalCMS/sample_file.pdf"  # غيّريه لمسار ملف فعلي عندك

# مسار الحفظ داخل الـ bucket
bucket_file_path = "uploads/sample_file.pdf"

# قراءة الملف
with open(file_path, "rb") as f:
    file_bytes = f.read()

# رفع الملف
upload_response = supabase.storage.from_(bucket_name).upload(
    path=bucket_file_path,
    file=file_bytes
)

print("Upload Response:", upload_response)
